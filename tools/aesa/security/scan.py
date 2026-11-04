"""Write AESA Guard scan artifacts and optional SARIF / baseline diff."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from aesa.export.sarif import findings_doc_to_sarif
from aesa.jsonio import write_json, write_text
from aesa.paths import resolve_default_output_dir
from aesa.policy import AesaPolicy
from aesa.security.baseline import diff_against_baseline, load_baseline, save_baseline
from aesa.security.engine import ScanResult, run_security_scan
from aesa.security.gating import compute_exit_code
from aesa.security.report import render_markdown_summary, render_terminal_report


def write_scan_artifacts(scan: ScanResult, output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    findings_doc = scan.to_findings_doc()
    summary = render_terminal_report(scan)
    write_json(output_dir / "inventory.json", scan.inventory)
    write_json(output_dir / "ecosystem-graph.json", scan.graph)
    write_json(output_dir / "findings.json", findings_doc)
    write_json(output_dir / "capabilities.json", {"capabilities": findings_doc["capabilities"]})
    write_text(output_dir / "scan-report.md", render_markdown_summary(scan, terminal=summary))
    write_text(output_dir / "scan-summary.txt", summary)
    write_json(output_dir / "findings.sarif.json", findings_doc_to_sarif(findings_doc))
    write_json(
        output_dir / "profile.json",
        {
            "aesa_audit_profile": "scan",
            "product": "AESA Guard",
            "product_version": scan.product_version,
            "package_version": scan.package_version,
            "purpose": "One-command discovery + deterministic security observations",
            "deliverable": "Terminal report, findings.json, SARIF, inventory, graph seed",
            "rules_applied": scan.rules_applied,
            "limitations": findings_doc["limitations"],
        },
    )
    return {
        "output_dir": str(output_dir),
        "finding_count": len(scan.findings),
        "component_count": len(scan.inventory.get("components") or []),
        "summary": summary,
    }


def _evidence_paths(scan: ScanResult, finding_evidence_ids: list[str]) -> list[str]:
    wanted = set(finding_evidence_ids)
    return [ev.file_path for ev in scan.evidences if ev.evidence_id in wanted and ev.file_path]


def apply_suppressions(scan: ScanResult, policy: AesaPolicy | None) -> list[dict[str, str]]:
    """Remove suppressed findings in-place; return suppression audit records."""
    if policy is None or not policy.suppressions:
        return []
    kept = []
    records: list[dict[str, str]] = []
    for finding in scan.findings:
        match = policy.applies_to_finding(
            rule_id=finding.rule_id,
            evidence_paths=_evidence_paths(scan, finding.evidence_ids),
        )
        if match is None:
            kept.append(finding)
            continue
        records.append(
            {
                "finding_id": finding.finding_id,
                "rule_id": finding.rule_id,
                "path": match.path,
                "justification": match.justification,
                "owner": match.owner,
            }
        )
    scan.findings[:] = kept
    return records


def run_scan(
    target: Path,
    *,
    output_dir: Path | None = None,
    baseline: Path | None = None,
    save_baseline_path: Path | None = None,
    fail_on: str | None = None,
    policy: AesaPolicy | None = None,
) -> tuple[ScanResult, dict[str, Any], int]:
    """Run scan; return (scan, payload, exit_code).

    Default ``output_dir`` is ``./aesa-out`` relative to the process cwd — not
    ``<target>/aesa-out`` — so scanning an external repository stays read-only
    with respect to the target tree.
    """
    scan = run_security_scan(target)
    suppressed = apply_suppressions(scan, policy)
    out = (output_dir or resolve_default_output_dir()).resolve()
    payload = write_scan_artifacts(scan, out)
    if suppressed:
        write_json(out / "suppressions.json", {"suppressions": suppressed})
        payload["suppressions"] = suppressed
    if policy and policy.source_path:
        payload["policy_path"] = str(policy.source_path)
        payload["policy_mode"] = policy.mode
    if policy and policy.require_review:
        payload["require_review"] = list(policy.require_review)

    risk_delta_summary: dict[str, Any] | None = None
    if baseline and baseline.is_file():
        delta = diff_against_baseline(scan, load_baseline(baseline))
        write_json(out / "risk-delta.json", delta)
        risk_delta_summary = delta["summary"]
        payload["risk_delta"] = risk_delta_summary

    if save_baseline_path is not None:
        save_baseline(scan, save_baseline_path)
        payload["baseline_saved"] = str(save_baseline_path)

    exit_code = compute_exit_code(
        fail_on,
        findings=scan.findings,
        risk_delta_summary=risk_delta_summary,
    )
    return scan, payload, exit_code
