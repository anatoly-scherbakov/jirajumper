from dataclasses import dataclass
from typing import Dict, NewType, Any, Protocol, Union, Tuple

from jira import Issue

from jirajumper.models import (
    FieldByName, JiraValue, HumanValue,
    NotImplementedType, FieldKeyByName,
)


class ToJira(Protocol):
    """Convert a human-readable value to JIRA field."""

    def __call__(self, human_value: HumanValue) -> JiraValue:
        """Convert a human-readable value to JIRA field."""
        raise NotImplemented()


class FromJira(Protocol):
    """Convert a native JIRA field value to a human readable one."""

    def __call__(self, jira_value: JiraValue) -> HumanValue:
        """Convert a native JIRA field value to a human readable one."""
        raise NotImplemented()


def identity(x):
    """Identity function."""
    return x


@dataclass(frozen=True)
class JiraField:
    """Transformations related to a particular JIRA field."""

    jira_name: Union[str, FieldByName]
    human_name: str
    description: str

    to_jira: Union[ToJira, NotImplementedType] = identity
    from_jira: FromJira = identity

    def resolve_jira_field_name(self, field_key_by_name: FieldKeyByName) -> str:
        """Resolve JIRA field name."""
        if isinstance(self.jira_name, str):
            return self.jira_name

        if isinstance(self.jira_name, FieldByName):
            return field_key_by_name[self.jira_name.readable_name]

        raise ValueError(f'`{self.jira_name}` is not a valid JIRA field name.')

    def retrieve(self, issue: Issue, field_key_by_name: FieldKeyByName):
        """Retrieve the native field value from given issue."""
        return self.from_jira(
            getattr(
                issue.fields,
                self.resolve_jira_field_name(
                    field_key_by_name=field_key_by_name,
                ),
            ),
        )

    def store(self, human_value: HumanValue) -> Tuple[str, JiraValue]:
        """Convert the readable value into JIRA native form."""
        return self.jira_name, self.to_jira(human_value)

    def is_writable(self):
        """Find out if this field is writable."""
        return self.to_jira is not NotImplemented
