# Managed Knowledge Base Connection

This will grow into something more formalized over time, but this is currently a containerized data baby-sitter.

This provides basic API to:

* Create and maintain a local repository with a specific named branch.
* Link that to a remote repository.
* Modify the authentication method.
* Sync the local to the remote; if this process is unable to reconcile the upstream and the local data the local data is discarded and replaced with the upstream.

## Why Would You Do This? What Purpose Is There?

Come have a long conversation with me where I ramble about heirarchical models and storing trajectories, about how git is the perfect vehicle for this data, and about how intertwined data and code versioning enables amazing patterns.

Recording the state of an experiment at regular intervals (or tracking the work of a lazy scientist) has the benefit of formally sharing the work.

## Development

Looking to get an understanding of how and what this thing is doing?

Open this with VSCode as a development container and the dev documents will get you up and running!

Running tox will run the testing suite that validates the code is doing what it's doing *and* publishes documentation!

It will spin up a docker container in the background which is used as a remote git server.

Digging into the tests in test_babygitr at the highest level will show an integration test which is a pretty good example of how to use this.

Do you want to see the test output in an easy to consume way? Why not just start the dev container and navigate to localhost:8090 where a local web server should be running. If things have been dumped out there, you will be able to find them! (If the server isn't started for some reason you can just run `python3 -m http.server 8090 --directory=/project/reports &` after running the tests.)

So, to cut to the chase, to run the testing suite try `tox -p`. You can be a lot more targeted, but that will run the full test suite.


TODO: 
[x] RepoWatcher authentication
[x] RepoWatcher Sync local and remote
[ ] BabyGitr stateful object
[ ] Main Loop
[ ] Validate testing suite fully passes
[ ] Ensure documentation is sufficient to show usage
[ ] Measure test time and output
[ ] Ensure tox call to default to but allow replacement of target
[ ] Publish to a package repository
[ ] Publish Docker image to DockerHub (or GitHub container reg?).
[ ] Add documentation for regolith image - https://solarsystem.nasa.gov/system/resources/detail_files/1801_PIA15822_hires.jpg