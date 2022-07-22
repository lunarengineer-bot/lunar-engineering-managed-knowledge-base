"""Create pytest fixtures."""
import pytest
import tempfile
from babygitr import repowatcher as br


@pytest.fixture(scope="package")
def test_dir():
    with tempfile.TemporaryDirectory() as t:
        yield t


# This will serve as a 'remote'.
@pytest.mark.usefixtures("test_dir")
@pytest.fixture(scope="package")
def test_project(test_dir):
    br.init_repo(
        f"{test_dir}/test_project",
    )
