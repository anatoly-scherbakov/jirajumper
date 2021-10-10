import json
from typing import Any, Dict, Optional, List

import backoff
import rich
from documented import DocumentedError
from jira import JIRA, JIRAError, Issue
from typer import Argument, Context, Option

from jeeves_jira.cache import retrieve, store
from jeeves_jira.client import issue_url, jira
from jeeves_jira.models import (
    JeevesJiraContext, OutputFormat, JIRAField,
    JiraCache,
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

        j jira select PROJ-123
    """


FIELD_ALIASES = {
    'epic-link': 'epic',
    'issuetype': 'type',
    'parent-link': 'parent',
    'version': 'fixVersions',
}


def find_alias_for(field_name: str) -> str:
    return FIELD_ALIASES.get(field_name, field_name)


def issue_to_json(
    issue: Issue,
    available_fields: List[JIRAField],
) -> Dict[str, Any]:   # type: ignore
    """
    Represent a JIRA issue as a JSON serializable dict.

    Take care of field names and (by default) strip null values.
    """
    available_field_by_id = {
        field.id: field
        for field in available_fields
    }

    return {
        find_alias_for(
            available_field_by_id[field_name].canonical_name,
        ): field_value
        for field_name, field_value
        in issue.raw['fields'].items()
        if field_value is not None
    }


def prettify_fields(  # type: ignore
    cache: JiraCache,
    fields: Dict[str, Any],
):
    return {
        cache.issue_fields[field_name].cli_name: field_description
        for field_name, field_description
        in fields.items()
        if field_description is not None
    }


@backoff.on_exception(backoff.expo, JIRAError, max_time=5)
def select(
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
        store(cache)
    else:
        key = cache.selected_issue_key

        if not key:
            raise NoIssueSelected()

        issue = client.issue(cache.selected_issue_key)

    if context.obj.output_format == OutputFormat.PRETTY:
        rich.print(f'[bold]{issue.key}[/bold] {issue.fields.summary}')
        rich.print(issue_url(client.server_url, issue.key))

    else:
        print(json.dumps(
            issue_to_json(
                issue=issue,
                available_fields=cache.issue_fields,
            ),
            indent=2,
        ))

    return issue
