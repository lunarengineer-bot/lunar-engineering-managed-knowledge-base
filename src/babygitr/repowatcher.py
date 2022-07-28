"""Monitors a potentially existent git repository.

This uses functionality which exists in GitPython
https://gitpython.readthedocs.io/en/stable/tutorial.html
"""
import logging
import os
import pygit2
from babygitr import _error as b_e
from schema import Schema, Use
from typing import Dict, List, Optional, Union

logger = logging.getLogger(__name__)

__SYNC_FREQUENCY__ = 0
__LOG_FREQUENCY__ = 0
__AUTHOR__ = pygit2.Signature("Timothy David Luna", "timmothy.d.luna@gmail.com")
__COMMITTER__ = pygit2.Signature("BabyGitr", "babygitr@norealmail.com")


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
        raise b_e.BabyGitrBaseException(f"Unable to connect to remote {_remote}")
    return _remote


def _new_repo(local_path: str) -> pygit2.Repository:
    """Create a new, empty, local repository."""
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
    parents: List[str] = []
    repo.create_commit(
        ref,  # reference_name
        __AUTHOR__,  # author
        __COMMITTER__,  # committer
        message,  # message
        tree,  # tree
        parents,  # parents
    )
    return repo


def init_repo(
    local_path: str = ".",
    branch: str = "knowledge_base",
    remote_path: Optional[str] = None,
) -> pygit2.Repository:
    """Create a local repository.

    This does one of two things; if it's given a `remote_path` then
    it will attempt to clone that repository down, else it will create
    an empty repository at the local location.

    This will set the working branch to `branch` (knowledge_base by
    default.)

    This will also explode gently, letting you know if issues
    popped up.

    What did I learn while doing this? pygit2 doesn't have good high
    level documentation.

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
    local_repo: pygit2.Repository
        This is a repository object that can be used to control a
        local git repository.

    Examples
    --------
    This is a simple example showcasing how to work with a local
    directory. (Just, don't use the temporary directory for reals.)

    >>> from tempfile import TemporaryDirectory
    >>> with TemporaryDirectory() as t:
    ...     local_repo = init_repo(f'{t}/.git', branch='test')
    ...     type(local_repo)
    <class 'pygit2.repository.Repository'>

    ...     list(local_repo.branches)

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
        # Down this leg we have a true remote to work with.
        # We'll just clone that one down!
        # This validates the repo exists and can be connected to.
        remote_path = Schema(Use(_remote_exists)).validate(remote_path)
        os.makedirs(local_path, exist_ok=True)
        repo = pygit2.clone_repository(
            url=remote_path,
            path=local_path,
        )
        logger.info(f"Connected to remote: {remote_path}")
    else:
        # Down this leg we have no remote, so we just make
        #   a blank project.
        logger.warn("No remote assigned. I'll still babysit your work!")
        # First, does a repo exist locally?
        if os.path.exists(os.path.join(local_path, '.git')):
            repo = pygit2.init_repository(
                path=local_path,
            )
        else:
            os.makedirs(local_path, exist_ok=True)
            repo = _new_repo(local_path=local_path)
        # Use the ID to return the Commit object.
    # Now checkout the branch, whether or not it exists.
    branch_obj = repo.lookup_branch(branch)
    if branch_obj is None:
        branch_obj = repo.branches.local.create(branch, repo.get(str(repo.head.target)))
    ref = repo.lookup_reference(branch_obj.name)
    repo.checkout(ref)
    return repo


def set_remote(
    local_repo: pygit2.Repository,
    remote_url: str,
    remote_name: str = "origin",
) -> None:
    """Set the remote URL for the repository.

    This sets the connection to the remote. If it cannot connect to
    the remote then it will die a tragic death.

    Tl;Dr: `git remote add origin https://github.com/<user-name>/<repo-name>.git`

    Parameters
    ----------
    local_repo: pygit2.Repository
        This is a pygit2 repository instance.
    remote_url: str
        This is the path to the remote.
    remote_name: str = 'origin'
        This is the name of the remote.
    """
    try:
        origin = local_repo.remotes[remote_name]
    except KeyError:
        origin = None
    if origin is not None:
        local_repo.remotes.set_url(remote_name, remote_url)
    else:
        origin = local_repo.remotes.create(
            remote_name,
            url=remote_url,
        )


def authenticate_with_repo(
    auth_config: Dict[str, str]
) -> Union[pygit2.credentials.UserPass, pygit2.credentials.Keypair]:
    """Authenticate with repository.

    This returns a callable object that may be used to authenticate.

    Parameters
    ----------
    auth_config: Dict[str, str]
        This is a dictionary with either the information for using
        either username/password or GPG.

    Examples
    --------
    Make a callable that can return a userpass.
    >>> cred_callable = authenticate_with_repo(dict(username='steve', password='steve!'))
    >>> type(cred_callable)
    <class 'pygit2.credentials.UserPass'>

    Make a callable that can return a GPG keypair.
    >>> cred_callable = authenticate_with_repo(
    ...     dict(
    ...         username='steve',
    ...         pubkey='~/.ssh/stupidkey.pub',
    ...         privkey='~/.ssh/stupidkey',
    ...     )
    ... )
    >>> type(cred_callable)
    <class 'pygit2.credentials.Keypair'>
    """
    _auth_config = auth_config.copy()
    userpass = set(_auth_config) == {'username', 'password'}
    keypair = (
        set(_auth_config) == {'username', 'pubkey', 'privkey', 'passphrase'}
        or
        set(_auth_config) == {'username', 'pubkey', 'privkey'}
    )
    if userpass:
        return pygit2.UserPass(**_auth_config)
    elif keypair:
        if 'passphrase' not in _auth_config:
            _auth_config['passphrase'] = ''
        return pygit2.Keypair(**_auth_config)
    else:
        raise NotImplementedError("""

        Currently Implemented Auth Methods
        ----------------------------------
        Please select from the sets below and pass a full set of parameters.

        * Username and password {'username', 'password'}
        * GPG {'username', 'pubkey', 'privkey'}
        * GPG {'username', 'pubkey', 'privkey', 'passphrase'}
        """)


def sync_repo(
    local_repo: pygit2.Repository,
) -> None:
    """Sync files, potentially with the remote repository.

    This polls the upstream branch for new information and pushes
    changes.

    Parameters
    ----------
    local_repo: pygit2.Repository
        This is the local repo.
    """
    # Here we check for new files and changes; stage those!
    index = local_repo.index
    index.add()
    index.write()
    raise NotImplementedError
