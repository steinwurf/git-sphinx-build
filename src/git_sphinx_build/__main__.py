from . import command
from . import git_run
from . import git_url_parser
from . import cache
from . import run_error

import click
import tempfile
import hashlib
import os
import logging


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

        # A unique name computed based on the git URL
        self.unique_name = None

    def prepare(self, repository, clone_path):

        assert repository
        assert os.path.isdir(clone_path)

        clone_path = os.path.abspath(os.path.expanduser(clone_path))

        # Get the URL to the repository
        if os.path.isdir(repository):
            self.workingtree_path = repository
            git_url = self.git.remote_origin_url(cwd=repository)
        else:
            git_url = repository

        # Compute the clone path
        git_info = self.git_url_parser.parse(url=git_url)

        url_hash = hashlib.sha1(git_url.encode('utf-8')).hexdigest()[:6]
        self.unique_name = git_info.name + '-' + url_hash

        self.repository_path = os.path.join(clone_path, self.unique_name)

        # Get the updates
        if os.path.isdir(self.repository_path):
            self.git.fetch(cwd=self.repository_path)
        else:
            self.git.clone(repository=git_url,
                           directory=self.repository_path, cwd=clone_path)

    def tags(self):
        return self.git.tags(cwd=self.repository_path)

    def branches(self):
        _, remote = self.git.branch(cwd=self.repository_path, remote=True)

        # Remote branches look like origin/master, origin/some_branch etc.
        # We flatten this.

        return remote


class BuildProperties(object):

    def environement(self):
        pass

    def docs_path(self):
        pass


@click.command()
@click.argument('repository')
@click.option('--clone_path')
@click.option('--build_path')
#@click.option('--remote_only')
def cli(repository, clone_path, build_path):

    logging.basicConfig(filename='git_sphinx_build.log', level=logging.DEBUG)

    log = logging.getLogger(__name__)

    git = git_run.GitRun(git_binary='git', runner=command.run)
    parser = git_url_parser.GitUrlParser()
    return

    # sphinx = cache.Sphinx(runner=command.run)

    # repo = Repository(git=git, git_url_parser=parser, log="ok")

    # repo.prepare(repository=repository, clone_path=clone_path)

    # with cache.Cache(cache_path=build_path, unique_name=repo.unique_name) as cas:

    #     workingtree_generator = cache.WorkingtreeGenerator(
    #         repository=repo,
    #         build_path=build_path, sphinx=sphinx)

    #     git_branch_generator = cache.GitBranchGenerator(
    #         repository=repo,
    #         build_path=build_path, sphinx=sphinx, git=git, cache=cas)

    #     git_tag_generator = cache.GitTagGenerator(
    #         repository=repo,
    #         build_path=build_path, sphinx=sphinx, git=git, cache=cas)

    #     task_generator = cache.TaskFactory()
    #     task_generator.add_generator(generator=workingtree_generator)
    #     task_generator.add_generator(generator=git_branch_generator)
    #     task_generator.add_generator(generator=git_tag_generator)

    #     tasks = task_generator.tasks()

    #     for task in tasks:

    #         try:
    #             result = task.run()
    #             print(result)

    #         except run_error.RunError as re:
    #             log.debug(re)


if __name__ == "__main__":
    cli()
