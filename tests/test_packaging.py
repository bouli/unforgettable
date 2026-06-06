import os
from pathlib import Path
import shutil
import subprocess
import sys
import venv


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def run_process(args, cwd=None):
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)
    return subprocess.run(
        args,
        cwd=cwd,
        env=env,
        text=True,
        capture_output=True,
    )


def assert_success(result):
    assert result.returncode == 0, (
        f"stdout:\n{result.stdout}\n\nstderr:\n{result.stderr}"
    )


def test_built_wheel_supports_installed_execution_paths(tmp_path):
    if shutil.which("uv") is None:
        raise AssertionError("uv is required to build the wheel")

    wheelhouse = tmp_path / "wheelhouse"
    wheelhouse.mkdir()
    build_result = run_process(
        ["uv", "build", "--wheel", "--out-dir", str(wheelhouse)],
        cwd=PROJECT_ROOT,
    )
    assert_success(build_result)

    wheels = sorted(wheelhouse.glob("unforgettable-*.whl"))
    assert len(wheels) == 1

    venv_path = tmp_path / "venv"
    venv.EnvBuilder(with_pip=True).create(venv_path)
    if sys.platform == "win32":
        python = venv_path / "Scripts" / "python.exe"
        unforgettable = venv_path / "Scripts" / "unforgettable.exe"
    else:
        python = venv_path / "bin" / "python"
        unforgettable = venv_path / "bin" / "unforgettable"

    install_result = run_process([str(python), "-m", "pip", "install", str(wheels[0])])
    assert_success(install_result)

    script_help = run_process([str(unforgettable), "--help"])
    assert_success(script_help)
    assert "Inspect and maintain an Unforgettable cache." in script_help.stdout
    assert "{list,set,get,clean}" in script_help.stdout
    assert "--cache-folder" in script_help.stdout

    module_help = run_process([str(python), "-m", "unforgettable", "--help"])
    assert_success(module_help)
    assert "Inspect and maintain an Unforgettable cache." in module_help.stdout
    assert "{list,set,get,clean}" in module_help.stdout
    assert "--cache-folder" in module_help.stdout

    version_result = run_process([str(unforgettable), "--version"])
    assert_success(version_result)
    assert version_result.stdout == "unforgettable v0.3.0\n"
