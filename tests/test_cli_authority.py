"""CLI surface tests for doctor / vet / init-gate / scan policy discovery."""

from __future__ import annotations

from pathlib import Path

from aesa.cli import main


def test_cli_doctor_help_and_empty_home(tmp_path: Path, capsys):
    home = tmp_path / "empty-home"
    home.mkdir()
    code = main(["doctor", "--home", str(home)])
    out = capsys.readouterr().out
    assert code == 0
    assert "AESA doctor" in out
    assert "no host config" in out.lower() or "absent" in out.lower()


def test_cli_init_gate_writes_files(tmp_path: Path, capsys):
    root = tmp_path / "repo"
    code = main(["init-gate", str(root)])
    out = capsys.readouterr().out
    assert code == 0
    assert (root / ".aesa.yml").is_file()
    assert (root / ".github" / "workflows" / "aesa-gate.yml").is_file()
    workflow = (root / ".github" / "workflows" / "aesa-gate.yml").read_text(encoding="utf-8")
    assert "trusted-policy" in workflow
    assert "Wrote" in out

    code2 = main(["init-gate", str(root)])
    out2 = capsys.readouterr().out
    assert code2 == 0
    assert "Exists" in out2


def test_cli_vet_local(tmp_path: Path, capsys):
    root = tmp_path / "pkg"
    skill = root / "skills" / "ok"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text("---\nname: ok\n---\nRead-only helper.\n", encoding="utf-8")
    code = main(["vet", str(root), "-o", str(tmp_path / "out")])
    out = capsys.readouterr().out
    assert "AESA vet" in out
    assert "verdict:" in out
    assert code in {0, 1}


def test_cli_scan_ignores_parent_policy(tmp_path: Path, capsys):
    parent = tmp_path / "parent"
    child = parent / "repo"
    child.mkdir(parents=True)
    (parent / ".aesa.yml").write_text(
        "version: 1\npolicy:\n  mode: enforce\n  fail_on: high\n",
        encoding="utf-8",
    )
    (child / "README.md").write_text("x\n", encoding="utf-8")
    code = main(["scan", str(child), "-o", str(tmp_path / "out"), "--fail-on", "never"])
    out = capsys.readouterr().out
    assert code == 0
    assert "Policy:" not in out
