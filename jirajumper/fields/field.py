import operator
import re
from dataclasses import asdict, dataclass
from typing import Optional, Protocol, Tuple, TypeVar, Union

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


class ToJQL(Protocol):
    """Construct a JQL expression from a raw argument value."""

    def __call__(self, expression: str) -> str:
        """Construct a JQL expression from a raw argument value."""
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

    is_mutable: bool = True

    jql_name: Optional[str] = None
    to_jira: Union[ToJira, NotImplementedType] = identity
    from_jira: FromJira = identity

    def retrieve(self, issue: Issue):
        """Retrieve the native field value from given issue."""
        return self.from_jira(
            operator.attrgetter(self.jira_name)(issue.fields),
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
            unresolved_name = self.jira_name
            resolved_name = self.jira_name

        elif isinstance(self.jira_name, FieldByName):
            unresolved_name = self.jira_name.readable_name
            resolved_name = field_key_by_name[unresolved_name]

        else:
            raise ValueError(
                f'`{self.jira_name}` is not a valid JIRA field name.',
            )

        field_dict = {
            **asdict(self),
            **{
                'unresolved_jira_name': unresolved_name,
                'jira_name': resolved_name,
            },
        }

        return ResolvedField(**field_dict)


def _jql_operator(is_multiple: bool, is_positive: bool) -> str:
    return {
        False: {
            False: '!=',
            True: '=',
        },
        True: {
            False: 'NOT IN',
            True: 'IN',
        },
    }[is_multiple][is_positive]


@dataclass(frozen=True)
class ResolvedField(JiraField):
    """JIRA field description with resolved field name."""

    unresolved_jira_name: Optional[str] = None

    def to_jql(self, expression: str) -> str:   # noqa: WPS210
        """Convert human readable expression to JQL."""
        minus, pattern = re.match('(-*)(.+)', expression).groups()
        is_positive = not minus

        search_values = list(map(
            str.strip,
            pattern.split(','),
        ))
        is_multiple = len(search_values) > 1

        jql_operator = _jql_operator(
            is_multiple=is_multiple,
            is_positive=is_positive,
        )

        jql_values = ', '.join(
            f'"{search_value}"'
            for search_value in search_values
        )

        if is_multiple:
            jql_values = f'({jql_values})'

        field_name = self.jql_name or self.unresolved_jira_name
        if ' ' in field_name:
            field_name = f'"{field_name}"'

        return f'{field_name} {jql_operator} {jql_values}'
