"""Holds the BabyGitr object.

Default Configuration
```python
>>> import json
>>> from babygitr import default_configuration
>>> print(json.dumps(default_configuration.validate({}), sort_keys = True, indent=4))
{
    "branch_name": "babygitr_managed_branch",
    "local_folder": ".",
    "observation_frequency": 30,
    "remote_url": "",
    "sync_configuration": {
        "keep_local": []
    },
    "sync_frequency": 30,
    "upstream_branch": ""
}

```

"""
import time
import yaml
from babygitr.repowatcher import (
    init_repo,
    set_remote,
    set_upstream_branch,
    # authenticate_with_repo
)
from schema import Optional as SchemaOptional, Schema
from typing import Dict, List, Optional, Union


_config_type = Dict[
    str, Union[
        str,
        int,
        Dict[
            str, List[str]
        ]
    ]
]


default_configuration = Schema({
    SchemaOptional('local_folder', default='.'): str,
    SchemaOptional('remote_url', default=''): str,
    SchemaOptional('branch_name', default='babygitr_managed_branch'): str,
    SchemaOptional('upstream_branch', default=''): str,
    SchemaOptional('observation_frequency', default=30): int,
    SchemaOptional('sync_frequency', default=30): int,
    SchemaOptional('sync_configuration', default=lambda: Schema(
        {
            SchemaOptional('keep_local', default=[]): [str],
        }
    ).validate({})): Dict[str, List[str]]
})


class BabyGitr:
    """Holds persistent state for project.

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
            with open(config, 'r') as yaml_file:
                config = yaml.safe_load(yaml_file.readlines())
        self._config = default_configuration.validate(config)
        ############################################################
        #                         Initial Setup                    #
        # -------------------------------------------------------- #
        # Here we're establishing that we can, in fact, connect to #
        #   the git repository and push and pull from the remote.  #
        # If we can't do that, we're going to throw some helpful   #
        #   (ish) errors messages and raise a new error.           #
        ############################################################
        init_repo(
            local_path=self._config['local_folder'],
            remote_path=self._config['remote_url'],
            branch=self._config['branch_name']
        )
        self._remote = set_remote(self._config['branch_name'])
        set_upstream_branch(self._config['upstream_branch'])
        # authenticate_with_repo()

    def generate_config():
        """Dump out a default configuration."""
        raise NotImplementedError

    def sync():
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
