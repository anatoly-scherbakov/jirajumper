from jira import JIRAError

from jirajumper.cache.cache import JeevesJiraContext
from jirajumper.commands.select import jump
from jirajumper.commands.update import JIRAUpdateFailed


def clone(
    context: JeevesJiraContext,
    stay: bool = False,
    **options: str,
):
    """Clone a JIRA issue."""
    parent_issue = context.obj.current_issue
    parent_issue_fields = dict(
        field.store(field.retrieve(issue=parent_issue))
        for field in context.obj.fields
        if field.is_writable()
    )

    raise ValueError(parent_issue_fields)

    resolved_fields = context.obj.fields.match_options(options)

    update_fields = dict(
        field.store(human_value)
        for field, human_value in resolved_fields
    )

    new_issue_fields = {
        **parent_issue_fields,
        **update_fields,
    }

    # raise ValueError(new_issue_fields)

    try:
        issue = context.obj.jira.create_issue(fields=new_issue_fields)
    except JIRAError as err:
        raise JIRAUpdateFailed(
            errors=err.response.json().get('errors', {}),
            fields=context.obj.fields,
        ) from err

    if not stay:
        jump(
            context=context,
            specifier=issue.key,
        )

    return issue
