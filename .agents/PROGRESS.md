## Progress

### Completed

- `.agents/issues/001-add-list-api-for-available-cache-ids.md`
  - Added `unforgettable.list()` to return user-created cache IDs from the cache index.
  - Covered empty folders, set/get integration, overwritten IDs, persistent folders, custom extensions, and IDs with spaces and punctuation.
  - Documented the `list()` API in `README.md`.
- `.agents/issues/002-add-cli-entry-point-with-list-command.md`
  - Added an `unforgettable` console script entry point backed by `unforgettable.cli:main`.
  - Added `python -m unforgettable` support and a `list` command with `--cache-folder`.
  - Printed listed cache IDs one per line and no output for empty cache folders.
  - Documented the CLI list workflow in `README.md`.
  - Covered CLI help, selected-folder listing, and empty-folder behavior with subprocess tests.
