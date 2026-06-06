## 2026-06-06 - 001 Manifest-Backed Metadata

- Implemented sidecar manifest persistence at `cache_manifest.json`.
- Manifest entries now track cache ID, content file name, byte size, content type, created time, and updated time.
- Preserved legacy cache folder readability for existing index/content files.
- Updated overwrites to preserve `created_at` and refresh `updated_at`.
- Switched content, index, and manifest writes to temp-file plus `os.replace` atomic replacement.
- Confirmed `clean` removes content files, `cache_index.yaml`, and `cache_manifest.json`.
- Added regression coverage for manifest metadata, binary metadata, legacy cache folders, overwrite timestamps, clean behavior, and atomic replacement.
- Verification: `uv run pytest` passed with 44 tests.
