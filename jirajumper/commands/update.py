from dataclasses import dataclass
from typing import Dict, Optional

import rich
from documented import DocumentedError
from jira import JIRA, JIRAError

from jirajumper import default_options
from jirajumper.cache.cache import JeevesJiraContext
from jirajumper.fields import JiraFieldsRepository


@dataclass
class JIRAUpdateFailed(DocumentedError):
    """
    Cannot update a JIRA issue 🙁.

    Errors:
    {self.formatted_errors}
    """

    errors: Dict[str, str]
    fields: JiraFieldsRepository

    @property
    def formatted_errors(self) -> str:
        """Format the error list received from JIRA."""
        field_per_resolved_jira_name = {
            field.jira_name: field
            for field in self.fields
        }

        error_by_field = [
            (field_per_resolved_jira_name[jira_name], error_message)
            for jira_name, error_message in self.errors.items()
        ]

        return '\n'.join([
            f'  - {field.human_name}\n      {error_message}'
            for field, error_message in error_by_field
        ])


def assign(jira: JIRA, key: str, assignee: str):
    """Assign issue to a person."""
    rich.print(f'Assigning {key} to {assignee}...')
    jira.assign_issue(
        issue=key,
        assignee=assignee,
    )

    rich.print('Assigned!')


def update(
    context: JeevesJiraContext,
    assignee: Optional[str] = default_options.ASSIGNEE,
    **options: str,
):
    """
    Update the selected JIRA issue.

    Use `jj jump` to select the issue to update.
    """
    fields_and_values = context.obj.fields.match_options(options)

    rich.print('Updating:')
    for print_field, human_value in fields_and_values:
        rich.print(f'  - {print_field.human_name} ≔ {human_value}')

    issue_fields = dict([
        store_field.store(human_value=human_value)
        for store_field, human_value in fields_and_values
    ])

    try:
        context.obj.current_issue.update(issue_fields)
    except JIRAError as err:
        raise JIRAUpdateFailed(
            errors=err.response.json().get('errors', {}),
            fields=context.obj.fields,
        ) from err

    if assignee is not None:
        assign(
            jira=context.obj.jira,
            key=context.obj.current_issue.key,
            assignee=assignee,
        )

    rich.print('Updated!')
