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
- `.agents/issues/003-add-cli-cache-mutation-commands.md`
  - Added CLI `set`, `get`, and `clean` commands backed by the existing cache class.
  - Defined missing cache IDs for CLI `get` as exit code `1` with a stderr message.
  - Documented CLI cache mutation and retrieval usage in `README.md`.
  - Covered successful CLI set, get, clean, missing get, and invalid set usage with subprocess tests.
- `.agents/issues/004-add-default-cli-cache-folder.md`
  - Added `.unforgettable-memory` as the CLI `--cache-folder` default.
  - Created the default folder automatically when omitted so CLI commands can run from a clean working directory.
  - Preserved explicit `--cache-folder` override behavior.
  - Documented the default cache folder workflow in `README.md`.
  - Covered default-folder use, explicit-folder override, and help text with subprocess tests.
- `.agents/issues/005-prompt-before-creating-missing-cli-cache-folder.md`
  - Added a confirmation prompt before creating a missing explicitly selected CLI cache folder.
  - Preserved automatic creation for the default `.unforgettable-memory` folder.
  - Exits non-zero without creating the folder when the prompt is declined or receives no input.
  - Documented the missing explicit folder prompt in `README.md`.
  - Covered confirmed, declined, and no-input prompt behavior with subprocess tests.
