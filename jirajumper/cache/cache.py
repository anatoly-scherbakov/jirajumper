import re
from dataclasses import dataclass
from functools import cached_property
from typing import Optional, List

import stringcase
from jira import JIRA, Issue
from pydantic import BaseModel, Field
from typer import Context

from jirajumper.fields import JiraFieldsRepository
from jirajumper.fields.field import FieldKeyByName
from jirajumper.models import OutputFormat


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


@dataclass
class GlobalOptions:
    """Global jeeves-jira configuration options."""

    output_format: OutputFormat
    jira: JIRA
    cache: JiraCache
    fields: JiraFieldsRepository

    @cached_property
    def current_issue(self) -> Issue:
        """Construct the currently selected JIRA issue object."""
        return self.jira.issue(self.cache.selected_issue_key)

    @cached_property
    def field_key_by_name(self) -> FieldKeyByName:
        """
        Map field names to keys.

        This is useful for `custom*` and the like: the field key can vary
        among installations but the canonical name helps us to find that key.
        """
        return {
            field['name']: field['key']
            for field in self.jira.fields()
            if field['clauseNames']
        }


class JeevesJiraContext(Context):
    """Typer context with GlobalOptions instance as obj."""

    obj: GlobalOptions
