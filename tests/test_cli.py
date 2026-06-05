import os
import subprocess
import sys

from unforgettable import unforgettable


def run_cli(*args, cwd=None):
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
    )


def test_cli_help_describes_list_command():
    result = run_cli("--help")

    assert result.returncode == 0
    assert "list" in result.stdout
    assert "--cache-folder" in result.stdout


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
