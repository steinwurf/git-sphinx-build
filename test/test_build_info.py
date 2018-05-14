import pytest

import git_sphinx_build
from git_sphinx_build.build_info import BuildInfo


def test_build_info():

    build_info = BuildInfo()

    build_info.slug = 'slug'

    with pytest.raises(AttributeError):
        build_info.slug = 'slug2'

    assert build_info.slug == 'slug'
