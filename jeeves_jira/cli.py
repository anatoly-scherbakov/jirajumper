from typer import Context, Typer

from jeeves_jira.cache import retrieve
from jeeves_jira.client import jira
from jeeves_jira.commands.list_issues import list_issues
from jeeves_jira.commands.select import select
from jeeves_jira.models import GlobalOptions, OutputFormat

app = Typer(help='Manage JIRA issues.')


@app.callback()
def global_options(
    context: Context,
    fmt: OutputFormat = OutputFormat.PRETTY,
):
    """Configure global options valid for most of jeeves-jira commands."""
    client = jira()
    cache = retrieve()

    context.obj = GlobalOptions(
        output_format=fmt,
        jira=client,
        cache=cache,
    )


app.command()(select)
app.command(name='list')(list_issues)
