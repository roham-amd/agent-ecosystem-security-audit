"""Baseline save / load / risk-aware diff for recurring AESA Guard assessments."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from aesa.jsonio import read_json, write_json
from aesa.security.engine import ScanResult


def baseline_path(output_dir: Path) -> Path:
    return output_dir / "baseline.json"


def save_baseline(scan: ScanResult, path: Path) -> dict[str, Any]:
    doc = {
        "baseline_version": "1.0",
        "saved_at_utc": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "product": "AESA Guard",
        "product_version": scan.product_version,
        "repository": scan.repository_path,
        "audited_commit": scan.commit,
        "component_keys": sorted(
            {
                (c.get("repository_path") or c.get("name") or c.get("component_id") or "")
                for c in scan.inventory.get("components") or []
            }
        ),
        "finding_keys": sorted({f"{f.rule_id}:{','.join(f.component_ids)}" for f in scan.findings}),
        "findings": [f.to_dict() for f in scan.findings],
        "summary": scan.to_findings_doc()["summary"],
        "limitations": [
            "Baseline identity is path/name + rule/component keys; renames look like churn.",
        ],
    }
    write_json(path, doc)
    return doc


def load_baseline(path: Path) -> dict[str, Any]:
    return read_json(path)


def diff_against_baseline(scan: ScanResult, baseline: dict[str, Any]) -> dict[str, Any]:
    current_components = {
        (c.get("repository_path") or c.get("name") or c.get("component_id") or "")
        for c in scan.inventory.get("components") or []
    }
    base_components = set(baseline.get("component_keys") or [])
    current_findings = {f"{f.rule_id}:{','.join(f.component_ids)}" for f in scan.findings}
    base_findings = set(baseline.get("finding_keys") or [])

    added_findings = sorted(current_findings - base_findings)
    removed_findings = sorted(base_findings - current_findings)
    added_components = sorted(current_components - base_components)
    removed_components = sorted(base_components - current_components)

    high_new = [
        f.to_dict()
        for f in scan.findings
        if f"{f.rule_id}:{','.join(f.component_ids)}" in set(added_findings)
        and f.severity in {"CRITICAL", "HIGH"}
    ]

    return {
        "diff_version": "1.0",
        "kind": "aesa_guard_risk_delta",
        "base": {
            "saved_at_utc": baseline.get("saved_at_utc"),
            "audited_commit": baseline.get("audited_commit"),
        },
        "target": {
            "audited_commit": scan.commit,
            "collected_at_utc": scan.collected_at_utc,
        },
        "summary": {
            "components_added": len(added_components),
            "components_removed": len(removed_components),
            "findings_added": len(added_findings),
            "findings_removed": len(removed_findings),
            "high_or_critical_findings_added": len(high_new),
        },
        "changes": {
            "components_added": added_components,
            "components_removed": removed_components,
            "findings_added": added_findings,
            "findings_removed": removed_findings,
            "high_or_critical_new_findings": high_new,
        },
        "policy_hints": {
            "block_if_high_or_critical_added": len(high_new) > 0,
            "incomplete_coverage": bool(scan.coverage.get("not_verified")),
        },
        "limitations": [
            "Risk delta is deterministic-rule based; AI semantic findings are not included.",
        ],
    }
