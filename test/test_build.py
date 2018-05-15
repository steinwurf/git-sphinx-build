def test_build(testdirectory):

    data_dir = testdirectory.mkdir('data')
    output_dir = testdirectory.mkdir('output')

    url = 'git@github.com:steinwurf/stub.git'

    cmd = ['git_sphinx_build', url, '--data_path', data_dir.path(),
           '--output_path', output_dir.path()]

    r = testdirectory.run(cmd)
    print(r)

    # pass
