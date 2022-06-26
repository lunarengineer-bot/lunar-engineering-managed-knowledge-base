"""Monitors a potentially existent git repository.

This uses functionality which exists in GitPython
https://gitpython.readthedocs.io/en/stable/tutorial.html
"""
import logging
import time
from git import NoSuchPathError, Repo
from git.exc import InvalidGitRepositoryError
from typing import Dict

logger = logging.getLogger(__name__)

__SYNC_FREQUENCY__ = 0
__LOG_FREQUENCY__ = 0


def parse_cli() -> Dict[str, str]:
    """Parses command line input.

    This tears apart the command line input to return a mapping
    of the input structure.

    Returns
    -------
    config_dict: Dict[str, str]
        A configuration dictionary for a BabyGitr object.
    """
    raise NotImplementedError


def authenticate_with_repo():
    """Authenticate with repository.

    This uses potentially temporary credentials to connect to a
    remote repository and generate secure and persistent
    credentials. These credentials are shared with the remote.
    """
    raise NotImplementedError


def make_repo(local_path: str = ".git") -> Repo:
    """Create a local repository.

    This checks for a local repository folder and, if it doesn't
    exist, makes it. It then runs git init in the folder to convert
    the location to a git repository.

    This will then return the repository object.

    This will also explode gently, letting you know if issues
    popped up.

    Parameters
    ----------
    local_path: str = '.git'
        The local repository path.

    Returns
    -------
    local_repo: Repo
        This is a repository object that can be used to control a
        local git repository.

    Examples
    --------
    >>> from tempfile import TemporaryDirectory
    >>> with TemporaryDirectory() as t:
    ...     local_repo = make_repo(f'{t}/.git')
    >>> type(local_repo)
    <class 'git.repo.base.Repo'>

    """
    # 0. Does this end in .git?
    if not isinstance(local_path, str) or not local_path.endswith(".git"):
        raise Exception(
            f"""BabyGitr Error: Bad local repo path!
        Local path does not meet the folliwing criteria:
        1. Is a string
        2. Ends in .git

        local_path: {local_path}
        """
        )
    # 1. Is this already a repo?
    try:
        # This is going to blow up if there's not a .git folder.
        repo = Repo(local_path)
    except InvalidGitRepositoryError:
        repo = None
    except NoSuchPathError:
        repo = None

    # 2. Try and make a repo!
    if repo is None:
        try:
            repo = Repo.init(local_path, bare=True)
        except BaseException as e:
            raise Exception(
                """BabyGitr Error: Unable to create local repo.

            Something crazy happened. Maybe you don't have write access.
            Maybe it's Tuesday. Maybe it's Schmaybelline.

            Whatever, I can't do my job. Fix me, please!
            """
            ) from e

    return repo


def sync_repo():
    """Sync with the remote repository.

    This polls the upstream branch for new information and pushes
    changes.
    """
    raise NotImplementedError


def set_remote():
    """Set the remote repository.

    This sets the connection to the remote.
    """
    # Repo.remote
    raise NotImplementedError


def set_upstream_branch():
    """Set an upstream branch to sync to.

    This sets an upstream source of information which should be
    synced.
    """
    raise NotImplementedError


class BabyGitr:
    """Holds persistent state for project."""

    def __init__(self, config: Dict[str, str]) -> None:
        """Spin up a baby-gitr."""
        self._config = config
        ############################################################
        #                         Initial Setup                    #
        # -------------------------------------------------------- #
        # Here we're establishing that we can, in fact, connect to #
        #   the git repository and push and pull from the remote.  #
        # If we can't do that, we're going to throw some helpful   #
        #   (ish) errors messages and raise a new error.           #
        ############################################################
        make_repo()
        self._remote = set_remote()
        set_upstream_branch()
        authenticate_with_repo()

    def connect():
        pass

    def sync():
        pass


def main():
    """Runs the baby-giting loop"""
    ################################################################
    #                          Parse Input                         #
    # ------------------------------------------------------------ #
    # Here we're observing the input from the command line. This   #
    #   information will be reused later.                          #
    ################################################################
    application_configuration: Dict[str, str] = parse_cli()
    # Now we use that information to create a BabyGitr
    repo_watcher: "BabyGitr" = BabyGitr(config=application_configuration)
    ################################################################
    #                       Supervision Loop                       #
    # ------------------------------------------------------------ #
    # At this point we've established our bona-fides and we're on  #
    #   the list of people allowed to contribute to the upstream   #
    #   repository, or not, and we're going to go through standard #
    #   updates regardless. If we're allowed to commit to the      #
    #   remote then we will be doing that as well!                 #
    ################################################################
    while True:
        time.sleep(application_configuration["supervision_cycle_period"])
        repo_watcher.sync()


if __name__ == "__main__":
    main()
