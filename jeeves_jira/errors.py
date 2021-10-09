from dataclasses import dataclass
from typing import Optional

from documented import DocumentedError


@dataclass
class MissingJiraCredentials(DocumentedError):
    """
    JIRA credentials are not properly configured.

    Normally, it is recommended to configure your JIRA settings as environment
    variables - say, in `~/.profile`.

        export JIRA_SERVER='{self.server_safe}'
        export JIRA_USERNAME='{self.username_safe}'
        export JIRA_TOKEN='{self.token_safe}'

    See https://yeti.sh/jira/token about how to create an API token for your
    Atlassian account.
    """

    server: Optional[str]
    username: Optional[str]
    token: Optional[str]

    def safe(self, credential: Optional[str]) -> str:
        if credential:
            return '(something)'
        else:
            return '(not provided)'

    @property
    def server_safe(self):
        """Safe server."""
        return self.safe(self.server)

    @property
    def username_safe(self):
        """Safe username."""
        return self.safe(self.username)

    @property
    def token_safe(self):
        """Safe token."""
        return self.safe(self.token)
