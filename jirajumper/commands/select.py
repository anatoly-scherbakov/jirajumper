import json
from typing import Optional

import backoff
import rich
from documented import DocumentedError
from jira import JIRA, JIRAError
from typer import Argument

from jirajumper.cache.cache import JeevesJiraContext, JiraCache
from jirajumper.client import issue_url
from jirajumper.models import (
    OutputFormat,
)


def normalize_issue_specifier(
    client: JIRA,
    specifier: str,
    current_issue_key: Optional[str],
):
    """Normalize issue specifier."""
    if specifier.isnumeric() and current_issue_key:
        project_key, _current_issue_number = current_issue_key.split('-')
        return f'{project_key}-{specifier}'

    if specifier.lower() == 'next':
        current_issue = client.issue(current_issue_key)
        links = current_issue.fields.issuelinks

        if not links:
            raise ValueError(
                f'Issue {current_issue_key} does not have any issues it blocks.',
            )

        for link in links:
            try:
                outward_issue = link.outwardIssue
            except AttributeError:
                continue

            if (
                link.type.name == 'Blocks' and
                outward_issue.fields.status.statusCategory.name != 'Done'
            ):
                return outward_issue.key

        raise ValueError(
            f'Cannot find an issue that follows {current_issue_key} :(',
        )

    return specifier


class NoIssueSelected(DocumentedError):
    """
    No issue has been selected.

    To select an issue PROJ-123, please run:

        jj jump PROJ-123
    """


@backoff.on_exception(backoff.expo, JIRAError, max_time=5)
def jump(
    context: JeevesJiraContext,
    specifier: Optional[str] = Argument(None),
):
    """Select a Jira issue to work with."""
    client = context.obj.jira
    cache = context.obj.cache

    if specifier:
        specifier = normalize_issue_specifier(
            client=client,
            specifier=specifier,
            current_issue_key=cache.selected_issue_key,
        )

        issue = client.issue(specifier)
        cache.selected_issue_key = issue.key

        context.obj.store_cache(
            JiraCache(
                selected_issue_key=issue.key,
            ),
        )
    else:
        key = cache.selected_issue_key

        if not key:
            raise NoIssueSelected()

        issue = client.issue(cache.selected_issue_key)

    if context.obj.output_format == OutputFormat.PRETTY:
        rich.print(f'[bold]{issue.key}[/bold] {issue.fields.summary}')
        rich.print(issue_url(client.server_url, issue.key))

        for field in context.obj.fields:
            field_value = field.retrieve(
                issue=issue,
                field_key_by_name=context.obj.field_key_by_name,
            )
            rich.print(f'  - {field.human_name}: {field_value}')

    else:
        print(
            json.dumps(
                {
                    field.human_name: field.retrieve(
                        issue=issue,
                        field_key_by_name=context.obj.field_key_by_name,
                    )
                    for field in context.obj.fields
                },
                indent=2,
            ),
        )

    return issue
