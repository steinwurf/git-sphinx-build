#! /usr/bin/env python
# encoding: utf-8

import os
import sys
import hashlib
import shutil

from . import git_run
from . import command


class VirtualEnv(object):
    """ Simple object which can be used to work within a virtualenv.


    venv = VirtualEnv.create(cwd='/tmp', runner=command.run, name=None)

    It is important to be aware of the cwd parameter, e.g. if you access files
    etc. it will be relative to cwd. So if cwd is the 'build' directory and you
    access a file in the root of the repository it will need to be prefixed
    with '../somefile.txt'.
    """

    def __init__(self, env, cwd, path, runner):
        """
        Wraps a created virtualenv
        """
        self.env = env
        self.path = path
        self.cwd = cwd
        self.runner = runner

        # Make sure the virtualevn Python executable is first in PATH
        if sys.platform == 'win32':
            python_path = os.path.join(path, 'Scripts')
        else:
            python_path = os.path.join(path, 'bin')

        print(self.env['PATH'])

        self.env['PATH'] = os.path.pathsep.join(
            [python_path, self.env['PATH']])

        print(self.env['PATH'])

    def run(self, cmd, cwd=None):
        """ Runs a command in the virtualenv.

        :param cmd: The command to run.
        :param cwd: The working directory i.e. where to run the command. If not
            specified the cwd used to create the virtual env will be used.
        """
        if not cwd:
            cwd = self.cwd

        return self.runner(command=cmd, cwd=cwd, env=self.env)

    def pip_local_download(self, pip_packages_path, packages):
        """ Downloads a set of packages from pip.

        :param pip_packages_path: Path to pip packages (is used when
            downloading/installing pip packages)
        :param packages: Package names as string, which should be
            downloaded.
        """
        packages = " ".join(packages)

        self.run('python -m pip download {} --dest {}'.format(
            packages, pip_packages_path))

    def pip_local_install(self, pip_packages_path, packages):
        """ Installs a set of packages from pip, using local packages from the
        path directory.

        :param pip_packages_path: Path to pip packages (is used when
            downloading/installing pip packages)
        :param packages: Package names as string, which be installed in the
            virtualenv
        """
        packages = " ".join(packages)

        assert(os.path.isdir(pip_packages_path))

        self.run('python -m pip install --no-index --find-links={} {}'.format(
            pip_packages_path, packages))

    def pip_install(self, packages):
        """ Installs a set of packages from pip

        :param packages: Package names as string, which be installed in the
            virtualenv
        """
        packages = " ".join(packages)

        self.run('python -m pip install {}'.format(packages))

    @staticmethod
    def create(cwd, env=None, runner=None, name=None, overwrite=False):
        """ Create a new virtual env.

        :param ctx: The Waf Context used to run commands.
        :param cwd: The working directory, as a string, where the virtualenv
            will be created and where the commands will run.
        :param env: The environment to use during creation of the virtualenv,
            once created the PATH and PYTHONPATH variables will be cleared to
            reflect the virtualenv. You must make sure that the virtualenv
            module is avilable. Either as a system package or by specifying the
            PYTHONPATH variable.
        :param name: The name of the virtualenv, as a string. If None a default
            name will be used.
        :param overwrite: If an existing virtualenv with the same name already
            exists we will overwrite it. To reuse the virtualenv pass
            overwrite=False.
        """

        # The Python executable
        python = sys.executable

        if not runner:
            runner = command.run

        if not env:
            # Use the current environment
            env = dict(os.environ)

        if not name:

            # Make a unique virtualenv for different Python executables
            # (e.g. 2.x and 3.x)
            unique = hashlib.sha1(python.encode('utf-8')).hexdigest()[:6]
            name = 'virtualenv-{}'.format(unique)

        # If no virtualenv exists - we create it
        path = os.path.join(cwd, name)

        if not os.path.isdir(path):

            # Create the new virtualenv - requires the virtualenv module to
            # be available
            cmd = [python, '-m', 'virtualenv', name, '--no-site-packages']

            runner(command=cmd, cwd=cwd, env=env)

        return VirtualEnv(env=env, path=path, cwd=cwd, runner=runner)

    @staticmethod
    def default_download_path():
        return os.path.join(os.path.expanduser("~"), '.git_sphinx_build')

    @staticmethod
    def download(url=None, checkout=None, git=None, download_path=None):

        if not url:
            url = 'https://github.com/pypa/virtualenv.git'

        if not checkout:
            checkout = '15.1.0'

        if not git:
            git = git_run.GitRun()

        if not download_path:
            download_path = VirtualEnv.default_download_path()

        repo_name = 'virtualenv-' + checkout
        repo_path = os.path.join(download_path, repo_name)

        if os.path.isdir(repo_path):
            # We already downloaded the virtualevn
            return repo_path

        git.clone(repository=url, directory=repo_name, cwd=download_path)
        git.checkout(branch=checkout, cwd=repo_path)

        return repo_path
