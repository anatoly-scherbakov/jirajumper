import rich

from jirajumper.cache.cache import JeevesJiraContext


def list_issues(
    context: JeevesJiraContext,
    **kwargs,
):
    """List JIRA issues by criteria."""
    fields_and_values = [
        (applicable_field, kwargs[applicable_field.human_name])
        for applicable_field in context.obj.fields
        if kwargs.get(applicable_field.human_name)
    ]

    expressions = [
        field.to_jql(expression)
        for field, expression in fields_and_values
    ]

    jql = ' AND '.join(expressions)
    issues = context.obj.jira.search_issues(jql, maxResults=None)

    for issue in issues:
        rich.print(f'* {issue.key} {issue.fields.summary}')
