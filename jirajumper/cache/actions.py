import json
import os
from pathlib import Path

from jirajumper.cache.cache import JiraCache


def project_path() -> Path:
    """Find project directory."""
    current_dir = Path.cwd()

    if (current_dir / 'pyproject.toml').exists():
        return current_dir

    raise ValueError('This is not a project dir!')


def construct_cache_file_path() -> Path:
    """Path to jirajumper cache file."""
    return Path(os.getenv(
        'JIRAJUMPER_CACHE',
        Path.home() / '.cache/jirajumper',
    )) / 'jirajumper.json'
