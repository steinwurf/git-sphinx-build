import click
import tempfile
import hashlib
import os
import logging
import json

import git_sphinx_build.factory
import git_sphinx_build.build_info


@click.group(invoke_without_command=True)
@click.option('--repository')
@click.option('--data_path')
@click.option('--output_path')
def cli(repository, data_path, output_path):

    logging.basicConfig(filename='git_sphinx_build.log', level=logging.DEBUG)

    log = logging.getLogger('git_sphinx_build.main')

    # Resolve the repository
    factory = git_sphinx_build.factory.resolve_factory(
        data_path=data_path)

    git_repository = factory.build(name='git_repository')
    git_repository.clone(repository=repository)

    # Instantiate the cache
    cache_factory = git_sphinx_build.factory.cache_factory(
        data_path=data_path, unique_name=git_repository.unique_name)

    cache = cache_factory.build(name='cache')

    # Build the documentation
    factory = git_sphinx_build.factory.build_factory(
        data_path=data_path, output_path=output_path,
        git_repository=git_repository, cache=cache)

    versions = {
        'output_path': output_path,
        'builds': []
    }

    with cache:

        task_generator = factory.build(name='task_generator')

        tasks = task_generator.tasks()

        for task in tasks:

            try:
                build_info = git_sphinx_build.build_info.BuildInfo()
                task.run(build_info=build_info)

                version = {
                    'slug': build_info.slug,
                    'type': build_info.type,
                    'path': build_info.output_path
                }

                versions['builds'].append(version)

            except RuntimeError as re:
                log.debug(re)

    with open('versions.json', 'w') as versions_json:

        json.dump(versions, versions_json, indent=2, sort_keys=True,
                  separators=(',', ': '))

    # If needed push the docs


@cli.command()
@click.argument('DEST_BRANCH')
def push(dest_branch):
    click.echo('push to %s' % dest_branch)


if __name__ == "__main__":
    cli()
