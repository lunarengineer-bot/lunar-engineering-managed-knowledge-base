"""Holds the BabyGitr object.

Default Configuration
```python
>>> import json
>>> from babygitr import default_configuration
>>> print(json.dumps(default_configuration.validate({}), sort_keys = True, indent=4))
{
    "auth_configuration": {
        "password": "secret",
        "username": "Kilroy"
    },
    "branch_name": "babygitr_managed_branch",
    "local_folder": ".",
    "remote_url": "",
    "sync_configuration": {
        "dir": ".",
        "observation_frequency": 30,
        "sync_frequency": 120
    }
}

>>> test = {'sync_configuration': {'dir': '.'}}
>>> print(json.dumps(default_configuration.validate(test), sort_keys = True, indent=4))
{
    "auth_configuration": {
        "password": "secret",
        "username": "Kilroy"
    },
    "branch_name": "babygitr_managed_branch",
    "local_folder": ".",
    "remote_url": "",
    "sync_configuration": {
        "dir": ".",
        "observation_frequency": 30,
        "sync_frequency": 120
    }
}

```

"""
import time
import yaml
from babygitr.repowatcher import (
    init_repo,
    set_remote,
    create_auth_callback
)
from schema import Optional as SchemaOptional, Schema
from typing import Dict, List, Optional, Union


_config_type = Dict[str, Union[str, int, Dict[str, List[str]]]]


default_configuration = Schema(
    {
        SchemaOptional("local_folder", default="."): str,
        SchemaOptional("remote_url", default=""): str,
        SchemaOptional("branch_name", default="babygitr_managed_branch"): str,
        SchemaOptional(
            "auth_configuration",
            default=lambda: {
                'username': 'Kilroy',
                'password': 'secret'
            }
        ): {
            # This
            SchemaOptional("username"): str,
            # with either
            SchemaOptional("public_key"): str,
            SchemaOptional("private_key"): str,
            SchemaOptional("passphrase"): str,
            # or
            SchemaOptional("password"): str,
        },
        SchemaOptional(
            "sync_configuration",
            default=lambda: {
                'dir': '.',
                "observation_frequency": 30,
                'sync_frequency': 120,
                "ignore": None
            }
        ): {
            SchemaOptional("dir", default='.'): str,
            SchemaOptional("observation_frequency", default=30): int,
            SchemaOptional("sync_frequency", default=120): int,
            SchemaOptional("ignore", default=None): [str],
        }
    }
)


class BabyGitr:
    """Holds persistent state for project.

    This class manages a persistent Git repository.

    Parameters
    ----------
    config: _config_type
        A configuration object for BabyGitr.
    """
    def __init__(self, config: Optional[Union[str, _config_type]] = None) -> None:
        ############################################################
        #                       Validate Config                    #
        # -------------------------------------------------------- #
        # This reads in and validates a configuration.             #
        ############################################################
        """Spin up a baby-gitr."""
        if config is None:
            config = {}
        if isinstance(config, str):
            with open(config, "r") as yaml_file:
                config = yaml.safe_load(yaml_file.read())
        self._config = default_configuration.validate(config)
        ############################################################
        #                         Initial Setup                    #
        # -------------------------------------------------------- #
        # Here we're establishing that we can, in fact, connect to #
        #   the git repository and push and pull from the remote.  #
        # If we can't do that, we're going to throw some helpful   #
        #   (ish) errors messages and raise a new error.           #
        ############################################################
        self._repository = init_repo(
            local_path=self._config["local_folder"],
            remote_path=self._config["remote_url"],
            branch=self._config["branch_name"],
        )
        set_remote(
            local_repo=self._repository,
            remote_name=self._config["remote_name"],
            remote_url=self._config["branch_name"]
        )
        self._auth_callable = create_auth_callback(
            local_repo=self._repository
        )
        # Is there any initial setup that needs to be done in terms of files?
        self.sync()

    def generate_config(self):
        """Dump out a default configuration."""
        raise NotImplementedError

    def sync(self):
        raise NotImplementedError


def parse_cli():
    raise NotImplementedError


def main():
    """Runs the baby-gitting loop"""
    ################################################################
    #                          Parse Input                         #
    # ------------------------------------------------------------ #
    # Here we're observing the input from the command line. This   #
    #   information will be reused later.                          #
    ################################################################
    application_configuration: Union[str, Dict[str, Union[str, int, Dict[str, List[str]]]], None] = parse_cli()
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
    sync_t = application_configuration['sync_configuration']['sync_frequency']
    observe_t = application_configuration['sync_configuration']['observation_frequency']
    while True:
        _t = min(sync_t, observe_t)
        time.sleep(_t)
        if _t == sync_t:
            repo_watcher.sync()
            observe_t -= _t
            sync_t = application_configuration['sync_configuration']['sync_frequency']
        elif _t == observe_t:
            repo_watcher.sync()
            sync_t -= _t
            observe_t = application_configuration['sync_configuration']['observation_t_frequency']


if __name__ == "__main__":
    main()
