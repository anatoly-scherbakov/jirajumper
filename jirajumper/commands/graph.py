import html
import textwrap
from types import MappingProxyType

import graphviz

from jirajumper.cache.cache import JeevesJiraContext
from jirajumper.client import issue_url
from jirajumper.commands.list_issues import generate_jql

DEFAULT_COLOR_MAP = MappingProxyType({
    'Code Review': '#BD34D1',  # Pink
    'In Review': '#BD34D1',  # Pink
    'Refinement': '#897A5F',  # Brown
    'In Progress': '#F7C325',  # Yellow
    # 'Queued': '#AC6363',      # Crimson
    'Rejected': '#AC6363',  # Crimson
    'Queued': '#D3455B',  # Red
    # 'Draft': '#CCCCCC',       # Gray
    # 'Draft': '#E8833A',  # Orange
    'Draft': '#EEEEEE',  # Light Gray
    # 'Closed': '#E8833A',      # Orange
    'Closed': '#CCCCCC',  # Gray
    'Put On Ice': '#2C88D9',  # Blue
    'QA': '#730FC3',  # Purple
    'In Testing': '#730FC3',  # Purple
    # 'Done': '#207868',        # Green
    'Done': '#1AAE9F',  # Mint
})


def graph(
    context: JeevesJiraContext,
    **options,
):
    """List JIRA issues by criteria."""
    jql = generate_jql(
        fields=context.obj.fields,
        options=options,
    )

    logger = context.obj.logger
    logger.info('JQL: `%s`', jql)

    jira = context.obj.jira
    issues = jira.search_issues(jql, maxResults=None)

    graph = graphviz.Digraph(
        comment='Jira task links',
        graph_attr={
            'rankdir': 'LR',
        }
    )
    for issue in issues:
        color = DEFAULT_COLOR_MAP.get(
            issue.fields.status.name,
            'white',
        )

        wrapped_summary = '<br/>'.join(
            textwrap.wrap(
                html.escape(issue.fields.summary.replace('"', '')),
                width=20,
            )
        )

        if (
            issue.fields.issuetype.name == 'Epic' and
            issue.fields.status.statusCategory.name != 'Done'
        ):
            logger.info('Retrieving children for epic %s...', issue)
            epic_children = jira.search_issues(
                f'"Epic Link" = {issue.key}',
                maxResults=None,
            )
            total_count = len(epic_children)
            done_count = len([
                issue
                for issue in epic_children
                if issue.fields.status.statusCategory.name == 'Done'
            ])
            progress = f'<I>[{done_count} of {total_count}]</I>'
        else:
            progress = ''

        label = textwrap.dedent(f'''
            <TABLE BGCOLOR="{color}" BORDER="0" CELLBORDER="1" CELLSPACING="0">
                <TR><TD ALIGN="left"><B>{issue.key}</B> <I>{issue.fields.issuetype}</I></TD></TR>
                <TR><TD ALIGN="left">{wrapped_summary}</TD></TR>
                <TR><TD ALIGN="left">{issue.fields.assignee}</TD></TR>
                <TR><TD ALIGN="left">{issue.fields.status} {progress}</TD></TR>
            </TABLE>
        ''')

        graph.node(
            issue.key,
            f'<{label}>',
            shape='none',
            href=issue_url(context.obj.jira.server_url, issue.key),
            target='_blank',
        )

        links = issue.fields.issuelinks
        for link in links:
            linked_issue = getattr(link, 'inwardIssue', None)
            if not linked_issue:
                continue

            if (
                linked_issue.fields.status.name == 'Put On Ice' and
                issue.fields.status.name in {'In Progress', 'Queued'}
            ):
                edge_options = {'color': '#D3455B', 'fontcolor': '#D3455B'}
            else:
                edge_options = {}

            graph.edge(
                linked_issue.key,
                issue.key,
                link.type.name,
                **edge_options,
            )

    graph.render(
        '/tmp/jeeves-jira-roadmap',
        format='png',
        view=True,
    )
