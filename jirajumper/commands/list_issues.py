from typing import Dict

import rich

from jirajumper.cache.cache import JeevesJiraContext
from jirajumper.fields import JiraFieldsRepository
from jirajumper.fields.field import ResolvedField


def generate_jql(
    fields: JiraFieldsRepository,
    options: Dict[str, str],
):
    """Generate JQL string."""
    fields_and_values = fields.match_options(options)

    field: ResolvedField
    expressions = [
        field.to_jql(expression)
        for field, expression in fields_and_values
    ]

    return ' AND '.join(expressions)


def list_issues(
    context: JeevesJiraContext,
    **options,
):
    """List JIRA issues by criteria."""
    jql = generate_jql(
        fields=context.obj.fields,
        options=options,
    )
    context.obj.logger.info('JQL: `%s`', jql)
    issues = context.obj.jira.search_issues(jql, maxResults=None)

    for issue in issues:
        rich.print(
            '* {key} [i]({status} / {assignee})[/i] {summary}'.format(
                key=issue.key,
                status=issue.fields.status,
                assignee=issue.fields.assignee,
                summary=issue.fields.summary,
            ),
        )
