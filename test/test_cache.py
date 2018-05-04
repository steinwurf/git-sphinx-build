import git_sphinx_build
from git_sphinx_build.cache import Cache


def test_cache(testdirectory):

    testdir = testdirectory.mkdir('testdir')

    c = Cache(cache_path=testdirectory.path(), unique_name='std-93242')
    c.update(sha1='32423', path=testdir.path())
    del c
