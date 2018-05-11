import git_sphinx_build
import git_sphinx_build.commandline as cli


def test_run(testdirectory):

    prompt = cli.Prompt()
    prompt.run('python --version', cwd=testdirectory.path())
