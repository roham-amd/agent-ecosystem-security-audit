"""Single source of truth for which findings may block CI / annotate PRs.

Capability observations are inventory — they never gate by default.
"""

from __future__ import annotations

from typing import Any, Protocol

GATE_FINDING_CLASSES: frozenset[str] = frozenset({"SECURITY_FINDING", "EXPOSURE"})
HIGH_SEVERITIES: frozenset[str] = frozenset({"CRITICAL", "HIGH"})


class _GateFinding(Protocol):
    finding_class: str
    severity: str


def is_gate_finding(finding: _GateFinding | dict[str, Any]) -> bool:
    """True when the finding may participate in fail-on / annotations."""
    if isinstance(finding, dict):
        fclass = str(finding.get("finding_class") or "")
        return fclass in GATE_FINDING_CLASSES
    return finding.finding_class in GATE_FINDING_CLASSES


def is_high_gate_finding(finding: _GateFinding | dict[str, Any]) -> bool:
    """True for CRITICAL/HIGH gate findings (``fail_on=high``)."""
    if not is_gate_finding(finding):
        return False
    if isinstance(finding, dict):
        return str(finding.get("severity") or "") in HIGH_SEVERITIES
    return finding.severity in HIGH_SEVERITIES


def gated_findings(findings: list[Any]) -> list[Any]:
    return [f for f in findings if is_gate_finding(f)]


def high_gate_findings(findings: list[Any]) -> list[Any]:
    return [f for f in findings if is_high_gate_finding(f)]


def compute_exit_code(
    fail_on: str | None,
    *,
    findings: list[Any],
    risk_delta_summary: dict[str, Any] | None = None,
) -> int:
    """Compute process exit code for ``fail_on`` policy.

    Baseline deltas and absolute scan checks use the **same** gate classes:
    CAPABILITY never blocks. ``fail_on=any`` with a baseline uses gated
    findings added (not every fingerprint key).
    """
    if fail_on not in {"high", "any"}:
        return 0
    exit_code = 0
    if risk_delta_summary is not None:
        if fail_on == "high" and risk_delta_summary.get("high_or_critical_findings_added"):
            exit_code = 1
        if fail_on == "any" and risk_delta_summary.get("gated_findings_added"):
            exit_code = 1
    if (fail_on == "high" and high_gate_findings(findings)) or (
        fail_on == "any" and gated_findings(findings)
    ):
        exit_code = 1
    return exit_code
