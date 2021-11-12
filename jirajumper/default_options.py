from typer import Option, Argument

ASSIGNEE = Option(
    None,
    help='Assignee display name or email address. Supports fuzzy search.',
)

SUMMARY = Argument(
    ...,
    help='Issue summary.'
)
