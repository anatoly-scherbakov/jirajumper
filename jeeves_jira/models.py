from enum import Enum

from jira import JIRA
from pydantic import BaseModel
from typer import Context

from jeeves_jira.cache.models import JiraCache


class OutputFormat(str, Enum):
    """Output format."""

    PRETTY = 'pretty'
    JSON = 'json'


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
