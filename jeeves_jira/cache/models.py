from typing import Optional

from pydantic import BaseModel


class JiraCache(BaseModel):
    """Cached JIRA configuration."""

    selected_issue_key: Optional[str] = None
