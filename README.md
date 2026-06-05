# Unforgettable - v0.1.1

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

The `list` command prints one cache ID per line and prints nothing when the
selected cache folder has no user-created entries.

Store text under a cache ID:

```shell
unforgettable --cache-folder .unforgettable-cache set greeting "hello"
```

Retrieve cached text:

```shell
unforgettable --cache-folder .unforgettable-cache get greeting
```

Clean the selected cache folder:

```shell
unforgettable --cache-folder .unforgettable-cache clean
```

`get` exits with status code `1` when the requested cache ID is missing.

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

## See Also

- GitHub: https://github.com/bouli/unforgettable
- PyPI: https://pypi.org/project/unforgettable/

## License

This package is distributed under the [MIT license](https://opensource.org/license/MIT).
