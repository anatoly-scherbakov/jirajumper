from typing import List, Optional

from more_itertools import first

from jirajumper.fields.field import JiraField


class JiraFieldsRepository(List[JiraField]):
    """List of supported JIRA issue fields."""

    def find_by_jira_name(self, jira_name: str) -> Optional[JiraField]:
        """Find a field by JIRA name."""
        return first(
            filter(
                lambda field: field.jira_name == jira_name,
                self,
            ), None,
        )

    def writable(self) -> 'JiraFieldsRepository':
        """Show only fields that are writable."""
        return JiraFieldsRepository(filter(
            JiraField.is_writable,
            self,
        ))
