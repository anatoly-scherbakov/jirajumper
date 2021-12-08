"""A few default JIRA fields with their definitions and formats."""
import operator

from jirajumper.fields.field import JiraField
from jirajumper.fields.repository import JiraFieldsRepository
from jirajumper.models import FieldByName

get_name = operator.attrgetter('name')


VERSION = JiraField(
    jira_name='fixVersions',
    jql_name='fixVersion',
    human_name='version',
    description='Software product version the issue is attached to.',

    to_jira=lambda version_name: [{'name': version_name}],
    from_jira=lambda jira_value: (jira_value or None) and jira_value[0].name,
)

SUMMARY = JiraField(
    jira_name='summary',
    human_name='summary',
    description='Issue summary (issue name, issue title).',
)


EPIC_LINK = JiraField(
    jira_name=FieldByName('Epic Link'),
    human_name='epic',
    description='Epic which the issue belongs to.',
)


STATUS = JiraField(
    jira_name='status',
    human_name='status',
    description='Issue status.',

    # It is impossible to set issue status directly in update() operation.
    is_mutable=False,
    to_jira=NotImplemented,
    from_jira=get_name,
)


STATUS_CATEGORY = JiraField(
    jira_name='status.statusCategory',
    human_name='status_category',
    jql_name='statusCategory',
    description='Issue status category: "To Do", "In Progress" and "Done".',

    is_mutable=False,
    to_jira=NotImplemented,
    from_jira=get_name,
)


TYPE = JiraField(
    jira_name='issuetype',
    human_name='type',
    description='Issue type.',

    to_jira=lambda type_name: {'name': type_name},
    from_jira=get_name,
)

PROJECT = JiraField(
    jira_name='project',
    human_name='project',
    description='JIRA Project.',

    # It is impossible to easily migrate across projects.
    is_mutable=False,

    to_jira=lambda project_key: {'key': project_key},
    from_jira=operator.attrgetter('key'),
)

DESCRIPTION = JiraField(
    jira_name='description',
    human_name='description',
    description='JIRA task description body.',
)

ASSIGNEE = JiraField(
    jira_name='assignee',
    human_name='assignee',
    description='Person the issue is assigned to.',
    from_jira=lambda assignee: assignee and assignee.displayName,
    to_jira=NotImplemented,
    is_mutable=False,
)


# TODO This should be configurable in configuration files or somehow else.
FIELDS = JiraFieldsRepository([
    SUMMARY,
    ASSIGNEE,
    VERSION,

    STATUS,
    STATUS_CATEGORY,

    TYPE,
    EPIC_LINK,
    PROJECT,
    DESCRIPTION,
])
