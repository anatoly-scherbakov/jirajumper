import rich

from jirajumper.cache.cache import JeevesJiraContext


def list_issues(    # noqa: WPS210
    context: JeevesJiraContext,
    **options,
):
    """List JIRA issues by criteria."""
    fields_and_values = context.obj.fields.match_options(options)

    expressions = [
        field.to_jql(expression)
        for field, expression in fields_and_values
    ]

    jql = ' AND '.join(expressions)
    issues = context.obj.jira.search_issues(jql, maxResults=None)

    for issue in issues:
        rich.print(f'* {issue.key} {issue.fields.summary}')
