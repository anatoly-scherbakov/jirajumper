from typing import Dict, List, Optional, Tuple

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

    def mutable(self) -> 'JiraFieldsRepository':
        """Show only fields that are mutable."""
        return JiraFieldsRepository(filter(
            lambda field: field.is_writable and field.is_mutable,
            self,
        ))

    def match_options(
        self,
        options: Dict[str, str],
    ) -> List[Tuple[JiraField, str]]:
        """
        Match fields in the repo with CLI options provided by the user.

        Returns a list of `(JiraField, str)` pairs, where `str` is the value
        assigned to this field by the user.
        """
        return [
            (field, options[field.human_name])
            for field in self
            if options.get(field.human_name)
        ]
