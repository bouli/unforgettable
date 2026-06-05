import os
import subprocess
import sys

from unforgettable import unforgettable


def run_cli(*args, cwd=None, input=None):
    env = os.environ.copy()
    src_path = os.path.abspath("src")
    env["PYTHONPATH"] = (
        src_path
        if not env.get("PYTHONPATH")
        else os.pathsep.join([src_path, env["PYTHONPATH"]])
    )
    return subprocess.run(
        [sys.executable, "-m", "unforgettable", *args],
        cwd=cwd,
        env=env,
        text=True,
        capture_output=True,
        input=input,
    )


def test_cli_help_describes_list_command():
    result = run_cli("--help")

    assert result.returncode == 0
    assert "list" in result.stdout
    assert "--cache-folder" in result.stdout
    assert ".unforgettable-memory" in result.stdout


def test_cli_list_prints_cache_ids_from_selected_cache_folder(tmp_path):
    cache = unforgettable(cache_folder=str(tmp_path))
    cache.set(content="first", cache_id="alpha")
    cache.set(content="second", cache_id="id with spaces: and punctuation?!")

    result = run_cli("--cache-folder", str(tmp_path), "list")

    assert result.returncode == 0
    assert result.stderr == ""
    assert result.stdout.splitlines() == [
        "alpha",
        "id with spaces: and punctuation?!",
    ]


def test_cli_list_handles_empty_cache_folder(tmp_path):
    result = run_cli("--cache-folder", str(tmp_path), "list")

    assert result.returncode == 0
    assert result.stderr == ""
    assert result.stdout == ""


def test_cli_set_stores_text_content_in_selected_cache_folder(tmp_path):
    result = run_cli(
        "--cache-folder",
        str(tmp_path),
        "set",
        "script-key",
        "stored from shell",
    )

    assert result.returncode == 0
    assert result.stdout == ""
    assert result.stderr == ""
    assert unforgettable(cache_folder=str(tmp_path)).get(cache_id="script-key") == (
        "stored from shell"
    )


def test_cli_set_uses_default_cache_folder_when_omitted(tmp_path):
    result = run_cli("set", "script-key", "stored from default folder", cwd=tmp_path)

    assert result.returncode == 0
    assert result.stdout == ""
    assert result.stderr == ""
    assert unforgettable(cache_folder=str(tmp_path / ".unforgettable-memory")).get(
        cache_id="script-key"
    ) == "stored from default folder"


def test_cli_explicit_cache_folder_overrides_default(tmp_path):
    explicit_cache_folder = tmp_path / "explicit-cache"
    explicit_cache_folder.mkdir()

    result = run_cli(
        "--cache-folder",
        str(explicit_cache_folder),
        "set",
        "script-key",
        "stored explicitly",
        cwd=tmp_path,
    )

    assert result.returncode == 0
    assert result.stdout == ""
    assert result.stderr == ""
    assert unforgettable(cache_folder=str(explicit_cache_folder)).get(
        cache_id="script-key"
    ) == "stored explicitly"
    assert not (tmp_path / ".unforgettable-memory").exists()


def test_cli_prompts_before_creating_missing_explicit_cache_folder(tmp_path):
    explicit_cache_folder = tmp_path / "new-cache"

    result = run_cli(
        "--cache-folder",
        str(explicit_cache_folder),
        "set",
        "script-key",
        "stored explicitly",
        input="yes\n",
    )

    assert result.returncode == 0
    assert result.stdout == ""
    assert "Create it? [y/N]" in result.stderr
    assert unforgettable(cache_folder=str(explicit_cache_folder)).get(
        cache_id="script-key"
    ) == "stored explicitly"


def test_cli_declining_missing_explicit_cache_folder_does_not_create_it(tmp_path):
    explicit_cache_folder = tmp_path / "new-cache"

    result = run_cli(
        "--cache-folder",
        str(explicit_cache_folder),
        "set",
        "script-key",
        "stored explicitly",
        input="no\n",
    )

    assert result.returncode == 1
    assert result.stdout == ""
    assert "cache folder was not created" in result.stderr
    assert not explicit_cache_folder.exists()


def test_cli_missing_explicit_cache_folder_without_input_exits_nonzero(tmp_path):
    explicit_cache_folder = tmp_path / "new-cache"

    result = run_cli(
        "--cache-folder",
        str(explicit_cache_folder),
        "list",
        input="",
    )

    assert result.returncode == 1
    assert result.stdout == ""
    assert "cache folder creation cancelled" in result.stderr
    assert "cache folder was not created" in result.stderr
    assert not explicit_cache_folder.exists()


def test_cli_get_prints_cached_text_from_selected_cache_folder(tmp_path):
    cache = unforgettable(cache_folder=str(tmp_path))
    cache.set(content="stored value", cache_id="script-key")

    result = run_cli("--cache-folder", str(tmp_path), "get", "script-key")

    assert result.returncode == 0
    assert result.stderr == ""
    assert result.stdout == "stored value\n"


def test_cli_clean_removes_entries_from_selected_cache_folder(tmp_path):
    cache = unforgettable(cache_folder=str(tmp_path))
    cache.set(content="stored value", cache_id="script-key")

    result = run_cli("--cache-folder", str(tmp_path), "clean")

    assert result.returncode == 0
    assert result.stdout == ""
    assert result.stderr == ""
    assert unforgettable(cache_folder=str(tmp_path)).list() == []


def test_cli_get_missing_cache_id_exits_nonzero_with_message(tmp_path):
    result = run_cli("--cache-folder", str(tmp_path), "get", "missing")

    assert result.returncode == 1
    assert result.stdout == ""
    assert result.stderr == "unforgettable: cache ID not found: missing\n"


def test_cli_set_requires_content_argument(tmp_path):
    result = run_cli("--cache-folder", str(tmp_path), "set", "missing-content")

    assert result.returncode == 2
    assert "usage:" in result.stderr
