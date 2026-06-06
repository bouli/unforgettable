import json
import os
import time
from base64 import b64encode
from datetime import datetime
from pathlib import Path

import unforgettable as unforgettable_module
from unforgettable import unforgettable


def test_get_returns_none_for_missing_cache_id(tmp_path):
    cache = unforgettable(cache_folder=str(tmp_path))

    assert cache.get(cache_id="missing") is None


def test_exists_returns_false_for_missing_cache_id(tmp_path):
    cache = unforgettable(cache_folder=str(tmp_path))

    assert cache.exists(cache_id="missing") is False


def test_list_returns_empty_list_for_new_cache_folder(tmp_path):
    cache = unforgettable(cache_folder=str(tmp_path))

    assert cache.list() == []


def test_set_and_get_text_content(tmp_path):
    cache = unforgettable(cache_folder=str(tmp_path))

    cache.set(content="cached value", cache_id="example")

    assert cache.get(cache_id="example") == "cached value"
    assert cache.exists(cache_id="example") is True
    assert cache.list() == ["example"]


def test_set_and_get_binary_content(tmp_path):
    cache = unforgettable(cache_folder=str(tmp_path))
    content = b"\x80\x81cached bytes"

    cache.set(content=content, cache_id="binary")

    assert cache.get(cache_id="binary") == content


def test_get_entry_returns_structured_text_content_and_metadata(tmp_path):
    cache = unforgettable(cache_folder=str(tmp_path))
    content = "first line\nsecond line"
    cache_id = "id with spaces: and punctuation?!"

    cache.set(content=content, cache_id=cache_id)

    entry = cache.get_entry(cache_id=cache_id)
    assert entry["cache_id"] == cache_id
    assert entry["content"] == content
    assert entry["encoding"] == "utf-8"
    assert entry["metadata"]["cache_id"] == cache_id
    assert entry["metadata"]["content_type"] == "text/plain"
    assert entry["metadata"]["byte_size"] == len(content.encode())


def test_get_entry_returns_base64_encoded_binary_content(tmp_path):
    cache = unforgettable(cache_folder=str(tmp_path))
    content = b"\x80\x81cached bytes"

    cache.set(content=content, cache_id="binary")

    entry = cache.get_entry(cache_id="binary")
    assert entry["cache_id"] == "binary"
    assert entry["content"] == b64encode(content).decode("ascii")
    assert entry["encoding"] == "base64"
    assert entry["metadata"]["content_type"] == "application/octet-stream"
    assert entry["metadata"]["byte_size"] == len(content)


def test_get_entry_returns_none_for_missing_cache_id(tmp_path):
    cache = unforgettable(cache_folder=str(tmp_path))

    assert cache.get_entry(cache_id="missing") is None


def test_export_returns_empty_entries_for_empty_cache_folder(tmp_path):
    cache = unforgettable(cache_folder=str(tmp_path))

    assert cache.export() == {"entries": []}


def test_export_returns_structured_entries_in_list_order(tmp_path):
    cache = unforgettable(cache_folder=str(tmp_path))
    multiline = "first line\nsecond line\n"
    binary = b"\x80\x81cached bytes"
    punctuated_cache_id = "id with spaces: and punctuation?!"

    cache.set(content=multiline, cache_id=punctuated_cache_id)
    cache.set(content=binary, cache_id="binary")

    exported = cache.export()

    assert [entry["cache_id"] for entry in exported["entries"]] == [
        punctuated_cache_id,
        "binary",
    ]
    assert exported["entries"][0]["content"] == multiline
    assert exported["entries"][0]["encoding"] == "utf-8"
    assert exported["entries"][0]["metadata"]["content_type"] == "text/plain"
    assert exported["entries"][1]["content"] == b64encode(binary).decode("ascii")
    assert exported["entries"][1]["encoding"] == "base64"
    assert exported["entries"][1]["metadata"]["content_type"] == (
        "application/octet-stream"
    )


def test_export_derives_metadata_for_legacy_cache_folder_without_manifest(tmp_path):
    (tmp_path / "cache_index.yaml").write_text('0: cache_index.yaml\n1: "legacy"')
    (tmp_path / "1.cache").write_text("legacy value")
    cache = unforgettable(cache_folder=str(tmp_path))

    exported = cache.export()

    assert len(exported["entries"]) == 1
    entry = exported["entries"][0]
    assert entry["cache_id"] == "legacy"
    assert entry["content"] == "legacy value"
    assert entry["encoding"] == "utf-8"
    assert entry["metadata"]["cache_id"] == "legacy"
    assert entry["metadata"]["byte_size"] == len("legacy value".encode())
    assert entry["metadata"]["created_at"] == entry["metadata"]["updated_at"]


def test_overwrites_existing_cache_entry(tmp_path):
    cache = unforgettable(cache_folder=str(tmp_path))

    cache.set(content="first value", cache_id="repeat")
    cache.set(content="second value", cache_id="repeat")

    assert cache.get(cache_id="repeat") == "second value"
    assert cache.list() == ["repeat"]


def test_delete_removes_single_cache_entry_index_manifest_and_file(tmp_path):
    cache = unforgettable(cache_folder=str(tmp_path))
    cache.set(content="first value", cache_id="first")
    cache.set(content="second value", cache_id="second")

    assert cache.delete(cache_id="first") is True

    assert cache.get(cache_id="first") is None
    assert cache.exists(cache_id="first") is False
    assert cache.get(cache_id="second") == "second value"
    assert cache.list() == ["second"]
    manifest = json.loads((tmp_path / "cache_manifest.json").read_text())
    assert "first" not in manifest["entries"]
    assert manifest["entries"]["second"]["file_name"] == "2.cache"
    assert not (tmp_path / "1.cache").exists()
    assert (tmp_path / "2.cache").exists()


def test_delete_returns_false_for_missing_cache_id(tmp_path):
    cache = unforgettable(cache_folder=str(tmp_path))

    assert cache.delete(cache_id="missing") is False


def test_info_returns_manifest_metadata_for_cache_id(tmp_path):
    cache = unforgettable(cache_folder=str(tmp_path))
    cache_id = "id with spaces: and punctuation?!"

    cache.set(content="cached value", cache_id=cache_id)

    metadata = cache.info(cache_id=cache_id)
    assert metadata["cache_id"] == cache_id
    assert metadata["file_name"] == "1.cache"
    assert metadata["byte_size"] == len("cached value".encode())
    assert metadata["content_type"] == "text/plain"
    assert datetime.fromisoformat(metadata["created_at"])
    assert datetime.fromisoformat(metadata["updated_at"])


def test_info_returns_none_for_missing_cache_id(tmp_path):
    cache = unforgettable(cache_folder=str(tmp_path))

    assert cache.info(cache_id="missing") is None


def test_info_derives_metadata_for_legacy_cache_folder_without_manifest(tmp_path):
    (tmp_path / "cache_index.yaml").write_text('0: cache_index.yaml\n1: "legacy"')
    (tmp_path / "1.cache").write_text("legacy value")
    cache = unforgettable(cache_folder=str(tmp_path))

    metadata = cache.info(cache_id="legacy")

    assert metadata["cache_id"] == "legacy"
    assert metadata["file_name"] == "1.cache"
    assert metadata["byte_size"] == len("legacy value".encode())
    assert metadata["content_type"] == "text/plain"
    assert datetime.fromisoformat(metadata["created_at"])
    assert metadata["updated_at"] == metadata["created_at"]


def test_multiple_cache_ids_are_retrieved_independently(tmp_path):
    cache = unforgettable(cache_folder=str(tmp_path))

    cache.set(content="one", cache_id="first")
    cache.set(content="two", cache_id="second")

    assert cache.get(cache_id="first") == "one"
    assert cache.get(cache_id="second") == "two"
    assert cache.list() == ["first", "second"]


def test_list_preserves_cache_ids_with_spaces_and_punctuation(tmp_path):
    cache = unforgettable(cache_folder=str(tmp_path))
    cache_id = "id with spaces: and punctuation?!"

    cache.set(content="stored", cache_id=cache_id)

    assert cache.list() == [cache_id]
    assert cache.get(cache_id=cache_id) == "stored"
    assert cache.exists(cache_id=cache_id) is True


def test_configured_cache_folder_persists_between_instances(tmp_path):
    cache_folder = str(tmp_path)
    cache = unforgettable(cache_folder=cache_folder)
    cache.set(content="persisted", cache_id="shared")

    new_cache = unforgettable(cache_folder=cache_folder)

    assert new_cache.get(cache_id="shared") == "persisted"
    assert new_cache.list() == ["shared"]


def test_default_cache_folder_is_reused_by_same_instance():
    cache = unforgettable()

    cache.set(content="temporary", cache_id="same-instance")

    assert cache.get(cache_id="same-instance") == "temporary"

    cache.clean()
    Path(cache.cache_folder).rmdir()


def test_custom_cache_file_extension_is_used(tmp_path):
    cache = unforgettable(cache_folder=str(tmp_path), cache_files_extension="txt")

    cache.set(content="custom extension", cache_id="file-extension")

    assert cache.get(cache_id="file-extension") == "custom extension"
    assert cache.list() == ["file-extension"]
    assert list(tmp_path.glob("*.txt"))


def test_clean_removes_cache_files_from_configured_folder(tmp_path):
    cache = unforgettable(cache_folder=str(tmp_path))
    cache.set(content="cached", cache_id="to-clean")

    cache.clean()

    assert list(tmp_path.iterdir()) == []


def test_set_records_manifest_metadata_for_new_entries(tmp_path):
    cache = unforgettable(cache_folder=str(tmp_path))

    cache.set(content="cached value", cache_id="example")

    manifest = json.loads((tmp_path / "cache_manifest.json").read_text())
    entry = manifest["entries"]["example"]
    assert entry["cache_id"] == "example"
    assert entry["file_name"] == "1.cache"
    assert entry["byte_size"] == len("cached value".encode())
    assert entry["content_type"] == "text/plain"
    assert datetime.fromisoformat(entry["created_at"])
    assert datetime.fromisoformat(entry["updated_at"])


def test_set_records_binary_content_type_and_byte_size(tmp_path):
    cache = unforgettable(cache_folder=str(tmp_path))
    content = b"\x80\x81cached bytes"

    cache.set(content=content, cache_id="binary")

    manifest = json.loads((tmp_path / "cache_manifest.json").read_text())
    entry = manifest["entries"]["binary"]
    assert entry["byte_size"] == len(content)
    assert entry["content_type"] == "application/octet-stream"


def test_overwriting_existing_entry_preserves_created_time_and_updates_updated_time(
    tmp_path,
):
    cache = unforgettable(cache_folder=str(tmp_path))

    cache.set(content="first value", cache_id="repeat")
    original_entry = json.loads((tmp_path / "cache_manifest.json").read_text())[
        "entries"
    ]["repeat"]
    time.sleep(0.001)
    cache.set(content="second value", cache_id="repeat")

    updated_entry = json.loads((tmp_path / "cache_manifest.json").read_text())[
        "entries"
    ]["repeat"]
    assert updated_entry["created_at"] == original_entry["created_at"]
    assert updated_entry["updated_at"] > original_entry["updated_at"]
    assert updated_entry["byte_size"] == len("second value".encode())
    assert cache.get(cache_id="repeat") == "second value"


def test_legacy_cache_folder_without_manifest_remains_readable_and_updatable(tmp_path):
    (tmp_path / "cache_index.yaml").write_text('0: cache_index.yaml\n1: "legacy"')
    (tmp_path / "1.cache").write_text("legacy value")
    cache = unforgettable(cache_folder=str(tmp_path))

    assert cache.get(cache_id="legacy") == "legacy value"
    assert cache.list() == ["legacy"]

    cache.set(content="modern value", cache_id="modern")

    assert cache.get(cache_id="legacy") == "legacy value"
    assert cache.get(cache_id="modern") == "modern value"
    assert cache.list() == ["legacy", "modern"]
    manifest = json.loads((tmp_path / "cache_manifest.json").read_text())
    assert manifest["entries"]["modern"]["file_name"] == "2.cache"


def test_clean_removes_manifest_index_and_content_files(tmp_path):
    cache = unforgettable(cache_folder=str(tmp_path))
    cache.set(content="cached", cache_id="to-clean")

    assert (tmp_path / "cache_index.yaml").exists()
    assert (tmp_path / "cache_manifest.json").exists()
    assert (tmp_path / "1.cache").exists()

    cache.clean()

    assert list(tmp_path.iterdir()) == []


def test_set_uses_atomic_replacement_for_index_content_and_manifest_writes(
    tmp_path,
    monkeypatch,
):
    original_replace = os.replace
    replaced_paths = []

    def recording_replace(source, destination):
        replaced_paths.append(Path(destination).name)
        original_replace(source, destination)

    monkeypatch.setattr(unforgettable_module.os, "replace", recording_replace)
    cache = unforgettable(cache_folder=str(tmp_path))

    cache.set(content="cached", cache_id="atomic")

    assert "cache_index.yaml" in replaced_paths
    assert "1.cache" in replaced_paths
    assert "cache_manifest.json" in replaced_paths
