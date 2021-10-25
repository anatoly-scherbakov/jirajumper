import operator
from functools import partial
from itertools import filterfalse
from pathlib import Path

import click
from rich.traceback import install
from typer import Context, Option, Typer
from typer.core import TyperArgument, TyperCommand

from jirajumper.cache.cache import GlobalOptions, field_key_by_name
from jirajumper.client import jira
from jirajumper.commands.assign import assign
from jirajumper.commands.clone import clone
from jirajumper.commands.list_issues import list_issues
from jirajumper.commands.select import jump
from jirajumper.commands.update import update
from jirajumper.fields import FIELDS, JiraField
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
    cache_path: Path = Option(
        default=Path.home() / '.cache/jirajumper/jirajumper.json',
        envvar='JIRAJUMPER_CACHE_PATH',
        help='Path to the JSON file where jirajumper will store its cache.',
    ),
):
    """Configure global options valid for most of jeeves-jira commands."""
    install(show_locals=False)

    client = jira()
    key_by_name = field_key_by_name(
        jira=client,
    )

    resolved_fields = map(
        partial(
            JiraField.resolve,
            field_key_by_name=key_by_name,
        ),
        FIELDS,
    )

    context.obj = GlobalOptions(
        output_format=format,
        jira=jira(),
        fields=list(resolved_fields),
        cache_path=cache_path,
    )


class UpdateCommand(TyperCommand):
    def __init__(self, **kwargs):
        custom_options = [
            click.Option(
                [f'--{field.human_name}'],
                help=field.description,
            )
            for field in FIELDS.writable()
        ]

        existing_params = list(filterfalse(
            lambda param: (
                isinstance(param, TyperArgument) and
                param.name == 'kwargs'
            ),
            kwargs.get('params', []),
        ))

        kwargs.update(
            params=existing_params + custom_options,
        )

        super().__init__(**kwargs)


app.command()(jump)
app.command(name='list')(list_issues)

app.command(
    cls=UpdateCommand,
    context_settings={
        'ignore_unknown_options': True,
    },
)(clone)

app.command(
    cls=UpdateCommand,
    context_settings={
        'ignore_unknown_options': True,
    },
)(update)

app.command()(assign)
