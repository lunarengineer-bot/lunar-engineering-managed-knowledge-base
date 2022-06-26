# Managed Knowledge Base Connection

This will grow into something more formalized over time, but this is currently a containerized data baby-sitter.

If provided access to a git repository this process will maintain a branch within that repository and will attempt to maintain continuity.

If this process is unable to reconcile the upstream and the local data the local data is discarded and replaced with the upstream.

Looking to get an understanding of how and what this thing is doing?

Open this with VSCode as a development container and the dev documents will get you up and running!

Running tox will run the testing suite that validates the code is doing what it's doing *and* publishes documentation!

Digging into the tests at the highest level will show an integration test which is a pretty good example of how to use this.

Do you want to see the test output in an easy to consume way? Why not just start the dev container and navigate to localhost:8090 where a local web server should be running. If things have been dumped out there, you will be able to find them!

So, to cut to the chase, to run the testing suite try `tox -p`. You can be a lot more targeted, but that will run the full test suite.


TODO: Finish test setup
TODO: Measure test time and output

TODO: validate pytest dumping coverage into .reports
TODO: Get authors into pyproject.toml
TODO: Change tox call to default to but allow replacement of target
TODO: Publish to flit

TODO: Add documentation for regolith image - https://solarsystem.nasa.gov/system/resources/detail_files/1801_PIA15822_hires.jpg