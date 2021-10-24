from jira import Issue

from jirajumper.models import RetrieveIssue


def retrieve_field(issue: Issue, field_name: str):
    ...


def jira_issue_to_retrieve_issue(issue: Issue) -> RetrieveIssue:
    """Retrieve JIRA issue fields into a readable form."""
    fields = issue.fields

    return RetrieveIssue(
        summary=fields.summary,
        issue_type=fields.issuetype.name,
        version=fields.fixVersions and fields.fixVersions[0].name,
        project=fields.project.key,
        epic_name=...,
        epic_link=...,
        assignee=fields.assignee and fields.assignee.accountId,
    )
