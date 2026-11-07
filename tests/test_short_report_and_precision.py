"""Week-4: short default report + Atlas precision gate."""

from __future__ import annotations

import json
from pathlib import Path

from aesa.cli import main
from aesa.security.report import render_short_terminal_report, render_terminal_report
from aesa.security.scan import run_scan


def _demo() -> Path:
    return Path(__file__).resolve().parents[1] / "examples" / "demo-vulnerable"


def test_default_report_is_short(tmp_path: Path):
    _scan, payload, _code = run_scan(_demo(), output_dir=tmp_path / "out")
    short = payload["summary"]
    assert "DECISION:" in short
    assert len(short.splitlines()) <= 15
    full_path = tmp_path / "out" / "scan-summary-full.txt"
    assert full_path.is_file()
    assert "AUTHORITY SURFACES" in full_path.read_text(encoding="utf-8")
    assert "AUTHORITY SURFACES" not in short


def test_full_flag_lengthens_report(tmp_path: Path):
    scan, _p, _c = run_scan(_demo(), output_dir=tmp_path / "out", full_report=True)
    text = render_terminal_report(scan, full=True)
    assert len(text.splitlines()) > 30
    assert render_short_terminal_report(scan).count("\n") < text.count("\n")


def test_precision_gate_passes_when_unlabeled():
    path = Path(__file__).resolve().parents[1] / "docs" / "atlas" / "precision.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    policy = data["policy"]
    assert policy["high_critical_require_literal_config"] is True
    labeled = sum(int(r.get("labeled_n") or 0) for r in data["rules"])
    # Until N>=100, gate only checks schema honesty — do not invent precision.
    if labeled < int(policy["min_labeled_for_gate"]):
        assert all(
            r.get("precision") in (None, 0) or r.get("labeled_n", 0) == 0 for r in data["rules"]
        )
        return
    threshold = float(policy["demote_below_precision"])
    for rule in data["rules"]:
        prec = rule.get("precision")
        if prec is None:
            continue
        if float(prec) < threshold:
            assert rule.get("default_severity") in {"LOW", "demote", "keep-low"}


def test_product_cli_hides_maintainer_commands():
    from aesa.cli.parser import build_parser

    product = build_parser(include_dev=False)
    assert "lock" in product.format_help()
    try:
        product.parse_args(["build", "all"])
        ok = True
    except SystemExit:
        ok = False
    assert ok is False
    dev = build_parser(include_dev=True)
    args = dev.parse_args(["build", "all"])
    assert args.command == "build"


def test_init_gate_writes_codeowners(tmp_path: Path):
    root = tmp_path / "repo"
    root.mkdir()
    assert main(["ci", "init", str(root)]) == 0
    assert (root / ".aesa.yml").is_file()
    assert (root / ".github" / "workflows" / "aesa-gate.yml").is_file()
    owners = (root / ".github" / "CODEOWNERS").read_text(encoding="utf-8")
    assert "AUTHORITY.lock" in owners
