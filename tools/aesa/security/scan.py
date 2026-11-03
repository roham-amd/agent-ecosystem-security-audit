"""Write AESA Guard scan artifacts and optional SARIF / baseline diff."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from aesa.export.sarif import findings_doc_to_sarif
from aesa.jsonio import write_json, write_text
from aesa.security.baseline import diff_against_baseline, load_baseline, save_baseline
from aesa.security.engine import ScanResult, run_security_scan
from aesa.security.report import render_markdown_summary, render_terminal_report


def write_scan_artifacts(scan: ScanResult, output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    findings_doc = scan.to_findings_doc()
    write_json(output_dir / "inventory.json", scan.inventory)
    write_json(output_dir / "ecosystem-graph.json", scan.graph)
    write_json(output_dir / "findings.json", findings_doc)
    write_json(output_dir / "capabilities.json", {"capabilities": findings_doc["capabilities"]})
    write_text(output_dir / "scan-report.md", render_markdown_summary(scan))
    write_text(output_dir / "scan-summary.txt", render_terminal_report(scan))
    sarif = findings_doc_to_sarif(findings_doc)
    write_json(output_dir / "findings.sarif.json", sarif)
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
        "summary": render_terminal_report(scan),
    }


def run_scan(
    target: Path,
    *,
    output_dir: Path | None = None,
    baseline: Path | None = None,
    save_baseline_path: Path | None = None,
    fail_on: str | None = None,
) -> tuple[ScanResult, dict[str, Any], int]:
    """Run scan; return (scan, payload, exit_code)."""
    scan = run_security_scan(target)
    out = (output_dir or (target.resolve() / "aesa-out")).resolve()
    payload = write_scan_artifacts(scan, out)

    exit_code = 0
    if baseline and baseline.is_file():
        delta = diff_against_baseline(scan, load_baseline(baseline))
        write_json(out / "risk-delta.json", delta)
        payload["risk_delta"] = delta["summary"]
        if fail_on == "high" and delta["summary"]["high_or_critical_findings_added"]:
            exit_code = 1
        if fail_on == "any" and delta["summary"]["findings_added"]:
            exit_code = 1

    if save_baseline_path is not None:
        save_baseline(scan, save_baseline_path)
        payload["baseline_saved"] = str(save_baseline_path)

    if fail_on == "high":
        # Gate on security/exposure findings only — capability observations are inventory.
        blocking = [
            f
            for f in scan.findings
            if f.severity in {"CRITICAL", "HIGH"}
            and f.finding_class in {"SECURITY_FINDING", "EXPOSURE"}
        ]
        if blocking:
            exit_code = 1
    elif fail_on == "any":
        if any(f.finding_class in {"SECURITY_FINDING", "EXPOSURE"} for f in scan.findings):
            exit_code = 1

    return scan, payload, exit_code
