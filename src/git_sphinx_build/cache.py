import json
import os

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

    def __init__(self, runner):
        """
        :param runner: A command.run function.
        """
        self.runner = runner

    def build(self, sourcedir, outputdir, cwd, **kwargs):

        # Running sphinx-build will fail if the repository does
        # not have working docs for the given branch, tag etc.

        args = ['sphinx-build', '-b', 'html', sourcedir, outputdir]
        self.runner(args, cwd=cwd)


class BuildDirectory(object):

    def __init__(self, sphinx, log):
        """
        : param build_path: The path to the build directory as a string. The
            build directory is where the build files(HTML) will be generated.
            The different builds will be available as subdirectories in the
            build_path.
        :param runner: A command.run function.
        """
        self.sphinx = sphinx
        self.log = log

    def run(self, source_path, output_path, cwd, **kwargs):

        try:

            self.sphinx.build(sourcedir=source_path,
                              outputdir=output_path, cwd=cwd, **kwargs)

        except run_error.RunError as re:
            self.log.debug(re)
            return None

        return self.outputdir


class BuildWorkingTree(object):

    def __init__(self, build_directory):
        """
        : param build_path: The path to the build directory as a string. The
            build directory is where the build files(HTML) will be generated.
            The different builds will be available as subdirectories in the
            build_path.
        :param runner: A command.run function.
        """
        self.build_directory = build_directory

    def run(self, cwd, **kwargs):

        return self.build_directory.run(
            build_dir='workingtree', cwd=cwd)


class BuildGit(object):

    def __init__(self, build_directory, checkout, git):
        """
        : param build_path: The path to the build directory as a string. The
            build directory is where the build files(HTML) will be generated.
            The different builds will be available as subdirectories in the
            build_path.
        :param runner: A command.run function.
        """
        self.build_directory = build_directory
        self.git = git
        self.checkout = checkout

    def run(self, cwd, **kwargs):

        self.git.checkout(branch=self.checkout, cwd=self.repository_path)

        args = ['sphinx-build', '-b', 'html',
                self.repository_path, self.html_path]

        self.runner(args, cwd=self.build_path)

        return self.html_path


class Builder(object):

    def __init__(self, build_path, git, runner):
        self.build_path = build_path
        self.git = git
        self.runner = runner

    def workingtree(self, workingtree_path):
        return BuildWorkingTree(
            repository_path=workingtree_path,
            build_path=self.build_path, runner=self.runner)

    def tag(self, repository_path, tag):

        return BuildGit(
            repository_path=repository_path, build_path=self.build_path,
            category='tag', checkout=tag, git=self.git, runner=self.runner)

    def branch(self, repository_path, branch):

        return BuildGit(
            repository_path=repository_path, build_path=self.build_path,
            category='branch', checkout=branch, git=self.git, runner=self.runner)
