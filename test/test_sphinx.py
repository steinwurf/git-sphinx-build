import mock

import git_sphinx_build
from git_sphinx_build.cache import Sphinx


def test_sphinx_find_conf(testdirectory):
    nested_a = testdirectory.mkdir('a')
    nested_b = nested_a.mkdir('b')

    nested_b.write_text(filename='conf.py', data=u'hello', encoding='utf-8')

    runner = mock.Mock()
    virtualenv = mock.Mock()

    sphinx = Sphinx(runner=runner, virtualenv=virtualenv)

    path = sphinx.find_configuration(source_path=testdirectory.path())
    assert path == nested_b.path()


def test_sphinx_build(testdirectory):
    output_dir = testdirectory.mkdir('output')
    nested_a = testdirectory.mkdir('a')
    nested_b = nested_a.mkdir('b')

    # nested_b.write_text(filename='conf.py', data=u'hello', encoding='utf-8')

    # runner = mock.Mock()

    # sphinx = Sphinx(runner=runner)

    # path = sphinx.build(source_path=testdirectory.path(),
    #                     output_path=output_dir.path(),
    #                     cwd=testdirectory.path())

    # runner.assert_called_once_with(
    #     command=['sphinx-build', '-b', 'html', nested_b.path(),
    #              output_dir.path()], cwd=testdirectory.path())
