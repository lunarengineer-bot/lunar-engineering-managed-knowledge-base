"""Tests the repo watcher."""
import os
import pytest
from babygitr import repowatcher as br
from pygit2 import Repository


####################################################################
#                      Making Repositories                         #
# ---------------------------------------------------------------- #
# The section below creates a series of fixtures used for further  #
#   testing. This split marks a distinction between a repository   #
#   created *with* a remote identified and one *without* a remote  #
#   identified.                                                    #
####################################################################
test_cases = [
    dict(local_path="local", branch="knowledge_base", remote_path=None),
    dict(local_path="upstream", branch="fried_cheese", remote_path="test_project"),
]


@pytest.mark.usefixtures("test_project")
@pytest.fixture(params=test_cases, ids=["local", "upstream"])
def repo_instance(request, test_dir) -> Repository:
    """Test make_repo happy path.

    This takes the test directory and parametrizes that fixture.
    """
    # Copy the inputs.
    input_dict = request.param.copy()
    # Update the local path to be in the temporary directory.
    input_dict["local_path"] = os.path.join(test_dir, input_dict["local_path"])
    # If this is supposed to set the remote to the test_project, do that.
    if input_dict["remote_path"] == "test_project":
        input_dict["remote_path"] = os.path.join(test_dir, "test_project")
    repo = br.init_repo(**input_dict)
    assert isinstance(repo, Repository)
    return repo


####################################################################
#                      Setting the Remote                          #
# ---------------------------------------------------------------- #
# The section below lays out happy and sad path testing for        #
#   connecting a local project with an upstream remote. At the end #
#   it declares an updated fixture appropriately set to the remote.#
####################################################################


@pytest.mark.usefixtures("test_project")
@pytest.mark.usefixtures("test_dir")
@pytest.mark.usefixtures("repo_instance")
def test_happy_path_set_remote(test_dir: str, repo_instance: Repository):
    """Test set_remote happy path."""
    br.set_remote(
        local_repo=repo_instance, remote_url=os.path.join(test_dir, "test_project")
    )
    assert repo_instance.remotes["origin"].name == "origin"
    assert repo_instance.remotes["origin"].url == os.path.join(test_dir, "test_project")
