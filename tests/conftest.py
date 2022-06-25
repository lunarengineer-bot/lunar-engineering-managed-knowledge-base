"""Create pytest fixtures."""
import pytest
import tempfile


@pytest.fixture
def test_dir():
    with tempfile.TemporaryDirectory() as t:
        yield t
