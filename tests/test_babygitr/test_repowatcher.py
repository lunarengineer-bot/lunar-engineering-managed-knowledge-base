"""Tests the repo watcher."""
import pytest
from babygitr import repowatcher as br
from git import Repo

####################################################################
#                      Making Repositories                         #
# ---------------------------------------------------------------- #
# The section below lays out happy and sad path testing for        #
#   creating a local repository. This mandates that all repos must #
#   have a .git suffix. At the end this creates a single repo for  #
#   use as a fixture.                                              #
####################################################################
test_cases = [
    # Obviously good value
    ".git",
    # Do it again!
    ".git",
    # Seems like it shouldn't work, but it will make the folder
    "nonexistent/folder/.git"
]


@pytest.mark.usefixtures("test_dir")
@pytest.mark.parametrize("repo", test_cases)
def test_happy_path_make_repo(repo: str, test_dir: str):
    """Test make_repo happy path."""
    br.init_repo(f"{test_dir}/{repo}")


test_cases = [
    # Obviously bad value
    (".mit", Exception, "BabyGitr Error: Bad local repo path"),
    (None, Exception, "BabyGitr Error: Bad local repo path"),
]


@pytest.mark.usefixtures("test_dir")
@pytest.mark.parametrize(("repo", "exception", "match"), test_cases)
def test_sad_path_make_repo(
    repo: str, exception: BaseException, match: str, test_dir: str
):
    """Test make_repo sad path."""
    with pytest.raises(exception, match=match):
        br.init_repo(f"{test_dir}/{repo}")


@pytest.fixture
def test_project(test_dir):
    br.init_repo(f'{test_dir}/test_project/.git')


####################################################################
#                      Setting the Remote                          #
# ---------------------------------------------------------------- #
# The section below lays out happy and sad path testing for        #
#   connecting a local project with an upstream remote. At the end #
#   it declares an updated fixture appropriately set to the remote.#
####################################################################
test_cases = ['this project']


@pytest.mark.usefixtures("test_project")
@pytest.mark.parametrize("remote", test_cases)
def test_happy_path_set_remote(remote: str, test_project: Repo):
    """Test set_remote happy path."""
    test_project.remote(remote)


test_cases = [
    # This obviously does not exist.
    ('fictitious')
]


@pytest.mark.usefixtures("test_project")
@pytest.mark.parametrize("remote", test_cases)
def test_sad_path_set_remote(remote: str, exception: BaseException, match: str,  test_project: Repo):
    """Test set_remote sad path."""
    with pytest.raises(exception, match=match):
        test_project.remote(remote)
