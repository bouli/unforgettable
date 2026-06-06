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
    assert (
        "Invalid usage, such as missing required arguments, exits with status code `2`."
        in readme
    )
    assert "Command values are written to stdout." in readme
    assert "Diagnostics, errors, and prompts are written to stderr." in readme
    assert "--create-cache-folder" in readme
    assert "--no-create-cache-folder" in readme
    assert "set notes --stdin" in readme
    assert "--output json" in readme
    assert '{"cache_ids": ["notes"]}' in readme
