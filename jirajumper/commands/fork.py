from typing import Optional

import rich
from jira import JIRAError
from typer import Option

from jirajumper import default_options
from jirajumper.cache.cache import JeevesJiraContext
from jirajumper.commands.clone import clone
from jirajumper.commands.link import LinkType, link
from jirajumper.commands.select import jump
from jirajumper.commands.update import JIRAUpdateFailed


def fork(
    context: JeevesJiraContext,
    link_type: LinkType = Option(LinkType.DEPENDED_ON_BY, '--type'),
    stay: bool = False,
    assignee: Optional[str] = default_options.ASSIGNEE,
    **options: str,
):
    """Fork a JIRA issue."""
    child_issue = clone(
        context=context,
        stay=True,
        assignee=assignee,
        **options,
    )

    link(
        context=context,
        link_type=link_type,
        specifiers=[child_issue.key],
    )

    if not stay:
        jump(
            context=context,
            specifier=child_issue.key,
        )
