from typing import Dict, Optional

from pydantic import BaseModel, Field


class CustomField(BaseModel):
    """Custom JIRA field."""

    internal_name: str
    readable_name: str


class JiraCache(BaseModel):
    """Cached JIRA configuration."""

    selected_issue_key: Optional[str] = None
    custom_fields: Dict[str, CustomField] = Field(default_factory=dict)
