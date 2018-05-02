from . import command
from . import git

import click
import tempfile


@click.command()
@click.argument('url')
def cli(url):

    git = Git(git_binary='git', run=command.run)

    temp_dir = tempfile.gettempdir()
    repo_dir = os.path.join(temp_dir, 'repo')

    git.clone(repository=url, directory=repo_dir, cwd=temp_dir)

    current_branch, other_branches = git.branch(cwd=repo_dir)
    tags = git.tags(cwd=repo_dir)

    checkouts = [current_branch] + other_branches + tags
    checkouts = [c.strip() for c in checkouts]

    print(checkouts)

    for checkout in checkouts:

        checkout_path = os.path.join(build_dir, 'checkouts', checkout)

        if os.path.isdir(checkout_path):
            remove_directory(path=checkout_path)

        shutil.copytree(src=cwd, dst=checkout_path, symlinks=True)

        args = ['git', 'checkout', '-f', checkout]
        ctx.cmd_and_log(args, cwd=checkout_path)

        docs_path = os.path.join(build_dir, 'docs', checkout)

        try:

            venv.run('sphinx-build --no-color -w log.txt -b html docs {}'.format(
                docs_path), cwd=checkout_path)

        except Exception:
            continue

    print("Current branch {}".format(
        git.current_branch(cwd=ctx.path.abspath())))


if __name__ == "__main__":
    cli()
