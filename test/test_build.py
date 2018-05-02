def test_build(testdirectory):

    r = testdirectory.run('git_sphinx_build')
    print(r)
    #assert 0
