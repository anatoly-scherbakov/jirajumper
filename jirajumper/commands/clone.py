from typing import Optional

from jira import JIRAError

from jirajumper import default_options
from jirajumper.cache.cache import JeevesJiraContext
from jirajumper.commands.select import jump
from jirajumper.commands.update import JIRAUpdateFailed, assign


def clone(
    context: JeevesJiraContext,
    stay: bool = False,
    assignee: Optional[str] = default_options.ASSIGNEE,
    summary: str = default_options.SUMMARY,
    **options: str,
):
    """Clone a JIRA issue."""
    options.update({
        'summary': summary,
    })

    parent_issue = context.obj.current_issue
    parent_issue_fields = dict(
        field.store(field.retrieve(issue=parent_issue))
        for field in context.obj.fields
        if field.is_writable()
    )

    resolved_fields = context.obj.fields.match_options(options)

    update_fields = dict(
        field.store(human_value)
        for field, human_value in resolved_fields
    )

    new_issue_fields = {
        **parent_issue_fields,
        **update_fields,
    }

    try:
        issue = context.obj.jira.create_issue(fields=new_issue_fields)
    except JIRAError as err:
        raise JIRAUpdateFailed(
            errors=err.response.json().get('errors', {}),
            fields=context.obj.fields,
        ) from err

    if not assignee:
        assignee = getattr(parent_issue.fields.assignee, 'displayName', None)

    if assignee:
        assign(
            jira=context.obj.jira,
            key=issue.key,
            assignee=assignee,
        )

    if not stay:
        jump(
            context=context,
            specifier=issue.key,
        )

    return issue
