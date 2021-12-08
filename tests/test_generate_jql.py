from jirajumper.commands.list_issues import generate_jql
from jirajumper.fields import JiraFieldsRepository
from jirajumper.fields.defaults import STATUS_CATEGORY
from jirajumper.fields.field import ResolvedField


def test_status_category():
    status_category = ResolvedField(
        human_name='status_category',
        jira_name='statusCategory',
        unresolved_jira_name='statusCategory',
        description='',
    )

    fields = JiraFieldsRepository([status_category])
    options = {'status_category': 'boo'}
    assert generate_jql(
        fields=fields,
        options=options,
    ) == 'statusCategory = "boo"'
