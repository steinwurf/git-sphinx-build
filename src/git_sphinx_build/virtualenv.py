#! /usr/bin/env python
# encoding: utf-8

import os
import sys
import hashlib
import shutil
import logging

from . import git_run
from . import command
from . import commandline

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

    def __init__(self, prompt=None, log=None):

        self.prompt = prompt if prompt else commandline.Prompt()
        self.log = log if log else logging.getLogger(__name__)

    def create_environment(self, path):

        if not os.path.isdir(path):

            args = ['python', '-m', 'virtualenv', path,
                    '--no-site-packages']

            self.prompt.run(command=args)

        # Create a new environment based on the new virtualenv
        env = dict(os.environ)

        # Make sure the virtualenv Python executable is first in PATH
        if sys.platform == 'win32':
            python_path = os.path.join(path, 'Scripts')
        else:
            python_path = os.path.join(path, 'bin')

        env['PATH'] = os.path.pathsep.join([python_path, env['PATH']])

        return env


def prompt_from_git(git, clone_path, prompt_class, log):
    """ This method will construct the VirtualEvn with a command where
        the virtualenv is in the path.
    """

    repo_path = os.path.join(clone_path, VERSION)

    if not os.path.isdir(repo_path):

        log.debug('Cloning {} into {}'.format(URL, repo_path))

        git.clone(repository=URL, directory=repo_path,
                  cwd=clone_path)

        git.checkout(branch=VERSION, cwd=repo_path)

    log.debug('Using virtualenv from {}'.format(URL, repo_path))

    env = dict(os.environ)
    env.update({'PYTHONPATH': clone_path})

    process = prompt_class(env=env)

    return VirtualEnv(process=process, process_factory=process_factory,
                      log=log)
