import rich
from jira import JIRAError

from jirajumper.cache.cache import JeevesJiraContext
from jirajumper.commands.update import JIRAUpdateFailed


def clone(
    context: JeevesJiraContext,
    **kwargs: str,
):
    """Clone a JIRA issue."""
    parent_issue = context.obj.current_issue
    parent_issue_fields = {
        field.resolve_jira_field_name(
            field_key_by_name=context.obj.field_key_by_name,
        ): field.retrieve(
            issue=parent_issue,
            field_key_by_name=context.obj.field_key_by_name,
        )
        for field in context.obj.fields
    }

    update_fields = {
        update_field.resolve_jira_field_name(
            field_key_by_name=context.obj.field_key_by_name,
        ): kwargs[update_field.human_name]
        for update_field in context.obj.fields
        if kwargs.get(update_field.human_name)
    }

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
            field_key_by_name=context.obj.field_key_by_name,
        ) from err

    rich.print(issue)
