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
    assert "AUTHORITY SNAPSHOT" in payload["summary"]


def test_scan_mcp_broad_args_is_security_finding(tmp_path: Path):
    """Local MCP + broad filesystem args escalate beyond a capability observation."""
    root = (
        Path(__file__).resolve().parents[1]
        / "tests"
        / "benchmark"
        / "fixtures"
        / "skill-to-mcp-path"
    )
    out = tmp_path / "aesa-out"
    scan, _payload, _code = run_scan(root, output_dir=out)
    mcp = next(f for f in scan.findings if f.rule_id == "AESA-RULE-002")
    assert mcp.finding_class == "SECURITY_FINDING"
    assert mcp.severity == "HIGH"
    # Evidence should carry content digest when the source file is readable.
    ev = next(e for e in scan.evidences if e.evidence_id == mcp.evidence_ids[0])
    assert ev.content_digest and ev.content_digest.startswith("sha256:")
    assert ev.file_path


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


def test_capability_origin_on_type_defaults(tmp_path: Path):
    root = (
        Path(__file__).resolve().parents[1]
        / "tests"
        / "benchmark"
        / "fixtures"
        / "benign-skill-only"
    )
    out = tmp_path / "aesa-out"
    scan, _payload, _code = run_scan(root, output_dir=out)
    skill_caps = [c for c in scan.capabilities if c.kind == "modify_agent_instructions"]
    assert skill_caps
    assert skill_caps[0].origin == "TYPE_DEFAULT"


def test_baseline_fingerprints(tmp_path: Path):
    from aesa.security.baseline import diff_against_baseline, save_baseline

    root = (
        Path(__file__).resolve().parents[1]
        / "tests"
        / "benchmark"
        / "fixtures"
        / "skill-to-mcp-path"
    )
    out = tmp_path / "aesa-out"
    scan, _payload, _code = run_scan(root, output_dir=out)
    comps = scan.inventory.get("components") or []
    assert comps
    assert all(c.get("fingerprint") for c in comps)
    baseline_file = out / "baseline.json"
    doc = save_baseline(scan, baseline_file)
    assert doc["baseline_version"] == "1.3"
    assert doc["component_fingerprints"]
    delta = diff_against_baseline(scan, doc)
    assert delta["summary"]["findings_added"] == 0


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
