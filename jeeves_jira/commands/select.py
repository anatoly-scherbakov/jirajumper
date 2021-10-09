from typing import Optional

import backoff
import rich
from documented import DocumentedError
from jira import JIRA, JIRAError
from typer import Argument, Option

from jeeves_jira.cache import retrieve, store
from jeeves_jira.client import issue_url, jira


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
    No issue has been selected!

    To select an issue PROJ-123, please run:

        j jira select PROJ-123
    """


@backoff.on_exception(backoff.expo, JIRAError, max_time=5)
def select(
    verbose: bool = Option(False, '-v'),
    specifier: Optional[str] = Argument(None),
):
    """Select a Jira issue to work with."""
    cache = retrieve()
    client = jira()

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

    rich.print(f'[bold]{issue.key}[/bold] {issue.fields.summary}')

    rich.print(issue_url(client.server_url, issue.key))

    if verbose:
        rich.print(issue.raw['fields'])

    return issue
