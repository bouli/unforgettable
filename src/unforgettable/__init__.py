from __future__ import annotations

import json
import os
import tempfile
from datetime import UTC, datetime


CACHE_INDEX_FILE_NAME = "cache_index.yaml"
CACHE_MANIFEST_FILE_NAME = "cache_manifest.json"


class unforgettable:
    cache_folder: str | None = None
    cache_files_extension: str = "cache"

    def __init__(
        self, cache_folder: str | None = None, cache_files_extension: str | None = None
    ):
        if cache_folder is not None:
            self.cache_folder = cache_folder
        else:
            self.cache_folder = self.get_cache_folder()

        if cache_files_extension is not None:
            self.cache_files_extension = cache_files_extension

    def safe_cache_id(func):
        def filter_cache_id(cache_id):
            cache_id = cache_id.replace('"', "").replace("\\", "")
            cache_id = f'"{cache_id}"'
            return cache_id

        def _filter_cache_id_func(*args, **kwargs):
            if "cache_id" in args:
                args["cache_id"] = filter_cache_id(cache_id=args["cache_id"])

            if "cache_id" in kwargs:
                kwargs["cache_id"] = filter_cache_id(cache_id=kwargs["cache_id"])

            return func(*args, **kwargs)

        return _filter_cache_id_func

    @safe_cache_id
    def set(self, content: str, cache_id: str):
        cache_folder = self.get_cache_folder()
        index_entries = self._read_index_entries()
        cached_file_index = self.get_index_from_file_index(_safe_cache_id=cache_id)
        if cached_file_index is not None:
            new_file_index = cached_file_index
        else:
            new_file_index = self._next_file_index(index_entries)
            index_entries.append((new_file_index, cache_id))
            self._write_index_entries(index_entries)

        new_file_name = f"{new_file_index}.{self.cache_files_extension}"
        new_file_path = os.path.join(cache_folder, new_file_name)
        content_type = "text/plain" if type(content) == str else "application/octet-stream"
        if type(content) == str:
            content = content.encode()
        self._atomic_write_bytes(new_file_path, content)
        self._record_manifest_entry(
            cache_id=cache_id,
            file_name=new_file_name,
            byte_size=len(content),
            content_type=content_type,
        )

    @safe_cache_id
    def get(self, cache_id: str) -> str:
        cached_file_index = self.get_index_from_file_index(_safe_cache_id=cache_id)
        code = self.get_cached_file_by_index(cached_file_index=cached_file_index)
        return code

    @safe_cache_id
    def exists(self, cache_id: str) -> bool:
        cached_file_index = self.get_index_from_file_index(_safe_cache_id=cache_id)
        if cached_file_index is None:
            return False

        cache_folder = self.get_cache_folder()
        cached_file_name = f"{cached_file_index}.{self.cache_files_extension}"
        cached_file_path = os.path.join(cache_folder, cached_file_name)
        return os.path.exists(cached_file_path)

    def list(self) -> list[str]:
        cache_ids = []
        for _, cache_id in self._read_index_entries():
            cache_ids.append(self._unsafe_cache_id(cache_id))

        return cache_ids

    def get_index_from_file_index(self, _safe_cache_id):
        for cached_file_index, cache_id in self._read_index_entries():
            if cache_id == _safe_cache_id:
                return cached_file_index
        return None

    def get_cache_index_path(
        self,
    ) -> str:
        cache_folder = self.get_cache_folder()
        cache_index_file_path = os.path.join(cache_folder, CACHE_INDEX_FILE_NAME)

        if not os.path.exists(cache_index_file_path):
            self._atomic_write_text(cache_index_file_path, f"0: {CACHE_INDEX_FILE_NAME}")

        return cache_index_file_path

    def get_cache_manifest_path(self) -> str:
        cache_folder = self.get_cache_folder()
        return os.path.join(cache_folder, CACHE_MANIFEST_FILE_NAME)

    def get_cache_index_file(
        self,
    ) -> str:
        with open(self.get_cache_index_path(), "r") as f:
            cache_index_file_content = f.read()

        return cache_index_file_content

    def get_cached_file_by_index(self, cached_file_index: int) -> str:
        code = None
        cache_folder = self.get_cache_folder()
        cached_file_name = f"{cached_file_index}.{self.cache_files_extension}"
        cached_file_path = os.path.join(cache_folder, cached_file_name)
        if not os.path.exists(cached_file_path):
            return None
        if self.is_file_binary(cached_file_path):
            read_mode = "rb"
        else:
            read_mode = "r"

        with open(cached_file_path, read_mode) as cached_file_reader:
            code = cached_file_reader.read()
        return code

    def clean(
        self,
    ):
        cache_folder = self.get_cache_folder()
        cache_folder_files = os.listdir(cache_folder)
        for file in cache_folder_files:
            file_to_clean = os.path.join(cache_folder, file)
            if os.path.exists(file_to_clean):
                os.remove(file_to_clean)

    def get_cache_folder(
        self,
    ):
        import tempfile

        if self.cache_folder is not None:
            return self.cache_folder

        tmpdirname = tempfile.mkdtemp()
        return tmpdirname

    def is_file_binary(self, file_path: str) -> bool:
        try:
            with open(file_path, "r") as fp:
                fp.read(16)
                return False
        except UnicodeDecodeError:
            return True

    def _read_index_entries(self) -> list[tuple[int, str]]:
        entries = []
        cache_index_file_name = os.path.basename(self.get_cache_index_path())

        for line in self.get_cache_index_file().splitlines():
            if ": " not in line:
                continue

            file_index, cache_id = line.split(": ", 1)
            cache_id = cache_id.strip()
            if cache_id == cache_index_file_name:
                continue

            entries.append((int(file_index.strip()), cache_id))

        return entries

    def _write_index_entries(self, entries: list[tuple[int, str]]):
        lines = [f"0: {CACHE_INDEX_FILE_NAME}"]
        lines.extend(f"{file_index}: {cache_id}" for file_index, cache_id in entries)
        self._atomic_write_text(self.get_cache_index_path(), "\n".join(lines))

    def _next_file_index(self, entries: list[tuple[int, str]]) -> int:
        if not entries:
            return 1
        return max(file_index for file_index, _ in entries) + 1

    def _read_manifest(self) -> dict:
        manifest_path = self.get_cache_manifest_path()
        if not os.path.exists(manifest_path):
            return {"version": 1, "entries": {}}

        with open(manifest_path, "r", encoding="utf-8") as manifest_reader:
            return json.load(manifest_reader)

    def _write_manifest(self, manifest: dict):
        manifest_path = self.get_cache_manifest_path()
        manifest_json = json.dumps(manifest, indent=2, sort_keys=True)
        self._atomic_write_text(manifest_path, f"{manifest_json}\n")

    def _record_manifest_entry(
        self,
        cache_id: str,
        file_name: str,
        byte_size: int,
        content_type: str,
    ):
        manifest = self._read_manifest()
        raw_cache_id = self._unsafe_cache_id(cache_id)
        existing_entry = manifest["entries"].get(raw_cache_id)
        now = datetime.now(UTC).isoformat()
        created_at = existing_entry["created_at"] if existing_entry else now
        manifest["entries"][raw_cache_id] = {
            "cache_id": raw_cache_id,
            "file_name": file_name,
            "byte_size": byte_size,
            "content_type": content_type,
            "created_at": created_at,
            "updated_at": now,
        }
        self._write_manifest(manifest)

    def _unsafe_cache_id(self, cache_id: str) -> str:
        if cache_id.startswith('"') and cache_id.endswith('"'):
            return cache_id[1:-1]
        return cache_id

    def _atomic_write_text(self, file_path: str, content: str):
        self._atomic_write_bytes(file_path, content.encode("utf-8"))

    def _atomic_write_bytes(self, file_path: str, content: bytes):
        directory = os.path.dirname(file_path)
        os.makedirs(directory, exist_ok=True)
        file_descriptor, temporary_path = tempfile.mkstemp(dir=directory)
        try:
            with os.fdopen(file_descriptor, "wb") as temporary_file:
                temporary_file.write(content)
            os.replace(temporary_path, file_path)
        except Exception:
            if os.path.exists(temporary_path):
                os.remove(temporary_path)
            raise
