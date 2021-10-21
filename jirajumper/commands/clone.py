from jira import JIRA

from jirajumper.models import JeevesJiraContext


def clone(
    context: JeevesJiraContext,
    **kwargs,
):
    """Clone a JIRA issue."""
    raise ValueError(kwargs)
