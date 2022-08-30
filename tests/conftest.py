"""Create pytest fixtures."""
import os
import pytest
import tempfile
from babygitr import repowatcher as br


@pytest.fixture(scope="package")
def test_dir():
    with tempfile.TemporaryDirectory() as t:
        # Create a file for testing purposes.
        with open(os.path.join(t, "silly.txt"), "w") as f:
            f.write("silly")
        yield t


# This will serve as a 'remote'.
@pytest.mark.usefixtures("test_dir")
@pytest.fixture(scope="package")
def test_project(test_dir):
    br.init_repo(
        local_path=f"{test_dir}/test_project",
    )
    return f"{test_dir}/test_project"
