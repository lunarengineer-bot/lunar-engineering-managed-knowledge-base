"""Tests the repo watcher."""
import os
from random import random
import pygit2
import pytest
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
__REMOTE_PATH__ = "http://127.0.0.1:8174/test_project.git"


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
        __REMOTE_PATH__, {
            'HEAD': 'fb00629148993ef01fd17727a7ab5ce4161dc1c5',
            'refs/heads/main': 'fb00629148993ef01fd17727a7ab5ce4161dc1c5'
        }
    ),
    ('stupidexample', {})
]


@pytest.mark.parametrize(('url', 'expected_out'), test_cases)
def test_get_remotes(url: str, expected_out: Dict[str, str]) -> None:
    assert br.get_remotes(url, allow_failure=True) == expected_out


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
        __REMOTE_PATH__,
        __REMOTE_PATH__,
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


# test_cases = [
#     dict(local_path="local", branch="knowledge_branch", remote_path=None),
#     dict(
#         local_path="upstream",
#         branch="knowledge_branch",
#         # This Tom-foolery is required for the testing suite.
#         remote_path=__REMOTE_PATH__,
#     ),
# ]


# @pytest.mark.usefixtures("test_project")
# @pytest.fixture(params=test_cases, ids=["local", "upstream"])
# def test_repo(request, test_dir) -> Repository:
#     """Test make_repo happy path.

#     This takes the test directory and parametrizes that fixture.
#     """
#     # Copy the inputs.
#     input_dict = request.param.copy()
#     # Update the local path to be in the temporary directory.
#     input_dict["local_path"] = os.path.join(test_dir, input_dict["local_path"])
#     repo = br.init_repo(**input_dict)
#     assert repo
#     # assert isinstance(repo, Repository)
#     # return repo


# ####################################################################
# #                      Setting the Remote                          #
# ####################################################################
# @pytest.mark.usefixtures("test_repo")
# def test(test_repo):
#     pass
# # @pytest.mark.usefixtures("test_project")
# # @pytest.mark.usefixtures("test_dir")
# # @pytest.mark.usefixtures("repo_instance")
# # def test_happy_path_set_remote(test_dir: str, repo_instance: Repository):
# #     """Test set_remote happy path."""
# #     br.set_remote(
# #         local_repo=repo_instance, remote_url=__REMOTE_PATH__
# #     )
# #     assert repo_instance.remotes["origin"].name == "origin"
# #     assert repo_instance.remotes["origin"].url == __REMOTE_PATH__


# # test_auths = [
# #     # I can set user pass
# #     {"username": "test_user", "password": "test_password"},
# #     # I can set GPG key
# #     {
# #         "username": "git",
# #         "pubkey": "/babygitrsecrets/id_rsa.pub",
# #         "privkey": "/babygitrsecrets/id_rsa",
# #     },
# #     # With a passphase!
# #     {
# #         "username": "git",
# #         "pubkey": "/babygitrsecrets/id_rsa.pub",
# #         "privkey": "/babygitrsecrets/id_rsa",
# #         "passphrase": "super secret",
# #     },
# # ]


# # @pytest.mark.parametrize(("auth_config"), test_auths)
# # def test_auth_callback(auth_config: Dict[str, str]):
# #     assert isinstance(br.create_auth_callback(auth_config), pygit2.RemoteCallbacks)


# # @pytest.mark.usefixtures("repo_instance", "test_dir")
# # def test_happy_path_sync_repo(repo_instance: Repository, test_dir):
# #     ################################################################
# #     #           Add a local file and push it to the remote.        #
# #     ################################################################
# #     # Get a random string for use as a non-overlapping filepath.
# #     silly_name = str(round(random()*100000))
# #     repo_dir = repo_instance.path.replace(".git/", "")
# #     stupid_file = os.path.join(repo_dir, "stupid.file")
# #     with open(stupid_file, "w") as f:
# #         f.writelines(["stupidlines"])
# #     old_refcount = repo_instance.remotes['origin'].refspec_count
# #     br.sync_repo(
# #         local_repo=repo_instance,
# #         author=pygit2.Signature("BabyGitr", "babygitr@nomail.com"),
# #         committer=pygit2.Signature("BabyGitr", "babygitr@nomail.com"),
# #         branch="knowledge_branch",
# #         auth_config={"username": "test_user", "password": "test_password"},
# #     )
# #     new_refcount = repo_instance.remotes['origin'].refspec_count
# #     raise Exception(f"""
# #     Old: {old_refcount}
# #     New: {new_refcount}
# #     Repo Description: {repo_instance.describe('knowledge_branch')}
# #     """)
# #     new_path = f"{test_dir}/{silly_name}"
# #     pygit2.clone_repository(__REMOTE_PATH__, new_path, checkout_branch='knowledge_branch')
# #     raise Exception(os.listdir(new_path))
# #     raise Exception(
# #         f"""
# #     repo dir: {repo_dir}
# #     repo dir contents: {os.listdir(repo_dir)}
# #     origin url: {repo_instance.remotes["origin"].url}
# #     origin url contents: {os.listdir(repo_instance.remotes["origin"].url)}
# #     """
# #     )
# #     raise Exception(repo_instance.index.conflicts)
