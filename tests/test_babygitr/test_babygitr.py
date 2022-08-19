import pytest
import tempfile
from babygitr.repowatcher import init_repo
from babygitr import BabyGitr
from typing import Dict, Union


# Here we're going to create a Pytest fixture which serves as a
#   remote repository to use for testing purposes.
@pytest.fixture(scope="package", autouse=True, name="remote")
def test_remote() -> str:
    """Return reference to a remote repository.

    This returns a string filepath interpretable as a remote
    repository.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        init_repo(local_path=tmpdir)
        yield tmpdir


# Here we're going to build the test cases, create a temp
#   folder to store artifacts, and write each of the test
#   case configs out to yaml. We then create two test cases
#   for each config; one where the dict is read in already
#   parsed and one where it is being built from the config
#   file being parsed by yaml.
# In both cases the temporary directory used for the test case
#   is used as a remote repository.
# Structure here is 'configuration, expected diff of local > remote, expected diff of remote > local'
configurations = [
    # 1. Here we have no remote. This is an empty configuration.
    #   Given an empty config we don't initialize a remote, we
    #   simply track the work.
    {},
    # 2. Here we have a remote repo. That's all we have.
    #   Given a target with no further configuration we should
    #   create the default branch. This, by default, assumes
    #   access.
    {"remote_url": "specific folder name upstream?"},
    # 3. This passes optional parameters specifying:
    #   * branch name
    #   * observation_frequency
    #   * sync_frequency
    #   * merge_strategy_arguments
    {
        "remote_url": "specific folder name upstream?",
        "branch_name": "some_number",
        "observation_frequency": "some_number",
        "sync_frequency": "some_number",
    },
]

expected_diff_local = [{}, {}, {}]
expected_diff_remote = [{}, {}, {}]

test_cases = [
    (x, y, z)
    for x, y, z in zip(configurations, expected_diff_local, expected_diff_remote)
]


@pytest.mark.usefixtures("test_dir")
@pytest.mark.parametrize(("configuration", "local_diff", "remote_diff"), test_cases)
def test_babygitr(
    configuration: Union[Dict[str, str], str],
    local_diff: str,
    remote_diff: str,
    test_dir,
):
    """This is an integration test that simulates an entire workflow."""
    ################################################################
    #                     Set Everything Up                        #
    # ------------------------------------------------------------ #
    # Here we're going to read the test config file in to create   #
    #   the settings.                                              #
    # Then we're either going to clone a repository or init an     #
    #   empty one. At the end of this the BabyGitr object knows    #
    #   whether or not it can connect to a remote and how to       #
    #   authenticate with it. It also understands which *branch*   #
    #   it is maintaining. If there is an upstream branch it will  #
    #   be capable of pulling that branch onto it's own and will   #
    #   be able to make informed choices as to which information   #
    #   to retain, and which to abandon.                           #
    ################################################################
    repo_watcher: "BabyGitr" = BabyGitr(config=configuration)
    # TODO: Validation of git repository structure.
    # Test 1: Is there a .git folder in the desired location?

    ################################################################
    #                  Make Some Local Changes                     #
    # ------------------------------------------------------------ #
    # Here we're going to make some minor changes to the local     #
    #   working copy, then we're going to *commit* those changes   #
    #   and push them to the remote, if we're allowed write access.#
    # Can validate this by cloning into another folder and check   #
    #   that contents are identical w/ git diff.                   #
    ################################################################
    # TODO: Here we make a local change to an item that BabyGitr is watching
    # Here we account for the new files and the modified files.
    repo_watcher.sync()
    # TODO: Here we validate the local hashes against the hashes in the remote.
    ################################################################
    #                 Deal With a Merge Conflict                   #
    # ------------------------------------------------------------ #
    # Depending on the setup configuration this will either take   #
    #   the remote as gospel, abandoning local changes, or will    #
    #   refuse to do a pull and merge.                             #
    ################################################################
    # TODO: Here we make some changes in some files in the remote.
    repo_watcher.sync()
    # TODO: Here we validate that our merge strategy is in effect by validating the changes.
