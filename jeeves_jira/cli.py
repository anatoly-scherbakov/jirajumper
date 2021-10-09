from itertools import starmap
from typing import List

import stringcase
from jira import JIRA
from typer import Context, Typer, Option

from jeeves_jira.cache import retrieve, store
from jeeves_jira.cache.models import IssueField
from jeeves_jira.client import jira
from jeeves_jira.commands.list_issues import list_issues
from jeeves_jira.commands.select import select
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


app.command()(select)
app.command(name='list')(list_issues)
