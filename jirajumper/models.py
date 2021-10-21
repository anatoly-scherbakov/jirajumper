import re
from enum import Enum
from functools import cached_property
from typing import List, Optional

import stringcase
from jira import JIRA
from pydantic import BaseModel, Field
from typer import Context


class OutputFormat(str, Enum):
    """Output format."""

    PRETTY = 'pretty'
    JSON = 'json'


class IssueFieldSchema(BaseModel):
    """JIRA issue field schema."""

    field_type: str = Field(alias='type')
    system: Optional[str] = None


class JIRAField(BaseModel):
    """Description of a JIRA issue field."""

    id: str
    key: str
    name: str
    custom: bool
    orderable: bool
    navigable: bool
    searchable: bool
    clause_names: List[str] = Field(alias='clauseNames')
    field_schema: Optional[IssueFieldSchema] = Field(None, alias='schema')

    @property
    def canonical_name(self):
        """
        Generate canonical name of the field.

        That name will be used to render field names in CLI.
        """
        if not self.custom:
            return self.id

        name = self.name.strip()
        name = re.sub(r'[\[\]]', '', name)

        name = stringcase.spinalcase(name)

        name = name.strip('-')
        name = name.replace('--', '-')

        return name


class JiraCache(BaseModel):
    """Cached JIRA configuration."""

    selected_issue_key: Optional[str] = None
    issue_fields: List[JIRAField] = Field(default_factory=list)


class GlobalOptions(BaseModel):
    """Global jeeves-jira configuration options."""

    output_format: OutputFormat
    jira: JIRA
    cache: JiraCache

    class Config:
        """Allow the use of JIRA instance."""

        arbitrary_types_allowed = True


class JeevesJiraContext(Context):
    """Typer context with GlobalOptions instance as obj."""

    obj: GlobalOptions
