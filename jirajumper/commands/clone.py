from typing import Optional

import rich
from typer import Option

from jirajumper.models import CloneIssue
from jirajumper.cache.cache import JeevesJiraContext


def clone(
    context: JeevesJiraContext,

    summary: str,
    epic_link: Optional[str] = Option(None, '--epic'),
    issue_type: Optional[str] = Option(None, '--type'),
    version: Optional[str] = None,
    project: Optional[str] = None,
    stay: bool = Option(
        False,
        help=(
            'Stay on current issue instead of switching '
            'to the newly created one'
        ),
    ),
    epic_name: Optional[str] = None,
    assignee: Optional[str] = None,
    status: Optional[str] = None,
):
    """Clone a JIRA issue."""
    fields = CloneIssue(
        summary=summary,
        issue_type=issue_type,
        version=version,
        project=project,
        epic_link=epic_link,
        epic_name=epic_name,
        assignee=assignee,
    )

    client = context.obj.jira
    cache = context.obj.cache

    parent_issue = client.issue(cache.selected_issue_key)

    if assignee:
        assignee_account_id = find_account_id_by_user_name(
            client=client,
            user_name=assignee,
        )

    elif parent_assignee := parent_issue.fields.assignee:
        assignee_account_id = parent_assignee.accountId

    else:
        assignee_account_id = None

    if parent_issue.fields.issuetype.name == 'Epic':
        if not epic_name:
            raise ValueError(
                'You are cloning an epic. Please specify --epic-name.',
            )

    project = project or parent_issue.fields.project.key

    description = parent_issue.fields.description

    status = parent_issue.fields.status.name
    epic = getattr(
        parent_issue.fields,
        epic_link_field,
    )
    parent = getattr(parent_issue.fields, 'parent', None)
    if parent and parent.fields.issuetype.name != 'Epic':
        parent_link = {
            'key': parent.key,
        }
    else:
        parent_link = None

    if not version and parent_issue.fields.fixVersions:
        version = parent_issue.fields.fixVersions[0].name

    if not version:
        raise ValueError(
            'No version specified in parent issue properties or '
            'in command line options.',
        )

    fields = {
        'parent': parent_link,
    }

    fields = dict(_prepare_fields(
        description=description,
        project=project,
        summary=summary,
        version=version,
        issue_type=issue_type or parent_issue.fields.issuetype.name,

        epic=epic,
        epic_name=epic_name,
        assignee_account_id=assignee_account_id,
    ))

    issue = client.create_issue(
        fields=fields,
    )

    if (
        issue.fields.status.name != status
        and parent_issue.fields.status.statusCategory.name != 'Done'
    ):
        transition_ids = [
            t['id'] for t in
            client.transitions(issue)
            if t['to']['name'] == status
        ]

        transition_id = first(transition_ids, None)

        if transition_id is None:
            rich.print(
                f'[orange]Warning:[/orange] Cannot transfer {issue} to status '
                f'[bold]{status}[/bold] because no direct transition found.',
            )

        else:
            client.transition_issue(issue, transition_id)

    if not stay:
        select(verbose=False, specifier=issue.key)

    else:
        rich.print(
            f'New issue: [bold]{issue.key}[/bold] {issue.fields.summary}')
        rich.print('  {}'.format(issue_url(client.server_url, issue.key)))
        rich.print(
            f'Selected issue: [bold]{parent_issue.key}[/bold] '
            f'{parent_issue.fields.summary}',
        )

    return issue

