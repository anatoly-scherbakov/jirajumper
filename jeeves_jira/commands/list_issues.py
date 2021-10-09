from jeeves_jira.client import custom_fields, jira


def list_issues():
    """List JIRA issues by criteria."""
    client = jira()
    fields = custom_fields(client)


