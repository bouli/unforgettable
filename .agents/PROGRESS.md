## 2026-06-06 - 001 Manifest-Backed Metadata

- Implemented sidecar manifest persistence at `cache_manifest.json`.
- Manifest entries now track cache ID, content file name, byte size, content type, created time, and updated time.
- Preserved legacy cache folder readability for existing index/content files.
- Updated overwrites to preserve `created_at` and refresh `updated_at`.
- Switched content, index, and manifest writes to temp-file plus `os.replace` atomic replacement.
- Confirmed `clean` removes content files, `cache_index.yaml`, and `cache_manifest.json`.
- Added regression coverage for manifest metadata, binary metadata, legacy cache folders, overwrite timestamps, clean behavior, and atomic replacement.
- Verification: `uv run pytest` passed with 44 tests.

## 2026-06-06 - 002 Existence Checks

- Added `cache.exists(cache_id)` to the Python API.
- Added `exists CACHE_ID` to the CLI with text output of `true` or `false`.
- Added `exists CACHE_ID --output json` with `{"cache_id": "...", "exists": true|false}` output.
- Preserved stdout for command values and stderr for diagnostics; missing entries exit with status code `1`.
- Documented the existence-check command and API in the README.
- Added regression coverage for present entries, missing entries, JSON output, text output, and cache IDs with spaces and punctuation.
- Verification: `uv run pytest` passed with 50 tests.

## 2026-06-06 - 003 Single-Entry Deletion

- Added `cache.delete(cache_id)` to the Python API, returning `True` when an entry is removed and `False` when the cache ID is missing.
- Added `delete CACHE_ID` to the CLI; successful deletion exits `0` with no stdout, while missing IDs exit `1` with a stderr diagnostic.
- Deletion now removes the selected content file and updates both `cache_index.yaml` and `cache_manifest.json` while preserving unrelated entries.
- Documented the deletion command and API in the README.
- Added regression coverage for successful deletion, missing deletion, repeated deletion, IDs with spaces and punctuation, and post-delete `list`/`get` behavior.
- Verification: `uv run pytest` passed with 56 tests.

## 2026-06-06 - 004 Entry Info

- Added `cache.info(cache_id)` to the Python API, returning metadata for existing entries and `None` for missing entries.
- Added `info CACHE_ID` to the CLI with readable text output and structured JSON output.
- Metadata inspection now returns cache ID, content file name, byte size, content type, created time, and updated time.
- Legacy cache folders without `cache_manifest.json` derive metadata from the index and content file.
- Missing `info` lookups exit `1` with a stderr diagnostic.
- Documented the metadata inspection command, JSON shape, legacy derivation, and API in the README.
- Added regression coverage for API metadata, text output, JSON output, missing entries, legacy cache folders, and IDs with spaces and punctuation.
- Verification: `uv run pytest` passed with 63 tests.

## 2026-06-06 - 005 Structured JSON Get

- Added `cache.get_entry(cache_id)` to return cache ID, content, encoding, and metadata for structured callers.
- Extended `get CACHE_ID --output json` to emit a parseable object while preserving raw stdout behavior for text-mode `get`.
- Represented text content with `encoding: "utf-8"` and binary content with `encoding: "base64"`.
- Preserved missing-entry behavior: exit status `1`, empty stdout, and the existing stderr diagnostic.
- Documented structured `get`, the JSON shape, the new API method, and binary base64 representation in the README.
- Added regression coverage for raw text output, JSON text, JSON multiline content, JSON binary content, missing entries, cache IDs with spaces and punctuation, and API structured retrieval.
- Verification: `uv run pytest` passed with 72 tests.

## 2026-06-06 - 006 JSON Export

- Added `cache.export()` to return all cache entries as a JSON-compatible `{"entries": [...]}` structure.
- Added `export` to the CLI, emitting valid JSON to stdout for the selected cache folder.
- Export entries reuse the structured `get` shape: cache ID, content, encoding marker, and metadata.
- Empty cache folders export as `{"entries": []}`.
- Preserved text, multiline text, cache IDs with spaces and punctuation, binary base64 content, and legacy cache folder metadata derivation.
- Documented the export command, JSON shape, empty result, API method, and binary representation in the README.
- Added regression coverage for API export, CLI export, empty exports, multiple entries, multiline text, binary content, legacy cache folders, installed help, and README contract.
- Verification: `uv run pytest` passed with 79 tests.
