## What to build

Extend the Unforgettable CLI with cache mutation and retrieval commands for
the existing library behavior. Terminal users should be able to store content
under a cache ID, retrieve content by cache ID, and clean a selected cache
folder without writing Python code.

The commands should reuse the same cache class used by the Python API and
should provide clear output and exit behavior for shell automation.

## Acceptance criteria

- [x] The CLI can store text content under a user-provided cache ID in a selected cache folder.
- [x] The CLI can retrieve content by cache ID from a selected cache folder.
- [x] The CLI can clean the selected cache folder.
- [x] Missing cache entries and invalid usage produce useful messages and non-zero exit codes where appropriate.
- [x] CLI commands reuse existing library behavior rather than duplicating cache storage logic.
- [x] Public documentation includes command-line usage examples for storing, retrieving, and cleaning cached values.
- [x] Tests cover successful CLI set, get, and clean workflows.
- [x] Tests cover defined CLI failure behavior.

## Blocked by

- `.agents/issues/002-add-cli-entry-point-with-list-command.md`
