import json
import os
import shutil
import hashlib
import sys

from . import run_error


class Cache:

    def __init__(self, cache_path, unique_name):
        """ Open or create a new cache

        :param cache_path: The path to the cache directory as a string. The
            cache directory is where the cache files (json) which contains
            information about the different builds will be stored.
        :param unique_name: The unique name of the repository as a string
        """

        # Read the "cache" from json
        filename = unique_name + '.json'
        cache_path = os.path.abspath(os.path.expanduser(cache_path))

        self.filepath = os.path.join(cache_path, filename)

        # Dict which will hold the cached values
        self.cache = None

    def __enter__(self):

        if os.path.isfile(self.filepath):

            with open(self.filepath, 'r') as json_file:
                self.cache = json.load(json_file)

        else:
            self.cache = {}

        return self

    def __exit__(self, *args):

        with open(self.filepath, 'w') as json_file:

            json.dump(self.cache, json_file, indent=2, sort_keys=True,
                      separators=(',', ': '))

    def match(self, sha1):

        if sha1 in self.cache:
            path = self.cache[sha1]

            return os.path.isdir(path)

        return False

    def update(self, sha1, path):

        assert os.path.isdir(path)

        self.cache[sha1] = path


class Sphinx(object):

    def __init__(self, virtualenv, runner):
        """
        :param runner: A command.run function.
        """
        self.build_env = virtualenv
        self.runner = runner

    def build(self, source_path, output_path, cwd):

        assert os.path.isdir(source_path)
        assert os.path.isdir(cwd)

        # Running sphinx-build will fail if the repository does
        # not have working docs for the given branch, tag etc.
        docs_path = self.find_configuration(source_path=source_path)

        # Create the environment (with sphinx installed etc)
        env = self.create_environment(docs_path=docs_path, cwd=cwd)

        if not os.path.isdir(output_path):
            os.makedirs(output_path)

        command = ['sphinx-build', '-b', 'html', docs_path, output_path]
        self.runner(command=command, cwd=cwd, env=env)

    def create_environment(self, docs_path, cwd):

        # Check if there is a requirements.txt file in the docs_path
        # if so we install it
        requirements_path = os.path.join(docs_path, 'requirements.txt')

        if os.path.isfile(requirements_path):

            with open(requirements_path, 'r') as requirements_file:
                requirements = requirements_file.read()

            name = self.environment_name(requirements=requirements)
            env = self.virtualenv.create(name=name)

            self.runner('python -m pip install -r {}'.format(
                requirements_path), cwd=cwd, env=env)

        else:

            name = self.environment_name(requirements='sphinx')
            env = self.virtualenv.create(name=name)

            self.runner('python -m pip install sphinx', cwd=cwd, env=env)

        return env

    def environment_name(self, requirements):

        # The Python executable
        python = sys.executable
        python_hash = hashlib.sha1(
            python.encode('utf-8')).hexdigest()[:6]

        # The requirements
        requirements_hash = hashlib.sha1(
            requirements.encode('utf-8')).hexdigest()[:6]

        name = 'sphinx-virtualenv-' + requirements_hash + '-' + python_hash

        return name

    def find_configuration(self, source_path):
        """ Find the Sphinx conf.py file.

        :return: The directory containing the Sphinx conf.py file
        """

        for root, _, filenames in os.walk(source_path):
            if 'conf.py' in filenames:
                return root

        raise run_error.RunError("No conf.py")


class SphinxVirtualEnv(object):

    def __init__(self, runner):
        pass


class WorkingtreeTask(object):

    def __init__(self, workingtree_path, build_path, sphinx):
        self.workingtree_path = workingtree_path
        self.build_path = build_path
        self.sphinx = sphinx

    def run():

        output_path = os.path.join(self.build_path, 'workingtree')

        self.sphinx.build(source_path=self.workingtree_path,
                          output_path=output_path, cwd=self.build_path)

        return {'type': 'workingtree', 'slug': 'workingtree',
                'path': output_path}


class WorkingtreeGenerator(object):

    def __init__(self, repository, build_path, sphinx):
        self.repository = repository
        self.build_path = build_path
        self.sphinx = sphinx

    def tasks(self):

        if self.repository.workingtree_path:

            task = WorkingtreeTask(
                workingtree_path=self.repository.workingtree_path,
                build_path=self.build_path,
                sphinx=self.sphinx)

            return [task]

        else:

            return []


class GitTask(object):

    def __init__(self, checkout_type, checkout, repository_path, build_path,
                 sphinx, git, cache):

        self.checkout_type = checkout_type
        self.checkout = checkout
        self.repository_path = repository_path
        self.build_path = build_path
        self.sphinx = sphinx
        self.git = git
        self.cache = cache

    def run(self):

        cwd = self.repository_path

        # https://stackoverflow.com/a/8888015/1717320
        self.git.reset(branch=self.checkout, hard=True, cwd=cwd)

        output_path = os.path.join(
            self.build_path, self.checkout_type, self.checkout)

        sha1 = self.git.current_commit(cwd=cwd)

        if self.cache.match(sha1=sha1):
            path = self.cache.path(sha1=sha1)

            if path != output_path:
                shutil.copytree(src=path, dst=output_path)

        else:

            self.sphinx.build(source_path=self.repository_path,
                              output_path=output_path, cwd=self.build_path)

            self.cache.update(sha1=sha1, path=output_path)

        return {'type': self.checkout_type, 'slug': self.checkout,
                'path': output_path}


class GitBranchGenerator(object):

    def __init__(self, repository, build_path,
                 sphinx, git, cache):

        self.repository = repository
        self.build_path = build_path
        self.sphinx = sphinx
        self.git = git
        self.cache = cache

    def tasks(self):

        tasks = []

        for branch in self.repository.branches():

            task = GitTask(checkout_type='branch', checkout=branch,
                           repository_path=self.repository.repository_path,
                           build_path=self.build_path, sphinx=self.sphinx,
                           git=self.git, cache=self.cache)

            tasks.append(task)

        return tasks


class GitTagGenerator(object):

    def __init__(self, repository, build_path,
                 sphinx, git, cache):

        self.repository = repository
        self.build_path = build_path
        self.sphinx = sphinx
        self.git = git
        self.cache = cache

    def tasks(self):

        tasks = []

        for tag in self.repository.tags():

            task = GitTask(checkout_type='tag', checkout=tag,
                           repository_path=self.repository.repository_path,
                           build_path=self.build_path, sphinx=self.sphinx,
                           git=self.git, cache=self.cache)

            tasks.append(task)

        return tasks


class TaskFactory(object):

    def __init__(self):
        self.generators = []

    def add_generator(self, generator):
        self.generators.append(generator)

    def tasks(self):

        tasks = []

        for generator in self.generators:

            generator_tasks = generator.tasks()

            tasks += generator_tasks

        return tasks
