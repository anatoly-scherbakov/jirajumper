from jira import JIRA

from jeeves_jira.models import JeevesJiraContext


def clone(
    context: JeevesJiraContext,
    **kwargs,
):
    """Clone a JIRA issue."""
    raise ValueError(kwargs)
