import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

from unforgettable import unforgettable

PROJECT_ROOT = Path(__file__).resolve().parents[1]


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


def run_local_checkout(*args):
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)
    return subprocess.run(
        ["uv", "run", *args],
        cwd=PROJECT_ROOT,
        env=env,
        text=True,
        capture_output=True,
    )


def test_local_checkout_module_execution_shows_cli_help():
    if shutil.which("uv") is None:
        raise AssertionError("uv is required to verify local checkout execution")

    result = run_local_checkout("python", "-m", "unforgettable", "--help")

    assert result.returncode == 0
    assert "Inspect and maintain an Unforgettable cache." in result.stdout
    assert "{list,set,get,exists,delete,clean}" in result.stdout
    assert "--cache-folder" in result.stdout
    assert ".unforgettable-memory" in result.stdout


def test_local_checkout_console_script_shows_cli_help():
    if shutil.which("uv") is None:
        raise AssertionError("uv is required to verify local checkout execution")

    result = run_local_checkout("unforgettable", "--help")

    assert result.returncode == 0
    assert "Inspect and maintain an Unforgettable cache." in result.stdout
    assert "{list,set,get,exists,delete,clean}" in result.stdout
    assert "--cache-folder" in result.stdout
    assert ".unforgettable-memory" in result.stdout


def test_cli_help_describes_list_command():
    result = run_cli("--help")

    assert result.returncode == 0
    assert "list" in result.stdout
    assert "--cache-folder" in result.stdout
    assert "--create-cache-folder" in result.stdout
    assert "--no-create-cache-folder" in result.stdout
    assert "--output" in result.stdout
    assert "{text,json}" in result.stdout
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


def test_cli_list_json_outputs_cache_ids_as_structured_data(tmp_path):
    cache = unforgettable(cache_folder=str(tmp_path))
    cache.set(content="first", cache_id="alpha")
    cache.set(content="second", cache_id="id with spaces: and punctuation?!")

    result = run_cli("--cache-folder", str(tmp_path), "--output", "json", "list")

    assert result.returncode == 0
    assert result.stderr == ""
    assert json.loads(result.stdout) == {
        "cache_ids": ["alpha", "id with spaces: and punctuation?!"]
    }


def test_cli_list_json_handles_empty_cache_folder(tmp_path):
    result = run_cli("--cache-folder", str(tmp_path), "--output", "json", "list")

    assert result.returncode == 0
    assert result.stderr == ""
    assert json.loads(result.stdout) == {"cache_ids": []}


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


def test_cli_set_reads_multiline_text_content_from_stdin(tmp_path):
    content = "first line\nsecond line\nthird line"

    result = run_cli(
        "--cache-folder",
        str(tmp_path),
        "set",
        "script-key",
        "--stdin",
        input=content,
    )

    assert result.returncode == 0
    assert result.stdout == ""
    assert result.stderr == ""
    assert unforgettable(cache_folder=str(tmp_path)).get(cache_id="script-key") == (
        content
    )


def test_cli_get_prints_multiline_stdin_content_without_extra_decoration(tmp_path):
    content = "first line\nsecond line\n"
    set_result = run_cli(
        "--cache-folder",
        str(tmp_path),
        "set",
        "multiline",
        "--stdin",
        input=content,
    )

    result = run_cli("--cache-folder", str(tmp_path), "get", "multiline")

    assert set_result.returncode == 0
    assert result.returncode == 0
    assert result.stderr == ""
    assert result.stdout == content


def test_cli_stdin_set_round_trips_cache_ids_with_spaces_and_punctuation(tmp_path):
    cache_id = "id with spaces: and punctuation?!"
    content = "stored through stdin"

    set_result = run_cli(
        "--cache-folder",
        str(tmp_path),
        "set",
        cache_id,
        "--stdin",
        input=content,
    )
    get_result = run_cli("--cache-folder", str(tmp_path), "get", cache_id)
    list_result = run_cli("--cache-folder", str(tmp_path), "list")

    assert set_result.returncode == 0
    assert get_result.returncode == 0
    assert get_result.stdout == content
    assert list_result.returncode == 0
    assert list_result.stdout.splitlines() == [cache_id]


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


def test_cli_create_cache_folder_creates_missing_explicit_folder_without_prompt(
    tmp_path,
):
    explicit_cache_folder = tmp_path / "new-cache"

    result = run_cli(
        "--cache-folder",
        str(explicit_cache_folder),
        "--create-cache-folder",
        "set",
        "script-key",
        "stored explicitly",
        input="",
    )

    assert result.returncode == 0
    assert result.stdout == ""
    assert result.stderr == ""
    assert unforgettable(cache_folder=str(explicit_cache_folder)).get(
        cache_id="script-key"
    ) == "stored explicitly"


def test_cli_no_create_cache_folder_rejects_missing_explicit_folder_without_prompt(
    tmp_path,
):
    explicit_cache_folder = tmp_path / "new-cache"

    result = run_cli(
        "--cache-folder",
        str(explicit_cache_folder),
        "--no-create-cache-folder",
        "set",
        "script-key",
        "stored explicitly",
        input="yes\n",
    )

    assert result.returncode == 1
    assert result.stdout == ""
    assert result.stderr == "unforgettable: cache folder does not exist\n"
    assert not explicit_cache_folder.exists()


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
    assert result.stdout == "stored value"


def test_cli_exists_present_cache_id_exits_zero_with_text_result(tmp_path):
    cache = unforgettable(cache_folder=str(tmp_path))
    cache.set(content="stored value", cache_id="script-key")

    result = run_cli("--cache-folder", str(tmp_path), "exists", "script-key")

    assert result.returncode == 0
    assert result.stderr == ""
    assert result.stdout == "true\n"


def test_cli_exists_missing_cache_id_exits_one_with_text_result(tmp_path):
    result = run_cli("--cache-folder", str(tmp_path), "exists", "missing")

    assert result.returncode == 1
    assert result.stderr == ""
    assert result.stdout == "false\n"


def test_cli_exists_json_outputs_cache_id_and_boolean_result(tmp_path):
    cache = unforgettable(cache_folder=str(tmp_path))
    cache.set(content="stored value", cache_id="script-key")

    result = run_cli(
        "--cache-folder",
        str(tmp_path),
        "--output",
        "json",
        "exists",
        "script-key",
    )

    assert result.returncode == 0
    assert result.stderr == ""
    assert json.loads(result.stdout) == {
        "cache_id": "script-key",
        "exists": True,
    }


def test_cli_exists_json_missing_cache_id_exits_one_with_false_result(tmp_path):
    result = run_cli(
        "--cache-folder",
        str(tmp_path),
        "--output",
        "json",
        "exists",
        "missing",
    )

    assert result.returncode == 1
    assert result.stderr == ""
    assert json.loads(result.stdout) == {"cache_id": "missing", "exists": False}


def test_cli_exists_round_trips_cache_ids_with_spaces_and_punctuation(tmp_path):
    cache_id = "id with spaces: and punctuation?!"
    cache = unforgettable(cache_folder=str(tmp_path))
    cache.set(content="stored value", cache_id=cache_id)

    result = run_cli(
        "--cache-folder",
        str(tmp_path),
        "--output",
        "json",
        "exists",
        cache_id,
    )

    assert result.returncode == 0
    assert result.stderr == ""
    assert json.loads(result.stdout) == {"cache_id": cache_id, "exists": True}


def test_cli_delete_removes_cache_id_from_get_list_manifest_and_files(tmp_path):
    cache = unforgettable(cache_folder=str(tmp_path))
    cache.set(content="first value", cache_id="first")
    cache.set(content="second value", cache_id="second")

    result = run_cli("--cache-folder", str(tmp_path), "delete", "first")
    list_result = run_cli("--cache-folder", str(tmp_path), "list")
    get_result = run_cli("--cache-folder", str(tmp_path), "get", "first")

    assert result.returncode == 0
    assert result.stdout == ""
    assert result.stderr == ""
    assert list_result.returncode == 0
    assert list_result.stdout.splitlines() == ["second"]
    assert get_result.returncode == 1
    assert get_result.stdout == ""
    assert get_result.stderr == "unforgettable: cache ID not found: first\n"
    manifest = json.loads((tmp_path / "cache_manifest.json").read_text())
    assert "first" not in manifest["entries"]
    assert "second" in manifest["entries"]
    assert not (tmp_path / "1.cache").exists()
    assert (tmp_path / "2.cache").exists()


def test_cli_delete_missing_cache_id_exits_one_with_diagnostic(tmp_path):
    result = run_cli("--cache-folder", str(tmp_path), "delete", "missing")

    assert result.returncode == 1
    assert result.stdout == ""
    assert result.stderr == "unforgettable: cache ID not found: missing\n"


def test_cli_delete_repeated_deletion_exits_one_on_second_attempt(tmp_path):
    cache = unforgettable(cache_folder=str(tmp_path))
    cache.set(content="stored value", cache_id="repeat")

    first_result = run_cli("--cache-folder", str(tmp_path), "delete", "repeat")
    second_result = run_cli("--cache-folder", str(tmp_path), "delete", "repeat")

    assert first_result.returncode == 0
    assert first_result.stdout == ""
    assert first_result.stderr == ""
    assert second_result.returncode == 1
    assert second_result.stdout == ""
    assert second_result.stderr == "unforgettable: cache ID not found: repeat\n"


def test_cli_delete_round_trips_cache_ids_with_spaces_and_punctuation(tmp_path):
    cache_id = "id with spaces: and punctuation?!"
    cache = unforgettable(cache_folder=str(tmp_path))
    cache.set(content="stored value", cache_id=cache_id)

    result = run_cli("--cache-folder", str(tmp_path), "delete", cache_id)

    assert result.returncode == 0
    assert result.stdout == ""
    assert result.stderr == ""
    assert unforgettable(cache_folder=str(tmp_path)).list() == []


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
    assert result.stdout == ""
    assert result.stderr == "unforgettable: set requires CONTENT or --stdin\n"


def test_cli_set_rejects_content_argument_with_stdin_flag(tmp_path):
    result = run_cli(
        "--cache-folder",
        str(tmp_path),
        "set",
        "script-key",
        "argument content",
        "--stdin",
        input="stdin content",
    )

    assert result.returncode == 2
    assert result.stdout == ""
    assert result.stderr == (
        "unforgettable: set accepts either CONTENT or --stdin, not both\n"
    )


def test_cli_set_stdin_requires_input_content(tmp_path):
    result = run_cli(
        "--cache-folder",
        str(tmp_path),
        "set",
        "script-key",
        "--stdin",
        input="",
    )

    assert result.returncode == 1
    assert result.stdout == ""
    assert result.stderr == "unforgettable: no stdin content received\n"
