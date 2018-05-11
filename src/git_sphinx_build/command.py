import os
import subprocess
import time

from . import compat
from . import check_output
from . import run_result
from . import run_error


def run(command, cwd, **kwargs):
    """Runs the command
    :param command: String or list of arguments
    :param cwd: The current working directory where the command will run
    :param kwargs: Keyword arguments passed to Popen(...)
    :return: A RunResult object representing the result of the command
    """

    if isinstance(command, compat.string_type):
        kwargs['shell'] = True

    if 'env' not in kwargs:
        # If 'env' is not passed as keyword argument use a copy of the
        # current environment.
        kwargs['env'] = os.environ.copy()

    if 'stdout' not in kwargs:
        kwargs['stdout'] = subprocess.PIPE

    if 'stderr' not in kwargs:
        kwargs['stderr'] = subprocess.PIPE

    assert 'cwd' not in kwargs
    kwargs['cwd'] = cwd

    start_time = time.time()

    popen = subprocess.Popen(
        command,
        # Need to decode the stdout and stderr with the correct
        # character encoding (http://stackoverflow.com/a/28996987)
        universal_newlines=True,
        **kwargs)

    stdout, stderr = popen.communicate()

    end_time = time.time()

    if isinstance(command, list):
        command = ' '.join(command)

    result = run_result.RunResult(
        command=command, path=cwd,
        stdout=stdout, stderr=stderr, returncode=popen.returncode,
        time=end_time - start_time)

    if popen.returncode != 0:
        raise run_error.RunError(result)

    return result


class Command(object):

    def __init__(self):
        self.cwd = os.getcwd()
        self.env = dict(os.environ)
        self.stdout = subprocess.PIPE
        self.stderr = subprocess.PIPE

    def run(self, command):

        return run(command=command, cwd=self.cwd, evn=self.env,
                   stdout=self.stdout, stderr=self.stderr)


class Process(object):

    def __init__(self):
        self.cwd = os.getcwd()
        self.env = dict(os.environ)
        self.stdout = subprocess.PIPE
        self.stderr = subprocess.PIPE

    def run(self, command):

        return run(command=command, cwd=self.cwd, evn=self.env,
                   stdout=self.stdout, stderr=self.stderr)


class ProcessFactory(object):

    def build(self):
        return Process()
