from typer import Typer

from jeeves_jira.commands.select import select

app = Typer(help='Manage JIRA issues.')

app.command()(select)
