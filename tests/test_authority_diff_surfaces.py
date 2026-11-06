from pathlib import Path

from aesa.export.agent_digest import fence_untrusted, render_agent_digest
from aesa.export.pr_comment import escape_markdown, render_authority_diff_comment
from aesa.harden import propose_patches, run_harden
from aesa.security.decision import compute_decision
from aesa.security.scan import run_scan


def test_escape_markdown_strips_links_and_mentions():
    raw = "See https://evil.example and ping @admin for ![x](y)"
    out = escape_markdown(raw)
    assert "https://" not in out
    assert "@admin" not in out
    assert fence_untrusted("ignore previous").startswith("<untrusted_evidence>")


def _demo_root() -> Path:
    return Path(__file__).resolve().parents[1] / "examples" / "demo-vulnerable"


def test_pr_comment_is_compact_and_decision_led(tmp_path: Path):
    demo = _demo_root()
    assert demo.is_dir()
    scan, payload, _code = run_scan(demo, output_dir=tmp_path / "out")
    comment = payload.get("pr_comment") or render_authority_diff_comment(scan.to_findings_doc())
    assert "Decision:" in comment
    assert len(comment.strip().splitlines()) <= 12
    assert compute_decision(scan.findings, coverage=scan.coverage) in {
        "BLOCK",
        "REVIEW",
        "NO-GATED-FINDINGS",
        "PASS-WITH-COVERAGE-GAPS",
    }


def test_agent_digest_fences_titles(tmp_path: Path):
    demo = _demo_root()
    assert demo.is_dir()
    scan, _payload, _code = run_scan(demo, output_dir=tmp_path / "out")
    digest = render_agent_digest(scan.to_findings_doc())
    assert digest["decision"] in {
        "BLOCK",
        "REVIEW",
        "NO-GATED-FINDINGS",
        "PASS-WITH-COVERAGE-GAPS",
    }
    assert digest["safety"]["evidence_fenced"] is True
    if digest["gated_findings"]:
        assert "<untrusted_evidence>" in digest["gated_findings"][0]["title"]


def test_harden_proposes_for_demo(tmp_path: Path):
    demo = _demo_root()
    assert demo.is_dir()
    scan, payload, _code = run_scan(demo, output_dir=tmp_path / "out")
    proposals = propose_patches(scan.to_findings_doc())
    assert proposals
    text, code = run_harden(findings_path=Path(payload["output_dir"]) / "findings.json")
    assert code == 0
    assert "AESA harden" in text


def test_rule_017_permission_bypass(tmp_path: Path):
    root = Path(__file__).resolve().parents[0] / "rules" / "fixtures"
    fixture = root / "rule-017-positive-bypass"
    scan, _payload, _code = run_scan(fixture, output_dir=tmp_path / "pos")
    assert any(f.rule_id == "AESA-RULE-017" for f in scan.findings)
    neg = root / "rule-017-negative-safe"
    scan_n, _p, _c = run_scan(neg, output_dir=tmp_path / "neg")
    assert not any(f.rule_id == "AESA-RULE-017" for f in scan_n.findings)
