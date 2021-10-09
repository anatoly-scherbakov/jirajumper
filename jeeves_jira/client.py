import os
from jira import JIRA

from jeeves_jira.errors import MissingJiraCredentials


def env_server() -> str:
    """Retrieve JIRA server address."""
    return os.getenv('JIRA_SERVER')


def env_username() -> str:
    """Retrieve JIRA server username."""
    return os.getenv('JIRA_USERNAME')


def env_token() -> str:
    """Retrieve JIRA server token."""
    return os.getenv('JIRA_TOKEN')


def jira() -> JIRA:
    """Construct an instance of Jira client and establish an HTTP connection."""
    server = env_server()
    username = env_username()
    token = env_token()

    if not all([server, username, token]):
        raise MissingJiraCredentials(
            server=server,
            username=username,
            token=token,
        )

    return JIRA(
        server=server,
        basic_auth=(
            username,
            token,
        ),
    )


def issue_url(server: str, key: str) -> str:
    return f'{server}/browse/{key}'
