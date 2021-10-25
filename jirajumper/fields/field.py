from dataclasses import asdict, dataclass
from typing import Protocol, Tuple, TypeVar, Union

from jira import Issue

from jirajumper.models import (
    FieldByName,
    FieldKeyByName,
    HumanValue,
    JiraValue,
    NotImplementedType,
)

AnyType = TypeVar('AnyType')


class ToJira(Protocol):
    """Convert a human-readable value to JIRA field."""

    def __call__(self, human_value: HumanValue) -> JiraValue:
        """Convert a human-readable value to JIRA field."""
        raise NotImplementedError()


class FromJira(Protocol):
    """Convert a native JIRA field value to a human readable one."""

    def __call__(self, jira_value: JiraValue) -> HumanValue:
        """Convert a native JIRA field value to a human readable one."""
        raise NotImplementedError()


def identity(any_value: AnyType) -> AnyType:
    """Identity function."""
    return any_value


@dataclass(frozen=True)
class JiraField:
    """Transformations related to a particular JIRA field."""

    jira_name: Union[str, FieldByName]
    human_name: str
    description: str

    to_jira: Union[ToJira, NotImplementedType] = identity
    from_jira: FromJira = identity

    def retrieve(self, issue: Issue):
        """Retrieve the native field value from given issue."""
        return self.from_jira(
            getattr(
                issue.fields,
                self.jira_name,
            ),
        )

    def store(self, human_value: HumanValue) -> Tuple[str, JiraValue]:
        """Convert the readable value into JIRA native form."""
        return self.jira_name, self.to_jira(human_value)

    def is_writable(self):
        """Find out if this field is writable."""
        return self.to_jira is not NotImplemented

    def resolve(self, field_key_by_name: FieldKeyByName) -> 'ResolvedField':
        """Resolve jira_name."""
        if isinstance(self.jira_name, str):
            jira_name = self.jira_name

        elif isinstance(self.jira_name, FieldByName):
            jira_name = field_key_by_name[self.jira_name.readable_name]

        else:
            raise ValueError(
                f'`{self.jira_name}` is not a valid JIRA field name.',
            )

        field_dict = {
            **asdict(self),
            **{
                'jira_name': jira_name,
            },
        }

        return ResolvedField(**field_dict)


@dataclass(frozen=True)
class ResolvedField(JiraField):
    """JIRA field description with resolved field name."""
