import click
from typer import Context, Typer, Option
from typer.core import TyperCommand

from jirajumper.cache import retrieve
from jirajumper.cache.cache import GlobalOptions
from jirajumper.client import jira
from jirajumper.commands.clone import clone
from jirajumper.commands.list_issues import list_issues
from jirajumper.commands.select import jump
from jirajumper.commands.update import update
from jirajumper.fields import FIELDS
from jirajumper.models import OutputFormat

app = Typer(
    help='Manage JIRA issues.',
    no_args_is_help=True,
)


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

    context.obj = GlobalOptions(
        output_format=format,
        jira=client,
        cache=cache,
        fields=FIELDS,
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


class UpdateCommand(TyperCommand):
    def __init__(self, **kwargs):
        custom_options = [
            click.Option(
                [f'--{field.human_name}'],
                help=field.description,
            )
            for field in FIELDS.writable()
        ]

        kwargs.update(
            params=custom_options,
        )

        super().__init__(**kwargs)


app.command()(jump)
app.command(name='list')(list_issues)
app.command()(clone)
app.command(
    cls=UpdateCommand,
    context_settings={
        'ignore_unknown_options': True,
    },
)(update)
