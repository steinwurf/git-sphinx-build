def test_build(testdirectory):

    clone_dir = testdirectory.mkdir('clone')
    build_dir = testdirectory.mkdir('build')

    url = 'git@github.com:steinwurf/stub.git'

    cmd = ['git_sphinx_build', url, '--clone_path', clone_dir.path(),
           '--build_path', build_dir.path()]

    r = testdirectory.run(cmd)
    print(r)
    assert 0
    pass
