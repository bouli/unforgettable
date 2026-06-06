from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_readme_documents_local_ai_agent_tool_contract():
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")

    assert "## Local AI-Agent Tool Contract" in readme
    assert "uvx unforgettable --help" in readme
    assert "uv tool run unforgettable --help" in readme
    assert "unforgettable --help" in readme
    assert "python -m unforgettable --help" in readme
    assert "unforgettable --version" in readme
    assert "Missing cache IDs for `get` exit with status code `1`." in readme
    assert "Missing cache IDs for `exists` exit with status code `1`." in readme
    assert "Missing cache IDs for `delete` exit with status code `1`." in readme
    assert "Missing cache IDs for `info` exit with status code `1`." in readme
    assert "Import failures exit with status code `1`." in readme
    assert (
        "Invalid usage, such as missing required arguments, exits with status code `2`."
        in readme
    )
    assert "Command values are written to stdout." in readme
    assert "Diagnostics, errors, and prompts are written to stderr." in readme
    assert "--create-cache-folder" in readme
    assert "--no-create-cache-folder" in readme
    assert "set notes --stdin" in readme
    assert "exists notes" in readme
    assert "delete notes" in readme
    assert "info notes" in readme
    assert "export" in readme
    assert "import --stdin" in readme
    assert "--output json" in readme
    assert '{"cache_id": "notes", "exists": true}' in readme
    assert '{"entries": []}' in readme
    assert '"content_type": "text/plain"' in readme
    assert '{"cache_ids": ["notes"]}' in readme


def test_readme_documents_release_verification_checklist():
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")

    assert "### Release Verification" in readme
    assert "uv tool run unforgettable --help" in readme
    assert "uv tool run unforgettable --version" in readme
    assert "uvx unforgettable --help" in readme
    assert "uvx unforgettable --version" in readme
    assert "If `uvx` is not installed" in readme
    assert "unforgettable --help` after installing the built wheel" in readme
    assert "python -m unforgettable --help` after installing the built wheel" in readme
    assert "unforgettable --version` after installing the built wheel" in readme
    assert "tests/test_packaging.py" in readme
    assert "verifies installed console script, module execution, and version output" in readme
