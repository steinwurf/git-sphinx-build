import git_sphinx_build
import git_sphinx_build.git


def test_git(testdirectory):
    git = git_sphinx_build.git.build()

    print(git.version(cwd=testdirectory.path()))
