import json
from pathlib import Path
from typing import Optional

from jira import Issue

from jirajumper.models import JiraCache


def project_path() -> Path:
    """Find project directory."""
    current_dir = Path.cwd()

    if (current_dir / 'pyproject.toml').exists():
        return current_dir

    raise ValueError('This is not a project dir!')


def settings_path() -> Path:
    return project_path() / '.cache/jeeves-jira.json'


def store(cache: JiraCache):
    settings_path().write_text(cache.json(by_alias=True))


def retrieve() -> JiraCache:
    """Retrieve JIRA configuration from cache."""
    try:
        raw_text = settings_path().read_text()
    except FileNotFoundError:
        settings_path().parent.mkdir(exist_ok=True)
        raw_text = '{}'

    raw = json.loads(raw_text)

    if raw:
        return JiraCache(**raw)

    return JiraCache()
