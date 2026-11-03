from pathlib import Path

from aesa.security.scan import run_scan


def test_scan_emits_findings_and_sarif(tmp_path: Path):
    root = (
        Path(__file__).resolve().parents[1]
        / "tests"
        / "benchmark"
        / "fixtures"
        / "skill-to-mcp-path"
    )
    out = tmp_path / "aesa-out"
    scan, payload, code = run_scan(root, output_dir=out)
    assert code == 0
    assert scan.findings
    assert any(f.rule_id == "AESA-RULE-002" for f in scan.findings)
    assert (out / "findings.json").is_file()
    assert (out / "findings.sarif.json").is_file()
    assert (out / "scan-summary.txt").is_file()
    assert "AESA Guard" in payload["summary"]


def test_scan_benign_skill_no_mcp_rules(tmp_path: Path):
    root = (
        Path(__file__).resolve().parents[1]
        / "tests"
        / "benchmark"
        / "fixtures"
        / "benign-skill-only"
    )
    out = tmp_path / "aesa-out"
    scan, _payload, code = run_scan(root, output_dir=out)
    assert code == 0
    fired = {f.rule_id for f in scan.findings}
    assert "AESA-RULE-002" not in fired
    assert "AESA-RULE-003" not in fired


def test_scan_fail_on_high(tmp_path: Path):
    root = (
        Path(__file__).resolve().parents[1]
        / "tests"
        / "benchmark"
        / "fixtures"
        / "skill-to-mcp-path"
    )
    out = tmp_path / "aesa-out"
    _scan, _payload, code = run_scan(root, output_dir=out, fail_on="high")
    assert code == 1


def test_validate_claim_confirmed_requires_evidence(tmp_path: Path):
    from aesa.cli.dispatch import _validate_claim
    from aesa.jsonio import write_json

    path = tmp_path / "claim.json"
    write_json(
        path,
        {
            "claim": "Can execute commands",
            "status": "CONFIRMED",
            "evidence_ids": [],
        },
    )
    ok, issues = _validate_claim(path)
    assert not ok
    assert any(i.code == "CLAIM_UNSUPPORTED_CONFIRMED" for i in issues)
