from __future__ import annotations

from typing import Any

_SARIF_SEVERITY = {
    "CRITICAL": "error",
    "HIGH": "error",
    "MEDIUM": "warning",
    "LOW": "note",
    "INFORMATIONAL": "note",
}


def report_to_sarif(report: dict[str, Any], *, tool_version: str = "3.0.0") -> dict[str, Any]:
    evidence_by_id = {
        e["evidence_id"]: e for e in report.get("evidence_registry") or [] if e.get("evidence_id")
    }
    rules: dict[str, dict] = {}
    results: list[dict] = []

    for finding in report.get("findings") or []:
        fid = finding.get("finding_id", "UNKNOWN")
        rule_id = f"aesa/{fid}"
        rules[rule_id] = {
            "id": rule_id,
            "name": finding.get("title", fid),
            "shortDescription": {"text": finding.get("title", fid)},
        }
        locations: list[dict] = []
        for eid in finding.get("evidence_ids") or []:
            ev = evidence_by_id.get(eid)
            if not ev:
                continue
            path = ev.get("path_or_source")
            if not path:
                continue
            region: dict[str, int] = {}
            if ev.get("line_start"):
                region["startLine"] = int(ev["line_start"])
            if ev.get("line_end"):
                region["endLine"] = int(ev["line_end"])
            loc = {
                "physicalLocation": {
                    "artifactLocation": {"uri": path},
                }
            }
            if region:
                loc["physicalLocation"]["region"] = region
            locations.append(loc)
        if not locations:
            continue
        results.append(
            {
                "ruleId": rule_id,
                "level": _SARIF_SEVERITY.get(finding.get("severity", "INFORMATIONAL"), "note"),
                "message": {"text": finding.get("description") or finding.get("title") or fid},
                "locations": locations,
            }
        )

    return {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "AESA",
                        "version": tool_version,
                        "informationUri": "https://github.com/roham-amd/agent-ecosystem-security-audit",
                        "rules": list(rules.values()),
                    }
                },
                "results": results,
            }
        ],
    }
