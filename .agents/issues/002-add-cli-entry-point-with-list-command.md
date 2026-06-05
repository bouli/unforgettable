## What to build

Expose Unforgettable as an installable command-line tool with a first complete
CLI path for listing cached IDs. After installation, users should be able to
run an `unforgettable` command, choose a cache folder, and list available cache
IDs using the same behavior as the library API.

The CLI should be a thin adapter over the cache class rather than a separate
implementation of cache index behavior. Listing output should be predictable
for terminal users and shell automation.

## Acceptance criteria

- [x] Installing the package exposes an `unforgettable` executable through the package metadata.
- [x] The CLI provides discoverable help text for the command and list operation.
- [x] The CLI accepts a cache folder option for listing persistent cache state.
- [x] The CLI list operation prints available cache IDs in a stable, script-friendly format.
- [x] The CLI list operation uses the library `list()` behavior rather than duplicating cache index logic.
- [x] The CLI list operation handles an empty cache folder cleanly.
- [x] Public documentation includes command-line usage examples for listing cache IDs.
- [x] Tests invoke the CLI through a user-facing command path and cover the list command.

## Blocked by

- `.agents/issues/001-add-list-api-for-available-cache-ids.md`
