from pathlib import Path

from unforgettable import unforgettable


def test_get_returns_none_for_missing_cache_id(tmp_path):
    cache = unforgettable(cache_folder=str(tmp_path))

    assert cache.get(cache_id="missing") is None


def test_set_and_get_text_content(tmp_path):
    cache = unforgettable(cache_folder=str(tmp_path))

    cache.set(content="cached value", cache_id="example")

    assert cache.get(cache_id="example") == "cached value"


def test_set_and_get_binary_content(tmp_path):
    cache = unforgettable(cache_folder=str(tmp_path))
    content = b"\x80\x81cached bytes"

    cache.set(content=content, cache_id="binary")

    assert cache.get(cache_id="binary") == content


def test_overwrites_existing_cache_entry(tmp_path):
    cache = unforgettable(cache_folder=str(tmp_path))

    cache.set(content="first value", cache_id="repeat")
    cache.set(content="second value", cache_id="repeat")

    assert cache.get(cache_id="repeat") == "second value"


def test_multiple_cache_ids_are_retrieved_independently(tmp_path):
    cache = unforgettable(cache_folder=str(tmp_path))

    cache.set(content="one", cache_id="first")
    cache.set(content="two", cache_id="second")

    assert cache.get(cache_id="first") == "one"
    assert cache.get(cache_id="second") == "two"


def test_configured_cache_folder_persists_between_instances(tmp_path):
    cache_folder = str(tmp_path)
    cache = unforgettable(cache_folder=cache_folder)
    cache.set(content="persisted", cache_id="shared")

    new_cache = unforgettable(cache_folder=cache_folder)

    assert new_cache.get(cache_id="shared") == "persisted"


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
    assert list(tmp_path.glob("*.txt"))


def test_clean_removes_cache_files_from_configured_folder(tmp_path):
    cache = unforgettable(cache_folder=str(tmp_path))
    cache.set(content="cached", cache_id="to-clean")

    cache.clean()

    assert list(tmp_path.iterdir()) == []
