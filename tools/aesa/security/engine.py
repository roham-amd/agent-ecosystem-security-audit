"""Orchestrate inventory → capabilities → rules → scan artifacts."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from aesa.inventory.collector import collect_inventory, inventory_to_json
from aesa.preflight import inventory_to_graph, resolve_git_commit
from aesa.security.capabilities import authority_bearing_component_ids, extract_capabilities
from aesa.security.models import Capability, Evidence, Finding
from aesa.security.rules import RULES, apply_all_rules
from aesa.versioning import package_version, product_version


@dataclass(slots=True)
class ScanResult:
    repository_path: str
    commit: str | None
    collected_at_utc: str
    inventory: dict[str, Any]
    graph: dict[str, Any]
    capabilities: list[Capability]
    evidences: list[Evidence]
    findings: list[Finding]
    coverage: dict[str, Any]
    authority_bearing_count: int
    external_destination_count: int
    product_version: str
    package_version: str
    rules_applied: list[str]

    def findings_by_severity(self) -> dict[str, int]:
        counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "INFORMATIONAL": 0}
        for finding in self.findings:
            counts[finding.severity] = counts.get(finding.severity, 0) + 1
        return counts

    def to_findings_doc(self) -> dict[str, Any]:
        return {
            "findings_version": "1.0",
            "product": "AESA Guard",
            "product_version": self.product_version,
            "package_version": self.package_version,
            "repository": self.repository_path,
            "audited_commit": self.commit,
            "collected_at_utc": self.collected_at_utc,
            "rules_applied": self.rules_applied,
            "summary": {
                "component_count": len(self.inventory.get("components") or []),
                "authority_bearing_components": self.authority_bearing_count,
                "external_data_destinations": self.external_destination_count,
                "finding_count": len(self.findings),
                "by_severity": self.findings_by_severity(),
            },
            "capabilities": [c.to_dict() for c in self.capabilities],
            "evidence_registry": [e.to_dict() for e in self.evidences],
            "findings": [f.to_dict() for f in self.findings],
            "coverage": self.coverage,
            "limitations": [
                "Deterministic rules produce OBSERVED/POTENTIAL findings, not confirmed exploits.",
                "Host effective permissions and runtime behavior remain NOT VERIFIED.",
                "Incomplete adapter coverage means absence of findings is not evidence of safety.",
            ],
        }

    def finding_by_id(self, finding_id: str) -> Finding | None:
        for finding in self.findings:
            if finding.finding_id == finding_id:
                return finding
        return None


def run_security_scan(target: Path) -> ScanResult:
    target = target.resolve()
    result = collect_inventory(target)
    commit = resolve_git_commit(target)
    inventory = inventory_to_json(result)
    if commit:
        inventory["repository_commit"] = commit

    components = list(result.components)
    capabilities = extract_capabilities(components)
    evidences, findings = apply_all_rules(components)

    # Attach inventory evidence stubs for capability references.
    for comp in components:
        cid = str(comp.get("component_id") or "")
        evidences.append(
            Evidence(
                evidence_id=f"E-INV-{cid}",
                component_id=cid,
                evidence_class="SOURCE_STATIC",
                verification_status="OBSERVED",
                file_path=comp.get("repository_path"),
                collection_method="inventory_adapter",
                source_commit=commit,
                observed_at=result.collected_at_utc,
                summary=f"Component discovered by adapter `{comp.get('adapter')}`.",
                limitations=["Discovery only; does not prove runtime loading."],
            )
        )

    authority_ids = authority_bearing_component_ids(capabilities)
    external = sum(
        1
        for c in capabilities
        if c.kind == "access_network" and c.status in {"OBSERVED", "POTENTIAL", "CONFIRMED"}
    )

    return ScanResult(
        repository_path=str(target),
        commit=commit,
        collected_at_utc=datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        inventory=inventory,
        graph=inventory_to_graph(result, commit=commit, audit_id="scan-guard"),
        capabilities=capabilities,
        evidences=evidences,
        findings=findings,
        coverage=result.coverage or {},
        authority_bearing_count=len(authority_ids),
        external_destination_count=external,
        product_version=product_version(),
        package_version=package_version(),
        rules_applied=[r.rule_id for r in RULES],
    )
