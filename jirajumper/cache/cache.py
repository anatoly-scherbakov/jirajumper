from dataclasses import dataclass
from functools import cached_property
from logging import Logger
from pathlib import Path
from typing import Optional

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


class JiraCache(BaseModel):
    """Cached JIRA configuration."""

    selected_issue_key: Optional[str] = None


def field_key_by_name(jira: JIRA) -> FieldKeyByName:
    """
    Map field names to keys.

    This is useful for `custom*` and the like: the field key can vary
    among installations but the canonical name helps us to find that key.
    """
    return {
        field['name']: field['key']
        for field in jira.fields()
    }


@dataclass
class GlobalOptions:
    """Global jeeves-jira configuration options."""

    logger: Logger
    output_format: OutputFormat
    jira: JIRA
    cache_path: Path
    fields: JiraFieldsRepository

    @cached_property
    def cache(self) -> JiraCache:
        """Retrieve jirajumper cache from disk."""
        try:
            raw_cache = self.cache_path.read_text()
        except (FileNotFoundError, PermissionError):
            return JiraCache()

        try:
            return JiraCache.parse_raw(raw_cache)
        except ValueError:
            return JiraCache()

    def store_cache(self, cache: JiraCache):
        """Store cache contents on disk."""
        encoded_cache = cache.json(by_alias=True)

        try:
            self.cache_path.write_text(encoded_cache)
        except FileNotFoundError:
            self.cache_path.parent.mkdir(parents=True, exist_ok=True)
            self.cache_path.write_text(encoded_cache)

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
        }


class JeevesJiraContext(Context):
    """Typer context with GlobalOptions instance as obj."""

    obj: GlobalOptions
