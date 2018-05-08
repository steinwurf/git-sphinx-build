import mock
import os

from git_sphinx_build.virtualenv import VirtualEnv


def test_virtualenv_create(testdirectory):

    clone_dir = testdirectory.mkdir('clone')
    create_dir = testdirectory.mkdir('create')

    path = VirtualEnv.download(download_path=clone_dir.path())

    env = dict(os.environ)
    env.update({'PYTHONPATH': path})

    venv = VirtualEnv.create(cwd=testdirectory.path(), env=env)

    venv.pip_install(packages=['sphinx'])
    venv.run('sphinx-build --help')
