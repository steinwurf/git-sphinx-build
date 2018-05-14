from . import command
import git_sphinx_build.commandline
import git_sphinx_build.repository
import git_sphinx_build.git
from . import git_url_parser
from . import cache
from . import run_error
from . import sphinx
from . import sphinx_config
from . import sphinx_environment
from . import virtualenv
from . import tasks
from . import build_info

import click
import tempfile
import hashlib
import os
import logging


@click.command()
@click.argument('repository')
@click.option('--clone_path')
@click.option('--build_path')
#@click.option('--remote_only')
def cli(repository, clone_path, build_path):

    logging.basicConfig(filename='git_sphinx_build.log', level=logging.DEBUG)

    log = logging.getLogger(__name__)

    git = git_sphinx_build.git.GitRun(git_binary='git', runner=command.run)
    parser = git_url_parser.GitUrlParser()

    venv = virtualenv.VirtualEnv.from_git(
        git=git, clone_path=os.path.join(clone_path, 'local-virtualenv'),
        log=log)

    venv = virtualenv.NameToPathAdapter(
        virtualenv=venv,
        virtualenv_root_path=os.path.join(clone_path, 'build_environements'))

    environment = sphinx_environment.SphinxEnvironment(
        prompt=git_sphinx_build.commandline.Prompt(), virtualenv=venv)

    config = sphinx_config.SphinxConfig()

    spnx = sphinx.Sphinx(sphinx_config=config,
                         sphinx_environment=environment,
                         prompt=git_sphinx_build.commandline.Prompt())

    repo = git_sphinx_build.repository.Repository(
        git=git, git_url_parser=parser, log="ok")

    repo.clone(repository=repository, clone_path=clone_path)

    with cache.Cache(cache_path=build_path, unique_name=repo.unique_name) as cas:

        workingtree_generator = tasks.WorkingtreeGenerator(
            repository=repo,
            build_path=build_path, sphinx=spnx)

        git_branch_generator = tasks.GitBranchGenerator(
            repository=repo,
            build_path=build_path, sphinx=spnx, git=git, cache=cas)

        # git_tag_generator = tasks.GitTagGenerator(
        #     repository=repo,
        #     build_path=build_path, sphinx=sphinx, git=git, cache=cas)

        task_generator = tasks.TaskFactory()
        task_generator.add_generator(generator=workingtree_generator)
        task_generator.add_generator(generator=git_branch_generator)
        # task_generator.add_generator(generator=git_tag_generator)

        tsk = task_generator.tasks()

        for task in tsk:

            try:
                bi = build_info.BuildInfo()
                result = task.run(build_info=bi)
                print(bi)

            except RuntimeError as re:
                log.debug(re)


if __name__ == "__main__":
    cli()
