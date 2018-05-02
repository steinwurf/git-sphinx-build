import git_sphinx_build
#import git_sphinx_build.run


def test_run(testdirectory):
    r = git_sphinx_build.run('python --version', cwd=testdirectory.path())
