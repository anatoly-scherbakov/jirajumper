import logging
import sys
from enum import Enum
from functools import partial
from itertools import filterfalse
from pathlib import Path

import click
import rich
from rich.traceback import install
from typer import Context, Option, Typer
from typer.core import TyperArgument, TyperCommand

from jirajumper.cache.cache import GlobalOptions, field_key_by_name
from jirajumper.client import jira
from jirajumper.commands.clone import clone
from jirajumper.commands.fork import fork
from jirajumper.commands.link import link
from jirajumper.commands.list_issues import list_issues
from jirajumper.commands.select import jump
from jirajumper.commands.update import update
from jirajumper.fields import FIELDS, JiraField, JiraFieldsRepository
from jirajumper.models import OutputFormat

app = Typer(
    help='Manage JIRA issues.',
    no_args_is_help=True,
)


class LogLevel(str, Enum):  # noqa: WPS600
    """Available logging levels."""

    DEBUG = 'debug'
    ERROR = 'error'


def exception_handler(exception_type, exception, traceback):
    """Custom exception handler to look more civilized than we are."""
    exception_name = exception_type.__name__
    exception_text = str(exception)
    rich.print(
        f'[red][bold]{exception_name}:[/bold][/red] {exception_text}',
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
    log_level: LogLevel = Option(   # noqa: WPS404, B008
        LogLevel.ERROR,
        help=(
            'Log message level: `debug` (to print all debug messages and '
            'exception tracebacks), or `error` (to only log critical errors).'
        ),
    ),
):
    """Configure global options valid for most of jeeves-jira commands."""
    logger = logging.getLogger('jj')

    if log_level == LogLevel.DEBUG:
        install(show_locals=False)
        logger.setLevel(logging.DEBUG)
    else:
        sys.excepthook = exception_handler
        logger.setLevel(logging.ERROR)

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
        logger=logger,
        output_format=format,
        jira=jira(),
        fields=JiraFieldsRepository(resolved_fields),
        cache_path=cache_path,
    )


class AutoOptionsCommand(TyperCommand):
    writable_only = False
    mutable_only = False

    def __init__(self, **kwargs):
        fields = FIELDS

        if self.mutable_only:
            fields = fields.mutable()

        if self.writable_only:
            fields = fields.writable()

        custom_options = [
            click.Option(
                ['--{option_name}'.format(
                    option_name=field.human_name.replace("_", "-"),
                )],
                help=field.description,
            )
            for field in fields
        ]

        existing_params = list(filterfalse(
            lambda existing_param: (
                isinstance(existing_param, TyperArgument) and
                existing_param.name == 'options'
            ),
            kwargs.get('params', []),
        ))

        kwargs.update(
            params=existing_params + custom_options,
        )

        super().__init__(**kwargs)


class CloneCommand(AutoOptionsCommand):
    writable_only = True


class UpdateCommand(AutoOptionsCommand):
    mutable_only = True


app.command()(jump)

app.command(
    cls=CloneCommand,
    context_settings={
        'ignore_unknown_options': True,
    },
)(clone)

app.command(
    cls=CloneCommand,
    context_settings={
        'ignore_unknown_options': True,
    },
)(fork)

app.command(
    cls=UpdateCommand,
    context_settings={
        'ignore_unknown_options': True,
    },
)(update)


app.command(
    cls=AutoOptionsCommand,
    context_settings={
        'ignore_unknown_options': True,
    },
    name='list',
)(list_issues)

app.command()(link)
