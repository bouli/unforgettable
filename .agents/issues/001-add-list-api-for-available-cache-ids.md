## What to build

Add a library API path for listing available cache IDs from an `unforgettable`
cache instance. Users should be able to call `list()` on an instance and
receive the user-created cache IDs recorded for that instance's cache folder.

The behavior should fit the existing file-backed cache model: listing should
work for new cache folders, persistent cache folders shared across instances,
overwritten cache entries, custom cache file extensions, and cache IDs that
contain spaces or punctuation.

## Acceptance criteria

- [x] A cache instance exposes a `list()` method that returns user-created cache IDs as structured Python data.
- [x] A new or empty cache folder returns an empty list rather than internal cache index bookkeeping.
- [x] Cache IDs created with `set()` appear in `list()` results and can still be retrieved with `get()`.
- [x] Repeated `set()` calls for the same cache ID do not create duplicate listed IDs.
- [x] Cache IDs persist in `list()` results across instances that use the same cache folder.
- [x] Listing works independently of the configured cache file extension.
- [x] Public documentation describes the new `list()` API.
- [x] Tests cover the external listing behavior without asserting private parsing details.

## Blocked by

None - can start immediately
