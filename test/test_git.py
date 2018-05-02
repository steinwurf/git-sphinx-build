import git_sphinx_build
#import git_sphinx_build.run


def test_git(testdirectory):
    git = git_sphinx_build.Git(git_binary="git", run=git_sphinx_build.run)

    print(git.version(cwd=testdirectory.path()))
