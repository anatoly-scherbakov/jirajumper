from typer import Option

ASSIGNEE = Option(
    None,
    help='Assignee display name or email address. Supports fuzzy search.',
)
