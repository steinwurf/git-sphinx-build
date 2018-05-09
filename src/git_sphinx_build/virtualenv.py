#! /usr/bin/env python
# encoding: utf-8

import os
import sys
import hashlib
import shutil

from . import git_run
from . import command

URL = 'https://github.com/pypa/virtualenv.git'
VERSION = '15.1.0'


class VirtualEnv(object):
    """ Simple object which can be used to work within a virtualenv.


    venv = VirtualEnv.create(cwd='/tmp', runner=command.run, name=None)

    It is important to be aware of the cwd parameter, e.g. if you access files
    etc. it will be relative to cwd. So if cwd is the 'build' directory and you
    access a file in the root of the repository it will need to be prefixed
    with '../somefile.txt'.
    """

    def __init__(self, virtualenv_root, runner, runner_environment):
        self.virtualenv_root = virtualenv_root
        self.runner = runner
        self.runner_environment = runner_environment

    def create(self, name):
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

        virtualenv_path = os.path.join(self.virtualenv_root, name)

        if not os.path.isdir(virtualenv_path):

            command = ['python', '-m', 'virtualenv', virtualenv_path,
                       '--no-site-packages']

            self.runner(command=command, cwd=self.virtualenv_root,
                        env=self.runner_environment)

        # Create a new environment based on the new virtualenv
        env = dict(os.environ)

        # Make sure the virtualenv Python executable is first in PATH
        if sys.platform == 'win32':
            python_path = os.path.join(virtualenv_path, 'Scripts')
        else:
            python_path = os.path.join(virtualenv_path, 'bin')

        env['PATH'] = os.path.pathsep.join([python_path, self.env['PATH']])

        return env


def default_download_path():

    # https://stackoverflow.com/a/4028943
    return os.path.join(os.path.expanduser("~"), '.git_sphinx_build',
                        'virtualenv_source', VERSION)


def download(git=None, download_path=None):

    if not git:
        # If we don't have git - use the default
        git = git_run.GitRun()

    if not download_path:
        # If we don't have a download path - use the default
        download_path = default_download_path()

    if os.path.isdir(download_path):

        # We already have it
        return download_path

    # We do not have it - lets clone
    os.makedirs(download_path)

    git.clone(repository=URL, directory=download_path, cwd=download_path)
    git.checkout(branch=VERSION, cwd=download_path)

    return download_path


def environment(download_path):

    env = dict(os.environ)
    env.update({'PYTHONPATH': download_path})

    return env
