"""Tests the repo watcher."""
import pytest
from babygitr import repowatcher as br

####################################################################
#                      Making Repositories                         #
# ---------------------------------------------------------------- #
# The section below lays out happy and sad path testing for        #
#   creating a local rpeository.                                   #
####################################################################
test_cases = [
    # Obviously good value
    ".git",
]


@pytest.mark.usefixtures("test_dir")
@pytest.mark.parametrize("repo", test_cases)
def test_happy_path_make_repo(repo: str, test_dir: str):
    """Test make_repo happy path."""
    br.make_repo(f"{test_dir}/{repo}")


test_cases = [
    # Obviously bad value
    (".mit", Exception, "BabyGitr Error: Bad local repo path"),
    ("nonexistent/folder/.git", Exception, "BabyGitr Error: Bad local repo path"),
]


@pytest.mark.usefixtures("test_dir")
@pytest.mark.parametrize(("repo", "exception", "match"), test_cases)
def test_sad_path_make_repo(repo, exception, match, test_dir):
    with pytest.raises(exception, match=match):
        br.make_repo(f"{test_dir}/{repo}")
