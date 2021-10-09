from pydantic import BaseModel


class IssueField(BaseModel):
    """Custom JIRA field."""

    cli_name: str
    readable_name: str
