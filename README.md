# Unforgettable - v0.4.0

Unforgettable is a tiny file-backed cache for Python code that repeats small
pieces of work. It is useful for local scripts, notebooks, tests, prototypes,
and automation where a value is expensive or annoying to compute more than
once.

The library has no runtime dependencies and exposes one main class:
`unforgettable`.

## Installation

Install with `uv`:

```shell
uv add unforgettable
```

Or with `pip`:

```shell
pip install unforgettable
```

Unforgettable requires Python 3.11 or newer.

## Quick Start

```python
from unforgettable import unforgettable

cache = unforgettable()

cached_value = cache.get(cache_id="expensive-operation")
if cached_value is None:
    cached_value = "computed result"
    cache.set(content=cached_value, cache_id="expensive-operation")

print(cached_value)
```

`get()` returns the cached value when it exists. If there is no value for that
`cache_id`, it returns `None`.

Use `list()` to inspect the cache IDs currently available in a cache folder.

```python
from unforgettable import unforgettable

cache = unforgettable()
cache.set(content="computed result", cache_id="expensive-operation")

assert cache.list() == ["expensive-operation"]
```

## Cache Text

```python
from unforgettable import unforgettable

cache = unforgettable()

cache.set(content="hello", cache_id="greeting")

assert cache.get(cache_id="greeting") == "hello"
```

## Cache Bytes

```python
from unforgettable import unforgettable

cache = unforgettable()

content = b"\x80\x81cached bytes"
cache.set(content=content, cache_id="binary-value")

assert cache.get(cache_id="binary-value") == content
```

## Persistent Cache Folder

By default, each cache instance creates its own temporary directory with
`tempfile`. Use `cache_folder` when you want cached values to persist across
Python process runs.

```python
import os

from unforgettable import unforgettable

cache_dir = os.environ.get("UNFORGETTABLE_CACHE_DIR", ".unforgettable-cache")
cache = unforgettable(cache_folder=cache_dir)

cache.set(content="saved between runs", cache_id="stable-key")
```

Creating a new cache instance with the same folder can read values written by
the previous instance.

```python
from unforgettable import unforgettable

first_cache = unforgettable(cache_folder=".unforgettable-cache")
first_cache.set(content="persisted", cache_id="example")

second_cache = unforgettable(cache_folder=".unforgettable-cache")
assert second_cache.get(cache_id="example") == "persisted"
```

## Command Line

Installing the package exposes an `unforgettable` command.

CLI commands use `.unforgettable-memory` in the current working directory by
default, so you can run commands without passing `--cache-folder`:

```shell
unforgettable set greeting "hello"
unforgettable get greeting
```

Pass `--cache-folder` to use a different persistent cache folder:

```shell
unforgettable --cache-folder .unforgettable-cache list
```

When an explicitly selected cache folder does not exist, the CLI asks before
creating it. Answer `y` or `yes` to create the folder and continue; any other
answer exits without creating the folder or changing cache contents.

For unattended automation, choose the missing-folder policy explicitly:

```shell
unforgettable --cache-folder .unforgettable-cache --create-cache-folder set greeting "hello"
unforgettable --cache-folder .unforgettable-cache --no-create-cache-folder list
```

`--create-cache-folder` creates a missing explicitly selected folder without
reading stdin. `--no-create-cache-folder` exits with status code `1` without
creating the folder or changing cache contents. Prompts and errors are written
to stderr; command values are written to stdout.

The `list` command prints one cache ID per line and prints nothing when the
selected cache folder has no user-created entries.

Use `--output json` when an agent or script needs structured output:

```shell
unforgettable --cache-folder .unforgettable-cache --output json list
```

JSON `list` output has the stable shape `{"cache_ids": ["example"]}` and uses
`{"cache_ids": []}` for an empty cache folder. Cache IDs with spaces and
punctuation are preserved as JSON strings. Plain text remains the default.

Store text under a cache ID:

```shell
unforgettable --cache-folder .unforgettable-cache set greeting "hello"
```

Store text from stdin, including multiline or piped content:

```shell
printf 'first line\nsecond line\n' | unforgettable --cache-folder .unforgettable-cache set notes --stdin
```

Retrieve cached text:

```shell
unforgettable --cache-folder .unforgettable-cache get greeting
```

Retrieved text is written directly to stdout without labels or added trailing
newlines, so cached values can be piped into other tools.

With `--output json`, `get` emits a structured object containing the cache ID,
content, encoding marker, and metadata:

```shell
unforgettable --cache-folder .unforgettable-cache --output json get greeting
```

Text values use `encoding: "utf-8"` and place the text directly in `content`.
Binary values use `encoding: "base64"` and place base64-encoded bytes in
`content`, so JSON output remains parseable.

Export all cache entries as JSON:

```shell
unforgettable --cache-folder .unforgettable-cache export
```

The `export` command writes a JSON object to stdout with an `entries` array.
Each entry has the same shape as JSON `get`: `cache_id`, `content`, `encoding`,
and `metadata`. Empty cache folders export as `{"entries": []}`. Text and
multiline values use `encoding: "utf-8"`; binary values use
`encoding: "base64"` with base64-encoded content.

Import exported JSON from stdin:

```shell
unforgettable --cache-folder .unforgettable-cache import --stdin < memory.json
```

The `import --stdin` command upserts entries by cache ID and preserves unrelated
entries in the selected cache folder. It exits with status code `1` and writes a
stderr diagnostic for empty stdin, malformed JSON, or invalid import data.

Check whether a cache ID exists without retrieving content:

```shell
unforgettable --cache-folder .unforgettable-cache exists greeting
```

The `exists` command writes `true` or `false` in text mode. It exits with status
code `0` when the cache ID exists and status code `1` when it is missing.

Delete one cache ID without clearing the whole cache folder:

```shell
unforgettable --cache-folder .unforgettable-cache delete greeting
```

The `delete` command exits with status code `0` after removing an entry. It
exits with status code `1` and writes a diagnostic to stderr when the cache ID
is missing.

Inspect metadata for a cache ID before retrieving content:

```shell
unforgettable --cache-folder .unforgettable-cache info greeting
```

The `info` command prints readable metadata in text mode. With `--output json`,
it emits `cache_id`, `file_name`, `byte_size`, `content_type`, `created_at`,
and `updated_at`.

Clean the selected cache folder:

```shell
unforgettable --cache-folder .unforgettable-cache clean
```

`get` exits with status code `1` when the requested cache ID is missing.
`info` exits with status code `1` when the requested cache ID is missing.

## Local AI-Agent Tool Contract

Agents can discover and run Unforgettable without adding it to the current
project. Use `uvx` where that alias is available:

```shell
uvx unforgettable --help
uvx unforgettable --version
```

Use `uv tool run` as the portable equivalent:

```shell
uv tool run unforgettable --help
uv tool run unforgettable --version
```

Installed environments can use the console script or module execution:

```shell
unforgettable --help
python -m unforgettable --help
```

For compatibility-sensitive workflows, check `unforgettable --version` before
depending on a specific command contract.

The CLI uses stable process behavior suitable for unattended tools:

- Successful commands exit with status code `0`.
- Missing cache IDs for `get` exit with status code `1`.
- Missing cache IDs for `exists` exit with status code `1`.
- Missing cache IDs for `delete` exit with status code `1`.
- Missing cache IDs for `info` exit with status code `1`.
- Import failures exit with status code `1`.
- Rejected cache-folder creation exits with status code `1`.
- Invalid usage, such as missing required arguments, exits with status code `2`.
- Command values are written to stdout.
- Diagnostics, errors, and prompts are written to stderr.

By default, CLI commands use `.unforgettable-memory` in the current working
directory and create that default folder automatically. When `--cache-folder`
selects a missing explicit folder, the CLI prompts on stderr before creating
it. Agents should avoid prompts by choosing a policy:

```shell
unforgettable --cache-folder .agent-cache --create-cache-folder set run-id "started"
unforgettable --cache-folder .agent-cache --no-create-cache-folder list
```

Use `--create-cache-folder` to create the explicit folder without reading from
stdin. Use `--no-create-cache-folder` to fail with status code `1` if the
folder is missing.

Store multiline or piped content with `set --stdin`:

```shell
printf 'first line\nsecond line\n' \
  | unforgettable --cache-folder .agent-cache --create-cache-folder set notes --stdin
```

Retrieve content with `get`; the cached value is written directly to stdout
without labels or added trailing newlines:

```shell
unforgettable --cache-folder .agent-cache get notes
```

Use JSON `get` when an agent needs content and metadata in one parseable
response:

```shell
unforgettable --cache-folder .agent-cache --output json get notes
```

Check for a cache ID without retrieving content:

```shell
unforgettable --cache-folder .agent-cache exists notes
```

Text `exists` output is `true` or `false`. The command exits with status code
`0` when the cache ID exists and status code `1` when it is missing.

Delete one obsolete entry without erasing unrelated memory:

```shell
unforgettable --cache-folder .agent-cache delete notes
```

`delete` exits with status code `0` when it removes an entry. It exits with
status code `1` and writes a stderr diagnostic when the cache ID is missing.

Inspect metadata before retrieving content:

```shell
unforgettable --cache-folder .agent-cache info notes
```

`info` exits with status code `0` when metadata is available. It exits with
status code `1` and writes a stderr diagnostic when the cache ID is missing.

Plain text output is the default. Use `--output json` when a command supports
structured output:

```shell
unforgettable --cache-folder .agent-cache --output json list
unforgettable --cache-folder .agent-cache --output json get notes
unforgettable --cache-folder .agent-cache --output json exists notes
unforgettable --cache-folder .agent-cache --output json info notes
unforgettable --cache-folder .agent-cache export
unforgettable --cache-folder .agent-cache import --stdin < memory.json
```

The JSON `list` shape is stable:

```json
{"cache_ids": ["notes"]}
```

The JSON `exists` shape is stable:

```json
{"cache_id": "notes", "exists": true}
```

The JSON `get` shape is stable:

```json
{"cache_id": "notes", "content": "first line\nsecond line\n", "encoding": "utf-8", "metadata": {"byte_size": 23, "cache_id": "notes", "content_type": "text/plain", "created_at": "2026-06-06T00:00:00+00:00", "file_name": "1.cache", "updated_at": "2026-06-06T00:00:00+00:00"}}
```

Binary content in JSON `get` output uses base64:

```json
{"cache_id": "binary", "content": "gIFjYWNoZWQgYnl0ZXM=", "encoding": "base64", "metadata": {"byte_size": 14, "cache_id": "binary", "content_type": "application/octet-stream", "created_at": "2026-06-06T00:00:00+00:00", "file_name": "1.cache", "updated_at": "2026-06-06T00:00:00+00:00"}}
```

The JSON `export` shape is stable:

```json
{"entries": [{"cache_id": "notes", "content": "first line\nsecond line\n", "encoding": "utf-8", "metadata": {"byte_size": 23, "cache_id": "notes", "content_type": "text/plain", "created_at": "2026-06-06T00:00:00+00:00", "file_name": "1.cache", "updated_at": "2026-06-06T00:00:00+00:00"}}]}
```

Empty cache folders export as:

```json
{"entries": []}
```

The `import --stdin` command accepts the same JSON shape produced by `export`.
It upserts matching cache IDs, keeps entries that are not present in the import
bundle, and rejects malformed or invalid input before changing existing memory
where practical.

The JSON `info` shape is stable:

```json
{"byte_size": 12, "cache_id": "notes", "content_type": "text/plain", "created_at": "2026-06-06T00:00:00+00:00", "file_name": "1.cache", "updated_at": "2026-06-06T00:00:00+00:00"}
```

Existing cache folders that only have the legacy index and content files remain
readable. When no manifest exists, `info` derives byte size, content type, and
timestamps from the stored content file.

## Custom Cache File Extension

Cache content files use the `cache` extension by default. You can choose a
different extension when creating the cache instance.

```python
from unforgettable import unforgettable

cache = unforgettable(
    cache_folder=".unforgettable-cache",
    cache_files_extension="txt",
)

cache.set(content="inspectable text", cache_id="example")
```

## Cleaning A Cache

Call `clean()` on a cache instance to remove the files in that instance's cache
folder.

```python
from unforgettable import unforgettable

cache = unforgettable(cache_folder=".unforgettable-cache")
cache.set(content="temporary", cache_id="example")

cache.clean()
```

## HTTP Request Example

This example caches successful HTTP responses by URL. Failed requests are not
cached.

```python
import requests

from unforgettable import unforgettable

cache = unforgettable(cache_folder=".request-cache")


def requests_get(url: str) -> bytes | None:
    cached_response = cache.get(cache_id=url)
    if cached_response is not None:
        return cached_response

    response = requests.get(url=url, timeout=5)
    if response.status_code != 200:
        return None

    cache.set(content=response.content, cache_id=url)
    return response.content


url = "https://github.com/bouli/unforgettable"
first_response = requests_get(url)
second_response = requests_get(url)
```

## API Reference

### `unforgettable(cache_folder=None, cache_files_extension=None)`

Creates a cache instance.

- `cache_folder`: optional folder for cache files. When omitted, the instance
  uses a temporary directory.
- `cache_files_extension`: optional extension for stored cache content files.
  Defaults to `cache`.

### `cache.set(content, cache_id)`

Stores `content` under `cache_id`.

- `content` can be `str` or `bytes`.
- Calling `set()` again with the same `cache_id` overwrites the existing cached
  content.

### `cache.get(cache_id)`

Returns the cached value for `cache_id`.

- Returns `str` for text files.
- Returns `bytes` for binary files.
- Returns `None` when the cache entry does not exist.

### `cache.get_entry(cache_id)`

Returns a structured cached entry for `cache_id`.

- Returns a `dict` with `cache_id`, `content`, `encoding`, and `metadata`.
- Uses `encoding == "utf-8"` for text content.
- Uses `encoding == "base64"` for binary content.
- Returns `None` when the cache entry does not exist.

### `cache.export()`

Returns all cache entries in a JSON-compatible structure.

- Returns a `dict` with an `entries` list.
- Each entry has the same `cache_id`, `content`, `encoding`, and `metadata`
  shape as `cache.get_entry(cache_id)`.
- Returns `{"entries": []}` when no user cache entries exist.
- Derives metadata for legacy cache folders that do not have a manifest.

### `cache.import_entries(exported_entries)`

Imports entries from the JSON-compatible structure returned by `cache.export()`.

- Upserts entries by `cache_id`.
- Preserves unrelated cache entries.
- Supports `encoding == "utf-8"` text and `encoding == "base64"` binary
  content.
- Raises `ValueError` for invalid import data before changing memory where
  practical.

### `cache.exists(cache_id)`

Returns `True` when `cache_id` has a cached value and `False` when it does not.

### `cache.delete(cache_id)`

Removes the cached value for `cache_id`.

- Returns `True` when an entry was removed.
- Returns `False` when the cache entry does not exist.
- Preserves unrelated cache entries.

### `cache.info(cache_id)`

Returns metadata for `cache_id`.

- Returns a `dict` with `cache_id`, `file_name`, `byte_size`, `content_type`,
  `created_at`, and `updated_at`.
- Returns `None` when the cache entry does not exist.
- Derives metadata for legacy cache folders that do not have a manifest.

### `cache.list()`

Returns a `list[str]` containing user-created cache IDs available in the cache
folder.

- Returns an empty list when no user cache entries exist.
- Omits internal cache index bookkeeping.
- Preserves cache IDs with spaces and punctuation.

### `cache.clean()`

Removes files from the cache instance's folder.

## Development

Install dependencies:

```shell
uv sync --dev
```

Run tests:

```shell
make tests
```

Run the coverage report:

```shell
make report
```

Build the package:

```shell
make build
```

### Release Verification

Before publishing a release, run the local tests, build the wheel, and verify
the agent-facing execution paths:

- `uv run --dev pytest -q`
- `uv run --dev pytest -q tests/test_packaging.py`
- `uv build --wheel`
- `uv tool run unforgettable --help`
- `uv tool run unforgettable --version`
- `unforgettable --cache-folder .release-cache --create-cache-folder set notes "release check"`
- `unforgettable --cache-folder .release-cache --output json get notes`
- `unforgettable --cache-folder .release-cache --output json exists notes`
- `unforgettable --cache-folder .release-cache --output json info notes`
- `unforgettable --cache-folder .release-cache export`
- `unforgettable --cache-folder .release-cache import --stdin < memory.json`
- `unforgettable --cache-folder .release-cache delete notes`
- `uvx unforgettable --help` where the `uvx` alias is installed
- `uvx unforgettable --version` where the `uvx` alias is installed
- `unforgettable --help` after installing the built wheel
- `python -m unforgettable --help` after installing the built wheel
- `unforgettable --version` after installing the built wheel

If `uvx` is not installed, record that it was unavailable and use
`uv tool run unforgettable --help` and `uv tool run unforgettable --version` as
the equivalent ephemeral execution checks. The packaging test builds the wheel
and verifies installed console script, module execution, and version output
contracts. The agent memory smoke checks above exercise `set`, structured JSON
`get`, `exists`, `info`, `export`, `import --stdin`, and `delete`; keep those
commands passing before release.

## See Also

- GitHub: https://github.com/bouli/unforgettable
- PyPI: https://pypi.org/project/unforgettable/

## License

This package is distributed under the [MIT license](https://opensource.org/license/MIT).
