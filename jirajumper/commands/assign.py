import rich
from typer import Argument

from jirajumper.cache.cache import JeevesJiraContext


def assign(
    context: JeevesJiraContext,
    assignee: str = Argument(
        ...,
        help='Assignee display name or email address. Supports fuzzy search.',
    ),
):
    """Assign the selected JIRA issue to a person."""
    key = context.obj.current_issue.key

    rich.print(f'Assigning {key} to {assignee}...')
    context.obj.jira.assign_issue(
        issue=key,
        assignee=assignee,
    )

    rich.print('Assigned!')
