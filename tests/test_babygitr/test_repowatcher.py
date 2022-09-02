"""Tests the repo watcher."""
import os
import pygit2
import pytest
import requests
import socket
from babygitr import repowatcher as br, _error as b_e
from pygit2 import Repository
from typing import Dict


####################################################################
#                        Git Configuration                         #
# ---------------------------------------------------------------- #
# These environment variables are spun up in the background by the #
#   test git server. They're used at different times throughout    #
#   the testing suite, so they're declared as a fixture here for   #
#   ease of use. Not all of these are used right now, but they're  #
#   all listed so that it's understood they may be introduced in   #
#   testing and will be understood by the testing suite.           #
####################################################################


@pytest.fixture
def git_server_config():
    return {
        "GIT_HTTP_USER": os.getenv("GIT_HTTP_USER"),
        "GIT_HTTP_PASSWORD": os.getenv("GIT_HTTP_PASSWORD"),
        "GIT_HTTP_MOCK_SERVER_PORT": os.getenv("GIT_HTTP_MOCK_SERVER_PORT"),
        "GIT_HTTP_MOCK_SERVER_ROUTE": os.getenv("GIT_HTTP_MOCK_SERVER_ROUTE"),
        "GIT_HTTP_MOCK_SERVER_ROOT": os.getenv("GIT_HTTP_MOCK_SERVER_ROOT"),
        "GIT_HTTP_MOCK_SERVER_ALLOW_ORIGIN": os.getenv(
            "GIT_HTTP_MOCK_SERVER_ALLOW_ORIGIN"
        ),
        "GIT_SSH_MOCK_SERVER_PORT": os.getenv("GIT_SSH_MOCK_SERVER_PORT"),
        "GIT_SSH_MOCK_SERVER_ROUTE": os.getenv("GIT_SSH_MOCK_SERVER_ROUTE"),
        "GIT_SSH_MOCK_SERVER_ROOT": os.getenv("GIT_SSH_MOCK_SERVER_ROOT"),
        "GIT_SSH_MOCK_SERVER_PASSWORD": os.getenv("GIT_SSH_MOCK_SERVER_PASSWORD"),
        "GIT_SSH_MOCK_SERVER_PUBKEY": os.getenv("GIT_SSH_MOCK_SERVER_PUBKEY"),
    }


####################################################################
#                        Utility Testing                           #
# ---------------------------------------------------------------- #
# This section tests some of the utilities; it also serves to      #
#   validate that the test setup functions appropriately, while    #
#   documenting the whole shebang. Sweet.                          #
####################################################################

test_cases = [
    (
        "https://github.com/lunarengineer-bot/lunar-engineering-managed-knowledge-base.git",
        "https://github.com/lunarengineer-bot/lunar-engineering-managed-knowledge-base.git",
    ),
    (
        "git@github.com:lunarengineer-bot/lunar-engineering-managed-knowledge-base.git",
        "git@github.com:lunarengineer-bot/lunar-engineering-managed-knowledge-base.git",
    ),
    (
        "http://localhost:8174/test_project.git",
        "http://localhost:8174/test_project.git",
    ),
]


@pytest.mark.parametrize(("path", "expectation"), test_cases)
def test__standardized_validated_path(path: str, expectation: bool) -> bool:
    assert br._standardized_validated_path(path) == expectation


test_cases_remote = [
    (
        "http://www.obviouslymadeupbadwebsite.git",
        b_e.BabyGitrConnectionError,
        "Is there a typo in your URL?",
    )
]


@pytest.mark.parametrize(("url", "exception", "error_match"), test_cases_remote)
def test__standardized_validated_path_errors(
    url: str, exception: b_e.BabyGitrBaseException, error_match: str
):
    with pytest.raises(exception, match=error_match):
        br._standardized_validated_path(url)


####################################################################
#                      Making Repositories                         #
# ---------------------------------------------------------------- #
# The section below creates a series of fixtures used for further  #
#   testing. This split marks a distinction between a repository   #
#   created *with* a remote identified and one *without* a remote  #
#   identified.                                                    #
####################################################################
test_cases = [
    dict(local_path="local", branch="knowledge_branch", remote_path=None),
    dict(
        local_path="upstream",
        branch="knowledge_branch",
        # This Tom-foolery is required for the testing suite.
        remote_path="http://127.0.0.1:8174/test_project.git",
    ),
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
    repo = br.init_repo(**input_dict)
    assert isinstance(repo, Repository)
    return repo


def test_thing(repo_instance):
    assert True


####################################################################
#                      Setting the Remote                          #
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


# test_auths = [
#     # I can set user pass
#     {"username": "lunarengineer-bot", "password": "Hah. No."},
#     # I can set GPG key
#     {
#         "username": "git",
#         "pubkey": "/babygitrsecrets/id_rsa.pub",
#         "privkey": "/babygitrsecrets/id_rsa",
#     },
#     # With a passphase!
#     {
#         "username": "git",
#         "pubkey": "/babygitrsecrets/id_rsa.pub",
#         "privkey": "/babygitrsecrets/id_rsa",
#         "passphrase": "super secret",
#     },
# ]


# @pytest.mark.parametrize(("auth_config"), test_auths)
# def test_auth_callback(auth_config: Dict[str, str]):
#     assert isinstance(br.create_auth_callback(auth_config), pygit2.RemoteCallbacks)


# @pytest.mark.usefixtures("repo_instance", "test_project")
# def test_happy_path_sync_repo(repo_instance: Repository, test_project):
#     # Add a file
#     repo_dir = repo_instance.path.replace(".git/", "")
#     stupid_file = os.path.join(repo_dir, "stupid.file")
#     # raise Exception(f"""
#     # {stupid_file}
#     # {repo_dir}
#     # """)
#     with open(stupid_file, "w") as f:
#         f.writelines(["stupidlines"])
#     br.sync_repo(
#         local_repo=repo_instance,
#         author=pygit2.Signature("BabyGitr", "babygitr@nomail.com"),
#         committer=pygit2.Signature("BabyGitr", "babygitr@nomail.com"),
#         branch="knowledge_branch",
#         auth_config={"username": "steve", "password": "steve"},
#     )
#     raise Exception(
#         f"""
#     repo dir: {repo_dir}
#     repo dir contents: {os.listdir(repo_dir)}
#     origin url: {repo_instance.remotes["origin"].url}
#     origin url contents: {os.listdir(repo_instance.remotes["origin"].url)}
#     """
#     )
