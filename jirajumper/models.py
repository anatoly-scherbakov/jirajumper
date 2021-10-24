from enum import Enum
from typing import Optional, NamedTuple, NewType, Dict, Any

from pydantic import BaseModel


FieldKeyByName = Dict[str, str]
JiraValue = NewType('JiraValue', Any)
HumanValue = NewType('HumanValue', Any)
NotImplementedType = type(NotImplemented)


class OutputFormat(str, Enum):
    """Output format."""

    PRETTY = 'pretty'
    JSON = 'json'


class Fields(BaseModel):
    """Supported base fields."""

    summary: Optional[str] = None
    issue_type: Optional[str] = None
    version: Optional[str] = None
    project: Optional[str] = None
    epic_name: Optional[str] = None
    epic_link: Optional[str] = None
    assignee: Optional[str] = None


class CloneIssue(Fields):
    """Fields to clone an issue."""

    summary: str


class RetrieveIssue(CloneIssue):
    """Retrieved issue."""

    summary: str


class FieldByName(NamedTuple):
    """Find a field by its user-facing JIRA name."""

    readable_name: str
