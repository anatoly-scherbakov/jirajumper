import rich
from jira import JIRAError

from jirajumper.cache.cache import JeevesJiraContext
from jirajumper.commands.update import JIRAUpdateFailed


def clone(
    context: JeevesJiraContext,
    **options: str,
):
    """Clone a JIRA issue."""
    parent_issue = context.obj.current_issue
    parent_issue_fields = {
        field.jira_name: field.retrieve(issue=parent_issue)
        for field in context.obj.fields
    }

    update_fields = context.obj.fields.match_options(options)

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

    rich.print(issue)
