def test_build(testdirectory):

    url = 'git@github.com:steinwurf/stub.git'

    r = testdirectory.run('git_sphinx_build {} --clone_path {}'.format(url, testdirectory.path()))
    #print(r)
    #assert 0
    pass