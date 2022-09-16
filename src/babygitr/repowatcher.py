"""Monitors a local git repository with a potential upstream.

This adds basic functionality to make a repo, track changes,
and push to a remote, with security.

TODO: Add in a packing operation which can find commits
and collapse them. Use that in BabyGitr to clean up at routine
intervals by consolidating chores into hourly / daily / weekly
snapshots.
"""
import logging
import os
import subprocess
from babygitr import _error as b_e
from schema import Schema, Use
from typing import Dict, Optional


logger = logging.getLogger(__name__)

__BABYGITR_MAIL__ = 'BabyGitr <babygitr@nosuchemail.com>'
__BABYGITR_BRANCH__ = 'knowledge_branch'


####################################################################
#                       Validation Routine                         #
####################################################################
def get_remotes(url: str, allow_failure: bool = False) -> Dict[str, str]:
    """Return CLI output from `git ls-remote {url}` or FAILURE.

    This returns a mapping of {remote: hash}, i.e.

    If no repo exists, or it cannot be contacted it will raise an
    exception, unless `allow_failure` is true, whereby it will
    return an empty dictionary.

    Parameters
    ----------
    url: str
        A local or remote path of a git project.
    allow_failure: bool
        If allow_failure is on a failure will return `{}`

    Examples
    --------
    >>> import pytest
    >>> import subprocess
    >>> import tempfile
    >>> from babygitr._error import BabyGitrConnectionError

    This doesn't exist!
    >>> with pytest.raises(BabyGitrConnectionError):
    ...     get_remotes('stupid madeup thing')

    But if you ask nicely I won't explode.
    >>> get_remotes('stupid madeup thing', allow_failure=True)
    {}

    What does this look like fo real fo reals?
    This is an *empty* project.
    >>> currdir = os.getcwd()
    >>> with tempfile.TemporaryDirectory() as t:
    ...     os.chdir(t)
    ...     _ = subprocess.run(['git init'], shell=True, check=True, capture_output=True)
    ...     get_remotes(t)
    ...     os.chdir(currdir)
    {}

    But this is *not* (obviously).
    >>> remotes = get_remotes('https://github.com/lunarengineer-bot/lunar-engineering-managed-knowledge-base')
    >>> type(remotes)
    <class 'dict'>
    >>> len(remotes)
    4
    >>> set(type(_) for _ in remotes.keys())
    {<class 'str'>}
    >>> set(type(_) for _ in remotes.values())
    {<class 'str'>}
    >>> for k, v in remotes.items():
    ...     print(k, ':', v)
    HEAD : decac5b6a213eb3ad36bc1720e7b3d1efa39dd2e
    refs/heads/babygitr_managed_branch : b0ce1364b0656b332c1a693cc8b9afa2a64d018e
    refs/heads/knowledge_base : ffa775fefd65d42813f9b34100277933c406782c
    refs/heads/main : decac5b6a213eb3ad36bc1720e7b3d1efa39dd2e
    """
    # Get the remotes if they exist.
    remote_string = f"git ls-remote {url}"
    _ = subprocess.run(
        [remote_string], shell=True, capture_output=True
    )
    if not _.returncode == 0 and not allow_failure:
        # We didn't succeed and want to do that loudly.
        raise b_e.BabyGitrConnectionError(
            f"""Unable to connect to {url}:

        I am unable to `git ls-remote` on your git repository, which
        means that I either can't *see* your git repository, or you
        have not set up authentication appropriately.

        Are you on a closed network? Is there a typo in your URL?
        Do I have access?

        Command Run
        -----------\n{remote_string}

        STDERR
        ------\n{_.stderr.decode()}
        """
        )
    if (not _.returncode == 0 and allow_failure) or not len(_.stdout):
        # This handles empty projects and allowing failure.
        return {}
    # Parse the CLI.
    remote_list = [_.split('\t') for _ in _.stdout.decode().split('\n') if _]
    remote_dict = {_[1]: _[0] for _ in remote_list}
    return remote_dict


def _standardized_validated_path(url: str) -> str:
    """Return standardized and guaranteed to exist path.

    This will take a path you throw at it which represents a git
    repository; this will validate that git is able to *see* your
    remote and will return the string. This is useful in Schema
    validation.

    Parameters
    ----------

    url: str
        An arbitrary path (internet or local) representing a git repository.

    Returns
    -------
    url: str
        That url potentially updated with a scheme prefix.

    Examples
    --------
    >>> _standardized_validated_path('https://github.com/lunarengineer-bot/lunar-engineering-managed-knowledge-base')
    'https://github.com/lunarengineer-bot/lunar-engineering-managed-knowledge-base'
    >>> _standardized_validated_path('git@github.com:lunarengineer-bot/lunar-engineering-managed-knowledge-base.git')
    'git@github.com:lunarengineer-bot/lunar-engineering-managed-knowledge-base.git'
    """
    # This is way easier than any other way I tried.
    if url.startswith("git"):
        test_url = "https://" + url.replace("git@", "").replace(":", "/", 1)
        logger.warning("BabyGitr: I coerced your url from git@ to http for testing.")
    else:
        test_url = url
    get_remotes(test_url)
    return url


####################################################################
#                     Basic Git Functionality                      #
# ---------------------------------------------------------------- #
# These few functions implement some basic patterns and build on   #
#   one another.                                                   #
####################################################################
def add_changes(
    change_globs: str = '.',
    author_string: str = __BABYGITR_MAIL__,
    message: str = "chore(babygitr): housekeeping",
) -> bool:
    """Use a change in status to trigger a potentially targeted commit.

    This checks `git status` to determine if there are any files
    which have changed since the last time a 'save' operation was
    run.

    If any changes have been made any which mach 'change_globs'
    glob pattern (e.g. 'src*', 'src tests/specifictest') their
    changes will be tracked via a commit with a formatted message;
    by default all changes are tracked, this may be changed via
    `change_globs`.

    This assumes it is being run in a git directory.

    Parameters
    ----------
    change_globs: str = '.'
        This is a space separated string set of globs
        i.e 'docs src/whatevs' or '.' or whatever.
        Anything that matches that pattern will be added.
    author_string: str = __BABYGITR_MAIL__
        This is a way to change the author associated with the
        commit.
    message: str = "chore(babygitr): housekeeping"
        This is a way to add formatted information to commits.

    Returns
    -------
    status: bool = True
    """
    # This returns messages in a standard parseable shell output format
    _ = subprocess.run(
        ["git status --short"], shell=True, check=True, capture_output=True
    )
    if not _.stdout:  # No changes
        return True  # All quiet on the Western front.

    # This adds change_globs folders. This works with str, iterable str, and such,
    # Check into the documentation for git add and then pass whatever you want into it,
    # just make sure it's been 'stringified'.
    _ = subprocess.run(
        [f"git add {change_globs}"], shell=True, check=True, capture_output=True
    )
    # Now I'm going to commit them all.
    commit_str = f"git commit -m '{message}'"
    # And I'm going to own it.
    commit_str += f" --author '{author_string}'"
    _ = subprocess.run(
        [commit_str], shell=True, check=True, capture_output=True
    )
    return True


def new_repo(
    local_path: str,
    change_globs: str = '.',
    author_string: str = __BABYGITR_MAIL__,
    default_branch: str = __BABYGITR_BRANCH__
) -> bool:
    """Create a new local repository, with a default branch, from desired files.

    Parameters
    ----------
    local_path: str
        This is the filepath for the git repository.
    change_globs: str = '.'
        This allows for specifying 'only save these files'.
    author_string: str = __BABYGITR_MAIL__
        This is a way to change the author associated with the
        commit.
    default_branch: str = __BABYGITR_BRANCH__
        This is the default branch to instantiate.

    Returns
    -------
    status: bool = True
    """
    # Start her up
    _ = subprocess.run(
        [f"git init {local_path}"], shell=True, check=True, capture_output=True
    )
    os.chdir(local_path)
    # Set the default branch
    _ = subprocess.run(
        [f"git config --global init.defaultBranch {default_branch}"], shell=True, check=True, capture_output=True
    )
    # Rename the current branch
    _ = subprocess.run(
        [f"git branch -m {default_branch}"], shell=True, check=True, capture_output=True
    )
    # Then go ahead and track everything at the desired paths.
    add_changes(
        change_globs=change_globs,
        author_string=author_string,
        message="chore(babygitr): initial",
    )
    return True


# def init_repo(
#     local_path: str = ".",
#     branch: str = "knowledge_base",
#     remote_path: Optional[str] = None,
#     change_globs: str = '.',
#     author_string: str = __BABYGITR_MAIL__,
#     default_branch: str = __BABYGITR_BRANCH__
# ) -> bool:
#     """Create a local repository.

#     This does one of two things; if it's given a `remote_path` then
#     it will attempt to clone that repository down, else it will create
#     an empty repository at the local location.

#     This will set the working branch to `branch` (knowledge_base by
#     default.)

#     This will also explode gently, letting you know if issues
#     popped up.

#     What did I learn while doing this? pygit2 doesn't have good high
#     level documentation.

#     Parameters
#     ----------
#     local_path: str
#         The local repository path.
#     branch: str
#         An optional branch to checkout to.
#     remote_path: Optional[str] = None
#         An optional remote url.

#     Returns
#     -------
#     repo_status: bool
#         Whether or not the operation concluded successfully.

#     Examples
#     --------
#     This is a simple example showcasing how to work with a local
#     directory.

#     >>> from tempfile import TemporaryDirectory
#     >>> with TemporaryDirectory() as t:
#     ...     local_repo = init_repo(f'{t}/.git', branch='test')
#     ...     type(local_repo)
#     <class 'bool'>

#     This is an example showcasing how to use with a 'local remote'
#     >>> with TemporaryDirectory() as t:
#     ...     remote_repo = init_repo(f'{t}/remote/.git', branch='test')
#     ...     local_repo = init_repo(
#     ...         local_path=f'{t}/local/.git',
#     ...         remote_path=f'{t}/remote/.git',
#     ...         branch='main',
#     ...     )
#     """
#     if remote_path is not None:
#         # Down this leg we have a remote to test.
#         # 1. Does this remote exist? If no explode.
#         # 2. Is there already stuff at the repo local location? If yes:
#         # 2.a. Is it the remote that you asked me to clone? Yes whatevs no explode.
#         ############################
#         # Testing Remote Existence #
#         ############################
#         # Derive a validated remote path. This is guaranteed to exist as a git project.
#         remote_path = Schema(Use(_standardized_validated_path)).validate(remote_path)
#         # Now list the remotes there.
#         remotes = _get_remotes(remote_path)
#         # And unpack the standard out.
#         # This is a list of tuples of (hash, str)
#         # We'll be reusing this.
        
#         #############################
#         # Investigating Local Files #
#         #############################
#         # Are there local files?
#         # if os.path.exists(local_path):  # Yep!
#         #     # Is there a repo there?
#         #     locals = _get_remotes(local_path, allow_failure=True)
#         #     if locals != "FAILURE":  # A repo exists at this location.
#         #         # If a repo exists here we want to make sure that our
#         #         #  local work, and the remote work, have an overlapping
#         #         #  set of branches.
#         #         repo_exists
#         #     else:  # No, these files are not a git project.
#         #         # 
#         # else:  # Nope!
#         #     straightgitclone
#         # At this point it is a folder that exists. If there's already a repo.
#         # TODO: This one prevents a re-clone.d\
#         # The only case here is *if this is already a clone it will have remotes*.
#         # This validates the repo exists and can be connected to.
#         # This makes the folder if it doesn't exist.
#         # This clones down a git project.
#         # This checks the branch out if it exists, else it creates it once cloned.
#         # What are the cases?
#         # Branch can be accessed.
#         # Branch cannot be accessed.
#         # if stdout == 'FAILURE':  # Branch cannot exist.
#         #     raise b_e.BabyGitrConnectionError(f"""

#         #     I could not list remotes at this url.
#         #     I might not be able to see it, it might not be a git repo.
#         #     Maybe something else?
#         #     Dunno man, you should send this to the developers if you think it's important.

#         #     URL: {remote_path}
#         #     """)
#         # elif f'refs/heads/{branch}' in stdout:  # Branch exists
#         #     log_msg = """Your remote project exists and my managed branch already exists.
#         #     I will just clone that."""
#         #     logger.info(log_msg)
#         #     _ = subprocess.run(
#         #         [f"git clone {remote_path} --branch {branch} {local_path}"], shell=True, check=True, capture_output=True
#         #     )
#         # else:  # Branch does not exist.
#         #     log_msg = """Your remote project exists but my managed branch does not exist.
#         #     I will clone and commit my branch."""
#         #     _ = subprocess.run(
#         #         [f"git clone {remote_path} {local_path}"], shell=True, check=True, capture_output=True
#         #     )
#         # logger.info('Done')
#         raise Exception(f"What does this look like? {_}")
#         logger.info(f"Connected to remote: {remote_path}")
#     else:
#         # Down this leg we have no remote, so we just make
#         #   a blank project.
#         logger.warn("No remote assigned. I'll still babysit your work!")
#     # Then make a new repo, or not! This works the same either way.
#     new_repo(
#         local_path=local_path,
#         change_globs=change_globs,
#         author_string=author_string,
#         default_branch=default_branch,
#     )
#     return True


# def set_remote(
#     local_repo: pygit2.Repository,
#     remote_url: str,
#     remote_name: str = "origin",
# ) -> None:
#     """Set the remote URL for the repository.

#     This sets the connection to the remote. If it cannot connect to
#     the remote then it will die a tragic death.

#     Tl;Dr: `git remote add origin https://github.com/<user-name>/<repo-name>.git`

#     Parameters
#     ----------
#     local_repo: pygit2.Repository
#         This is a pygit2 repository instance.
#     remote_url: str
#         This is the path to the remote.
#     remote_name: str = 'origin'
#         This is the name of the remote.
#     """
#     try:
#         origin = local_repo.remotes[remote_name]
#     except KeyError:
#         origin = None
#     if origin is not None:
#         local_repo.remotes.set_url(remote_name, remote_url)
#     else:
#         origin = local_repo.remotes.create(
#             remote_name,
#             url=remote_url,
#         )


# __AUTH_STR__ = """

# Currently Implemented Auth Methods
# ----------------------------------
# Please select from the sets below and pass a full set of parameters.

# * Username and password {'username', 'password'}
# * GPG {'username', 'pubkey', 'privkey'}
# * GPG {'username', 'pubkey', 'privkey', 'passphrase'}
# """


# def create_auth_callback(auth_config: Dict[str, str]) -> pygit2.RemoteCallbacks:
#     """Return an authentication callback.

#     This returns a callable object that may be used in pygit2
#     authentication.

#     Parameters
#     ----------
#     auth_config: Dict[str, str]
#         This is a dictionary with either the information for using
#         either username/password or GPG.

#     Examples
#     --------
#     Make a callable that can return a userpass.
#     >>> cred_callable = create_auth_callback(dict(username='steve', password='steve!'))
#     >>> type(cred_callable)
#     <class 'pygit2.callbacks.RemoteCallbacks'>

#     Make a callable that can return a GPG keypair.
#     >>> cred_callable = create_auth_callback(
#     ...     dict(
#     ...         username='steve',
#     ...         pubkey='~/.ssh/stupidkey.pub',
#     ...         privkey='~/.ssh/stupidkey',
#     ...     )
#     ... )
#     >>> type(cred_callable)
#     <class 'pygit2.callbacks.RemoteCallbacks'>

#     These are the currently implemented authentication methods.
#     >>> print(__AUTH_STR__)
#     <BLANKLINE>
#     <BLANKLINE>
#     Currently Implemented Auth Methods
#     ----------------------------------
#     Please select from the sets below and pass a full set of parameters.
#     <BLANKLINE>
#     * Username and password {'username', 'password'}
#     * GPG {'username', 'pubkey', 'privkey'}
#     * GPG {'username', 'pubkey', 'privkey', 'passphrase'}
#     <BLANKLINE>
#     """
#     _auth_config = auth_config.copy()
#     userpass = set(_auth_config) == {"username", "password"}
#     keypair = set(_auth_config) == {
#         "username",
#         "pubkey",
#         "privkey",
#         "passphrase",
#     } or set(_auth_config) == {"username", "pubkey", "privkey"}
#     if userpass:
#         auth_func = pygit2.UserPass(**_auth_config)
#     elif keypair:
#         if "passphrase" not in _auth_config:
#             _auth_config["passphrase"] = ""  # nosec - This is not confidential...
#         auth_func = pygit2.Keypair(**_auth_config)
#     else:
#         raise NotImplementedError()
#     return pygit2.RemoteCallbacks(credentials=auth_func)


# def sync_repo(
#     local_repo: pygit2.Repository,
#     author: pygit2.Signature,
#     committer: pygit2.Signature,
#     branch: str,
#     auth_config: Optional[Dict[str, str]],
# ) -> None:
#     """Sync files, potentially with the remote repository.

#     This polls the upstream branch for new information and pushes
#     changes.

#     Parameters
#     ----------
#     local_repo: pygit2.Repository
#         This is the local repo.
#     author: pygit2.Signature
#         The signature for the author.
#     committer: pygit2.Signature
#         The signature for the committer.
#     branch: str
#         The branch to commit the latest ref for.
#     auth_config: Dict[str, str]
#         This is a dictionary with either the information for using
#         either username/password or GPG.
#     """
#     # Go ahead and add all the tracked changes.
#     _add_changes(
#         repo=local_repo,
#         author=author,
#         committer=committer,
#         ref=local_repo.head.name,
#         message="chore(babygitr): sync",
#         parents=[local_repo.head.target],
#     )
#     # If there's no auth config then we're done!
#     if auth_config is None:
#         return None
#     # Test the connection
#     local_repo.remotes["origin"].connect(
#         callbacks=create_auth_callback(auth_config=auth_config)
#     )
#     # Push the desired branch upstream
#     try:
#         local_repo.remotes["origin"].push(
#             [local_repo.lookup_reference_dwim(branch).name],
#             callbacks=create_auth_callback(auth_config=auth_config),
#         )
#     except Exception as e:
#         raise Exception(f"{local_repo.remotes['origin']}") from e
