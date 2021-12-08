from enum import Enum
from types import MappingProxyType
from typing import List, Set

import rich
from jira import JIRA, Issue
from typer import Argument

from jirajumper.cache.cache import JeevesJiraContext
from jirajumper.commands.select import normalize_issue_specifier


class LinkType(str, Enum):   # noqa: WPS600
    """
    Supported Jira link types.

    # FIXME Can we deduce that dynamically and store in cache?
    """

    SPLIT_FROM = 'split-from'
    SPLIT_TO = 'split-to'

    RELATES_TO = 'relates-to'

    IS_CAUSED_BY = 'is-caused-by'
    CAUSES = 'causes'

    IS_DUPLICATED_BY = 'is-duplicated-by'
    DUPLICATES = 'duplicates'

    DEPENDS_ON = 'deps'
    DEPENDED_ON_BY = 'dep'

    IS_BLOCKED_BY = 'is-blocked-by'
    BLOCKS = 'blocks'

    REMOVE = 'remove'
    CONFLUENCE = 'confluence'
    LIST = 'list'

    @property
    def jira_name(self):
        """Jira native name of the transition."""
        return self.name.lower().replace('_', ' ')


def remove_link(
    current_issue: Issue,
    issue_keys: Set[str],
    link_type: LinkType,
    jira: JIRA,
):
    """Remove links to a number of issues."""
    for existing_link in current_issue.fields.issuelinks:
        linked_issue = getattr(
            existing_link, 'outwardIssue', None,
        ) or existing_link.inwardIssue

        if linked_issue.key in issue_keys:
            jira.delete_issue_link(existing_link.id)
            rich.print(
                f'{current_issue.key} and {linked_issue.key} '
                f'are no longer connected.',
            )


def link_confluence(
    current_issue: Issue,
    issue_keys: Set[str],
    link_type: LinkType,
    jira: JIRA,
):
    """Remove links to a number of issues."""
    raise NotImplementedError('Linking to Confluence is not yet implemented.')


def list_links(
    current_issue: Issue,
    issue_keys: Set[str],
    link_type: LinkType,
    jira: JIRA,
):
    """Remove links to a number of issues."""
    rich.print('Issue links:')
    for existing_link in current_issue.fields.issuelinks:
        linked_issue = getattr(
            existing_link, 'outwardIssue', None,
        ) or existing_link.inwardIssue

        if linked_issue.key in issue_keys:
            rich.print(
                f'  * {current_issue.key} {existing_link} {linked_issue.key}',
            )


def link_default(
    current_issue: Issue,
    issue_keys: Set[str],
    link_type: LinkType,
    jira: JIRA,
):
    """Create a link between issues."""
    for issue_key in issue_keys:
        jira.create_issue_link(
            type=link_type.jira_name,
            inwardIssue=current_issue.key,
            outwardIssue=issue_key,
        )
        rich.print(
            f'* {current_issue} {link_type} {issue_key}.',
        )


LINK_MANAGERS = MappingProxyType({
    LinkType.CONFLUENCE: link_confluence,
    LinkType.REMOVE: remove_link,
    LinkType.LIST: list_links,
})


def link(
    context: JeevesJiraContext,
    link_type: LinkType,
    specifiers: List[str] = Argument(None),  # noqa: WPS404, B008
):
    """Link current issue to some other issue."""
    parent_issue = context.obj.current_issue
    jira = context.obj.jira

    issue_keys = {
        normalize_issue_specifier(
            client=jira,
            specifier=specifier,
            current_issue_key=parent_issue.key,
        )
        for specifier in specifiers or []
    }

    linker = LINK_MANAGERS.get(
        link_type,
        link_default,
    )

    return linker(
        current_issue=parent_issue,
        issue_keys=issue_keys,
        link_type=link_type,
        jira=jira,
    )
