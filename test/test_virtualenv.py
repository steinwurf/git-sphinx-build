import mock
import os

import git_sphinx_build
import git_sphinx_build.virtualenv as venv


def test_virtualenv_download_path():

    assert venv.default_download_path() != ""


def test_virtualenv_download(testdirectory):

    venv.download(download_path=testdirectory.path())


def test_virtualenv_create(testdirectory):

    # Set a download dir, it should not exist otherwise the test
    # will not download one
    download_path = os.path.join(testdirectory.path(), 'download')

    venv.download(download_path=download_path)

    # Create an environment where the virtualenv is available
    runner_environment = venv.environment(download_path=download_path)

    # clone_dir = testdirectory.mkdir('clone')
    # create_dir = testdirectory.mkdir('create')

    # path = VirtualEnv.download(download_path=clone_dir.path())

    # env = dict(os.environ)
    # env.update({'PYTHONPATH': path})

    # venv = VirtualEnv.create(cwd=testdirectory.path(), env=env)

    # venv.pip_install(packages=['sphinx'])
    # venv.run('sphinx-build --help')
