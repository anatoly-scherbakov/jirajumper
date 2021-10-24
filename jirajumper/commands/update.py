from dataclasses import dataclass
from typing import Dict

import rich
from documented import DocumentedError
from jira import JIRAError

from jirajumper.fields import JiraFieldsRepository
from jirajumper.cache.cache import JeevesJiraContext


@dataclass
class JIRAUpdateFailed(DocumentedError):
    """
    Cannot update a JIRA issue :(

    Errors
    {self.formatted_errors}
    """

    errors: Dict[str, str]
    fields: JiraFieldsRepository

    @property
    def formatted_errors(self) -> str:
        """Format the error list received from JIRA."""
        error_by_field = [
            (self.fields.find_by_jira_name(jira_name), error_message)
            for jira_name, error_message in self.errors.items()
        ]

        return '\n'.join([
            f'  - {field.human_name}\n      {error_message}'
            for field, error_message in error_by_field
        ])


def update(
    context: JeevesJiraContext,
    **kwargs: str,
):
    """
    Update the selected JIRA issue.

    Use `jj jump` to select the issue to update.
    """
    fields_and_values = [
        (field, kwargs[field.human_name])
        for field in context.obj.fields
        if kwargs.get(field.human_name)
    ]

    rich.print('Updating:')
    for field, human_value in fields_and_values:
        rich.print(f'  - {field.human_name} ≔ {human_value}')

    issue_fields = dict([
        field.store(human_value)
        for field, human_value in fields_and_values
    ])

    try:
        context.obj.current_issue.update(issue_fields)
    except JIRAError as err:
        raise JIRAUpdateFailed(
            errors=err.response.json().get('errors', {}),
            fields=context.obj.fields,
        ) from err

    rich.print('Updated!')
