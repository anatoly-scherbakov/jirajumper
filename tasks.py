from pathlib import Path

from magicinvoke import Context, task


def is_python_package_or_file(path: Path) -> bool:
    """Determine if the path represents a Python code file or a package."""
    return (
        (path.is_file() and path.suffix == '.py') or
        (path.is_dir() and (path / '__init__.py').exists())
    )


@task
def find_python_targets(ctx: Context) -> None:
    """Find all Python targets in current directory."""
    targets = map(str, filter(is_python_package_or_file, Path.cwd().iterdir()))
    ctx['python_targets'] = ' '.join(targets)


@task(find_python_targets)
def lint(ctx: Context):
    """Run linters against the code base."""
    targets = ctx['python_targets']
    ctx.run(
        f'git diff origin/master | flakehell lint --diff {targets}',
        pty=True,
    )


@task(find_python_targets, name='format')
def fmt(ctx: Context):
    """Auto-format code."""
    targets = ctx['python_targets']
    ctx.run(f'isort {targets}')


@task
def publish(ctx: Context):
    """Publish to PyPI."""
    ctx.run('poetry publish --build', pty=True)


@task
def inc(ctx: Context):
    """Increment version number."""
    ctx.run('poetry version patch', pty=True)


@task
def new_branch(
    ctx: Context,
    name: str,
):
    """Create a new branch with the given name and create PR."""
    ctx.run(f'git checkout -b {name}', pty=True)
    ctx.run('poetry version patch', pty=True)
    ctx.run(f'git commit -a -m "New branch: {name}"', pty=True)
    ctx.run(f'gh pr create --fill --head {name}', pty=True)
