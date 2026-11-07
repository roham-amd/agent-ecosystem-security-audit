"""AUTHORITY.lock write / check / diff (north-star direction 1 MVP)."""

from __future__ import annotations

import json
from pathlib import Path

from aesa.authority_lock import (
    build_authority_lock,
    check_locked,
    diff_authority_locks,
    write_authority_lock,
)
from aesa.cli import main


def _repo_with_mcp(root: Path, servers: dict) -> None:
    path = root / ".cursor" / "mcp.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"mcpServers": servers}, indent=2) + "\n", encoding="utf-8")


def test_lock_write_check_and_diff(tmp_path: Path):
    root = tmp_path / "repo"
    _repo_with_mcp(
        root,
        {
            "echo": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-everything@1.0.0"],
            }
        },
    )
    dest, lock = write_authority_lock(root)
    assert dest.name == "AUTHORITY.lock"
    assert lock["version"] == 2
    assert lock["records"]
    assert any(r["name"] == "echo" for r in lock["records"])

    report, code = check_locked(root)
    assert code == 0
    assert report["verdict"] == "LOCKED"

    _repo_with_mcp(
        root,
        {
            "echo": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-everything@1.0.0"],
            },
            "newcomer": {"command": "npx", "args": ["-y", "evil-pkg"]},
        },
    )
    report2, code2 = check_locked(root)
    assert code2 == 1
    assert report2["verdict"] == "AUTHORITY_CHANGED"
    assert any(line.startswith("+") for line in report2["lines"])

    head = build_authority_lock(root)
    delta = diff_authority_locks(lock, head)
    assert delta["summary"]["records_added"] >= 1
    assert delta["summary"]["authority_changed"] is True


def test_lock_cli_roundtrip(tmp_path: Path):
    root = tmp_path / "repo"
    _repo_with_mcp(root, {"x": {"command": "node", "args": ["x.js"]}})
    assert main(["lock", str(root)]) == 0
    assert (root / "AUTHORITY.lock").is_file()
    assert main(["lock", str(root), "--check"]) == 0
    assert (
        main(["check", str(root), "--locked", "-o", str(tmp_path / "out"), "--fail-on", "never"])
        == 0
    )

    _repo_with_mcp(
        root,
        {
            "x": {"command": "node", "args": ["x.js"]},
            "y": {"command": "node", "args": ["y.js"]},
        },
    )
    assert main(["lock", str(root), "--check"]) == 1
    assert (
        main(["check", str(root), "--locked", "-o", str(tmp_path / "out2"), "--fail-on", "never"])
        == 1
    )
