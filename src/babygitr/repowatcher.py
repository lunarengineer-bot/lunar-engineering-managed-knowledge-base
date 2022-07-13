"""Monitors a potentially existent git repository.

This uses functionality which exists in GitPython
https://gitpython.readthedocs.io/en/stable/tutorial.html
"""
import logging
import pygit2
from babygitr import _error as b_e
# from git import NoSuchPathError, Repo
from schema import Schema, Use
from typing import Optional

logger = logging.getLogger(__name__)

__SYNC_FREQUENCY__ = 0
__LOG_FREQUENCY__ = 0


def _remote_exists(remote: str) -> str:
    """Return True if remote exists and can be accessed.

    Parameters
    ----------
    remote: str
        A string representing the path to a remote repository.

    Returns
    -------
    remote: str
        A validated string representing the path to a remote.

    Examples
    --------
    >>> import pytest
    >>> from babygitr._error import BabyGitrBaseException
    >>> with pytest.raises(BabyGitrBaseException, match='Unable to connect'):
    ...     _remote_exists('/stupidexample')
    """
    # Can git connect to this as a remote?
    _remote = pygit2.discover_repository(remote)
    if _remote is None:
        raise b_e.BabyGitrBaseException(
            f'Unable to connect to remote {_remote}'
            )
    return _remote


def init_repo(
    local_path: str,
    branch: str = 'main',
    remote_path: Optional[str] = None,
) -> pygit2.Repository:
    """Create a local repository.

    This does one of two things; if it's given a `remote_path` then
    it will attempt to clone that repository down, else it will create
    an empty repository at the local location.

    This will also explode gently, letting you know if issues
    popped up.

    Parameters
    ----------
    local_path: str
        The local repository path.
    branch: str
        An optional branch to checkout to.
    remote_path: Optional[str] = None
        An optional remote url.

    Returns
    -------
    local_repo: Repo
        This is a repository object that can be used to control a
        local git repository.

    Examples
    --------
    This is a simple example showcasing how to work with a local
    directory. (Just, don't use the temporary directory for reals.)

    >>> from tempfile import TemporaryDirectory
    >>> with TemporaryDirectory() as t:
    ...     local_repo = init_repo(f'{t}/.git', branch='test')
    >>> type(local_repo)
    <class 'pygit2.repository.Repository'>
    >>> list(local_repo.branches)

    This is an example showcasing how to use with a 'local remote'
    >>> with TemporaryDirectory() as t:
    ...     remote_repo = init_repo(f'{t}/remote/.git', branch='test')
    ...     local_repo = init_repo(
    ...         local_path=f'{t}/local/.git',
    ...         remote_path=f'{t}/remote/.git',
    ...         branch='main',
    ...     )
    """
    if remote_path is not None:
        # This validates the repo exists and can be connected to.
        remote_path = Schema(Use(_remote_exists)).validate(remote_path)
        repo = pygit2.clone_repository(
            url=remote_path,
            path=local_path,
            checkout_branch=branch
        )
        logger.info(f"Connected to remote: {remote_path}")
    else:
        logger.warn("No remote assigned. I'll still babysit your work!")
        repo = pygit2.init_repository(
            path=local_path,
        )
        # https://www.pygit2.org/recipes/git-commit.html
        # Add all the files we're going to watch to start.
        index = repo.index
        # Just add *everything*
        index.add_all()
        # Then write it to the index.
        index.write()
        ref = "HEAD"
        message = "Initial commit"
        tree = index.write_tree()
        parents = []
        author = pygit2.Signature('Timothy David Luna', 'timmothy.d.luna@gmail.com')
        committer = pygit2.Signature('BabyGitr', 'babygitr@norealmail.com')
        repo.create_commit(ref, author, committer, message, tree, parents)
    return repo


def set_remote(local_repo, remote_name: str = 'knowledge_base') -> None:
    """Set the remote repository.

    This sets the connection to the remote. If the remote does not
    exist it will attempt to create the remote. If it cannot create
    the remote then it will die a tragic death.

    Parameters
    ----------
    local_repo: Repo
        This is a git repository instance.
    remote_project: str
        This is the path to the remote.
    **kwargs: Any
        These are keyword arguments unpacked into create_remote
    """
    raise Exception("This is up next!")
    # try:
    #     remote = local_repo.remote(remote_name)
    # except ValueError as e:
    #     # This is *most likely* because the remote doesn't exist.
    #     remote = None
    # if remote is None:
    #     local_repo.create_remote(
    #         name='',
    #         url='',
    #         **kwargs
    #     )


def authenticate_with_repo():
    """Authenticate with repository.

    This uses potentially temporary credentials to connect to a
    remote repository and generate secure and persistent
    credentials. These credentials are shared with the remote.
    """
    raise NotImplementedError


def sync_repo():
    """Sync with the remote repository.


    This polls the upstream branch for new information and pushes
    changes.
    """
    # repo.untracked_files
    raise NotImplementedError


def set_upstream_branch():
    """Set an upstream branch to sync to.

    This sets an upstream source of information which should be
    synced.
    """
    raise NotImplementedError
