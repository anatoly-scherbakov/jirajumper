from jirajumper.fields.defaults import STATUS_CATEGORY


def test_status_category():
    resolved_field = STATUS_CATEGORY.resolve(field_key_by_name={})
    assert resolved_field.jira_name == 'status.statusCategory'
    assert resolved_field.jql_name == 'statusCategory'
