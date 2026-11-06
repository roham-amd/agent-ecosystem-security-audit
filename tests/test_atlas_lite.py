"""Mini-Atlas regression: benign corpus must not BLOCK; attacks must gate."""

from __future__ import annotations

from pathlib import Path

from aesa.security.decision import compute_decision
from aesa.security.gating import is_high_gate_finding
from aesa.security.scan import run_scan

_ATLAS = Path(__file__).resolve().parent / "atlas"


def test_benign_corpus_never_blocks(tmp_path: Path):
    for fixture in sorted((_ATLAS / "benign").iterdir()):
        if not fixture.is_dir():
            continue
        scan, _payload, _code = run_scan(fixture, output_dir=tmp_path / fixture.name)
        decision = compute_decision(scan.findings, coverage=scan.coverage)
        assert decision != "BLOCK", f"{fixture.name} BLOCKED: {[f.rule_id for f in scan.findings]}"
        assert not any(is_high_gate_finding(f) for f in scan.findings), fixture.name


def test_attack_fixtures_gate(tmp_path: Path):
    expected = {
        "sessionstart-env-exfil": {"AESA-RULE-015", "AESA-RULE-004"},
        "mcp-auto-approve": {"AESA-RULE-018", "AESA-RULE-017"},
        "base-url-override": {"AESA-RULE-019"},
    }
    for name, rules in expected.items():
        fixture = _ATLAS / "attacks" / name
        scan, _payload, _code = run_scan(fixture, output_dir=tmp_path / name)
        fired = {f.rule_id for f in scan.findings}
        assert rules & fired, f"{name}: expected one of {rules}, got {fired}"
        decision = compute_decision(scan.findings, coverage=scan.coverage)
        assert decision in {"BLOCK", "REVIEW"}, f"{name} decision={decision}"
