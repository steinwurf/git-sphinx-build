from . import command
from . import git_run
from . import git_url_parser

import click
import tempfile
import hashlib
import os

class Repository(object):

    def __init__(self, git, git_url_parser, log):
        self.git = git
        self.git_url_parser = git_url_parser
        self.log = log

        self.git_info = None

        self.git_url = None
        
        # Path to the local working tree (if one exists)
        self.workingtree_path = None

        # Path to where this repository is cloned
        self.repository_path = None

    def prepare(self, repository, clone_path):

        assert repository
        assert os.path.isdir(clone_path)

        clone_path = os.path.abspath(os.path.expand_user(clone_path))

        # Get the URL to the repository
        if os.path.isdir(repository):
            self.workingtree_path = repository
            git_url = self.git.remote_origin_url(cwd=repository)
        else:
            git_url = repository

        # Compute the clone path
        git_info = self.git_url_parser.parse(url=git_url)

        url_hash = hashlib.sha1(git_url.encode('utf-8')).hexdigest()[:6]
        repository_dir = git_info.name + '-' + url_hash

        self.repository_path = os.path.join(clone_path, repository_dir)

        # Get the updates
        if os.path.isdir(self.repository_path):
            git.fetch(cwd=self.repository_path)
        else:
            git.clone(repository=git_url, directory=self.repository_path, cwd=clone_path)


@click.command()
@click.argument('repository')
@click.option('--clone_path')
#@click.option('--build_path')
#@click.option('--remote_only')
def cli(repository, clone_path):
    
    git = git_run.GitRun(git_binary='git', run=command.run)
    parser = git_url_parser.GitUrlParser()

    repository = Repository(git=git, git_url_parser=parser, log="ok")

    repository.prepare(repository=repository, clone_path=clone_path)

    # current_branch, other_branches = git.branch(cwd=repo_dir)
    # tags = git.tags(cwd=repo_dir)

    # checkouts = [current_branch] + other_branches + tags
    # checkouts = [c.strip() for c in checkouts]

    # print(checkouts)

    # for checkout in checkouts:

    #     checkout_path = os.path.join(build_dir, 'checkouts', checkout)

    #     if os.path.isdir(checkout_path):
    #         remove_directory(path=checkout_path)

    #     shutil.copytree(src=cwd, dst=checkout_path, symlinks=True)

    #     args = ['git', 'checkout', '-f', checkout]
    #     ctx.cmd_and_log(args, cwd=checkout_path)

    #     docs_path = os.path.join(build_dir, 'docs', checkout)

    #     try:

    #         venv.run('sphinx-build --no-color -w log.txt -b html docs {}'.format(
    #             docs_path), cwd=checkout_path)

    #     except Exception:
    #         continue

    # print("Current branch {}".format(
    #     git.current_branch(cwd=ctx.path.abspath())))


if __name__ == "__main__":
    cli()
