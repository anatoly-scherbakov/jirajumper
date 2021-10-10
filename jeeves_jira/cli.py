from itertools import starmap
from typing import List

import click
import stringcase
from jira import JIRA
from typer import Context, Typer, Option
from typer.core import TyperCommand, TyperArgument

from jeeves_jira.cache import retrieve, store
from jeeves_jira.cache.models import IssueField
from jeeves_jira.client import jira
from jeeves_jira.commands.clone import clone
from jeeves_jira.commands.list_issues import list_issues
from jeeves_jira.commands.select import select, issue_to_json
from jeeves_jira.models import GlobalOptions, OutputFormat, JIRAField

app = Typer(help='Manage JIRA issues.')


def retrieve_issue_fields(client: JIRA) -> List[JIRAField]:
    """Retrieve possible issue fields and describe them."""
    return [
        JIRAField(**field_parameters)
        for field_parameters in client.fields()
    ]


@app.callback()
def global_options(
    context: Context,
    format: OutputFormat = Option(
        OutputFormat.PRETTY,
        help='Format to print the data in',
    ),
):
    """Configure global options valid for most of jeeves-jira commands."""
    client = jira()
    cache = retrieve()

    if not cache.issue_fields:
        cache.issue_fields = retrieve_issue_fields(client)
        store(cache)

    context.obj = GlobalOptions(
        output_format=format,
        jira=client,
        cache=cache,
    )


EDITABLE_FIELDS = frozenset({
    'epic',
    'type',
    'project',
    'version',
    'assignee',
    'description',
    'parent',
})


class CloneCommand(TyperCommand):
    def __init__(self, **kwargs):
        # FIXME 🐞 JIRA client is initialized multiple times in the code
        client = jira()

        cache = retrieve()

        # FIXME 🐞 `clone` command will crash if no issue is selected
        current_issue = client.issue(cache.selected_issue_key)

        # FIXME 🐞 `clone` command will crash if JIRA available fields have not
        #   been retrieved yet
        issue_data = issue_to_json(
            issue=current_issue,
            available_fields=cache.issue_fields,
        )

        custom_options = [
            click.Option(
                [f'--{field_name}'],
                help=f'[{field_value}]',
            )
            for field_name, field_value in issue_data.items()
            if field_name in EDITABLE_FIELDS
        ]

        kwargs.update(
            params=custom_options,
        )

        super().__init__(**kwargs)


app.command()(select)
app.command(name='list')(list_issues)
app.command(
    # context_settings={
    #     'allow_extra_args': True,
    #     'ignore_unknown_options': True,
    # },
    cls=CloneCommand,
)(clone)
