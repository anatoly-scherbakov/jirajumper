"""A few default JIRA fields with their definitions and formats."""
import operator

from jirajumper.fields.field import JiraField
from jirajumper.fields.repository import JiraFieldsRepository
from jirajumper.models import FieldByName

get_name = operator.attrgetter('name')


VERSION = JiraField(
    jira_name='fixVersions',
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
    to_jira=NotImplemented,
    from_jira=get_name,
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
    to_jira=lambda assignee_name: {'name': assignee_name},
)


# TODO This should be configurable in configuration files or somehow else.
FIELDS = JiraFieldsRepository([
    SUMMARY,
    VERSION, STATUS,
    TYPE,
    EPIC_LINK,
    PROJECT,
    DESCRIPTION,
])
