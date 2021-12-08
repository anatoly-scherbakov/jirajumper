from dataclasses import dataclass
from typing import Optional, List

import rich
from documented import DocumentedError
from more_itertools import first
from typer import Argument

from jirajumper.cache.cache import JeevesJiraContext


@dataclass
class NoTransitionFound(DocumentedError):
    """
    No transition found!

        - Source: {self.source_status}
        - Destination: {self.destination_status}

    Transitive transitions are not yet supported ☹
    """

    source_status: str
    destination_status: str


def status(
    context: JeevesJiraContext,
    status_values: Optional[List[str]] = Argument(None),
):
    """Get or set issue status."""
    issue = context.obj.current_issue
    jira = context.obj.jira

    if status_values is None:
        rich.print(issue.fields.status)
        return

    for status in status_values:
        transitions = jira.transitions(issue=issue.key)

        suitable_transitions = [
            transition['name']
            for transition in transitions
            if transition['to']['name'].lower() == status.lower()
        ]

        try:
            target_transition = first(suitable_transitions)
        except ValueError as err:
            raise NoTransitionFound(
                source_status=issue.fields.status.name,
                destination_status=status,
            ) from err

        jira.transition_issue(
            issue=issue.key,
            transition=target_transition,
        )
        rich.print(f'✔️ Status is now [bold]{status}[/bold].')
