"""Human-readable terminal and markdown reports for AESA Guard scans."""

from __future__ import annotations

from aesa.security.engine import ScanResult
from aesa.security.models import Finding


def render_terminal_report(scan: ScanResult) -> str:
    counts = scan.inventory.get("coverage", {}).get("component_counts_by_type") or {}
    sev = scan.findings_by_severity()
    lines = [
        "AESA Guard — Agent Ecosystem Security Scan",
        f"Product: AESA Guard {scan.product_version}  (tooling {scan.package_version})",
        f"Repository: {scan.repository_path}",
        f"Commit: {scan.commit or 'unknown'}",
        "",
        "ECOSYSTEM SUMMARY",
        f"  Components discovered              {len(scan.inventory.get('components') or [])}",
        f"  Authority-bearing components       {scan.authority_bearing_count}",
        f"  External data destinations         {scan.external_destination_count}",
        f"  High-priority review candidates    {sev.get('CRITICAL', 0) + sev.get('HIGH', 0)}",
        "",
        "COMPONENTS BY TYPE",
    ]
    if counts:
        width = max(len(str(k)) for k in counts) + 2
        for name, count in sorted(counts.items()):
            lines.append(f"  {str(name).ljust(width)}{count}")
    else:
        lines.append("  (none discovered by deterministic adapters)")

    lines.extend(
        [
            "",
            "FINDINGS",
            f"  CRITICAL {sev.get('CRITICAL', 0)}  HIGH {sev.get('HIGH', 0)}  "
            f"MEDIUM {sev.get('MEDIUM', 0)}  LOW {sev.get('LOW', 0)}",
        ]
    )
    if not scan.findings:
        lines.append("  No deterministic rule findings. This is NOT a clean bill of health.")
    else:
        for finding in scan.findings[:12]:
            lines.append(
                f"  [{finding.severity}/{finding.confidence}] {finding.finding_id} {finding.title}"
            )
            path = ""
            if finding.evidence_ids:
                for ev in scan.evidences:
                    if ev.evidence_id == finding.evidence_ids[0] and ev.file_path:
                        path = ev.file_path
                        break
            if path:
                lines.append(f"      evidence: {path}")
            lines.append(f"      action: {finding.recommended_action}")

    coverage = scan.coverage
    lines.extend(
        [
            "",
            "COVERAGE",
            f"  Deterministically discovered  {coverage.get('deterministically_discovered', 0)}",
            f"  Adapter maturity              {coverage.get('component_counts_by_maturity')}",
            "",
            "NOT VERIFIED",
        ]
    )
    for item in coverage.get("not_verified") or ["(see inventory coverage)"]:
        lines.append(f"  - {item}")

    lines.extend(
        [
            "",
            "IMPORTANT",
            "  Deterministic findings are OBSERVED/POTENTIAL evidence, not confirmed exploits.",
            "  Incomplete coverage never equals safety. Use `aesa explain F-00N` for detail.",
            "  Optional AI deep review: attach skills/aesa-auditor after this scan.",
            "",
        ]
    )
    return "\n".join(lines)


def render_finding_explanation(scan: ScanResult, finding: Finding) -> str:
    evidence_lines: list[str] = []
    for eid in finding.evidence_ids:
        for ev in scan.evidences:
            if ev.evidence_id == eid:
                evidence_lines.append(
                    f"- `{ev.evidence_id}` [{ev.evidence_class}/{ev.verification_status}] "
                    f"{ev.file_path or '(no path)'}: {ev.summary}"
                )
                for lim in ev.limitations:
                    evidence_lines.append(f"  limitation: {lim}")
    lines = [
        f"# {finding.finding_id}: {finding.title}",
        "",
        f"- Rule: `{finding.rule_id}`",
        f"- Severity: **{finding.severity}**",
        f"- Confidence: **{finding.confidence}**",
        f"- Components: {', '.join(finding.component_ids) or '(none)'}",
        f"- Capabilities: {', '.join(finding.capabilities) or '(none)'}",
        "",
        "## Description",
        "",
        finding.description,
        "",
        "## Attack path reasoning",
        "",
        f"1. Attacker control: {finding.attacker_control or 'NOT VERIFIED'}",
        f"2. Entry point: {finding.entry_point or 'NOT VERIFIED'}",
        f"3. Trust boundary: {finding.trust_boundary or 'NOT VERIFIED'}",
        f"4. Impact: {finding.impact or 'NOT VERIFIED'}",
        "",
        "## Missing controls / evidence",
        "",
    ]
    for item in finding.missing_controls or ["(none listed)"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Evidence", ""])
    lines.extend(evidence_lines or ["- (no evidence records)"])
    lines.extend(
        [
            "",
            "## Recommended action",
            "",
            finding.recommended_action or "(none)",
            "",
            "## Next steps",
            "",
            "- Do not promote this to CONFIRMED without independent verification.",
            "- Optional: load matching `modules/*.md` and investigate with the auditor skill.",
            "",
        ]
    )
    return "\n".join(lines)


def render_markdown_summary(scan: ScanResult) -> str:
    terminal = render_terminal_report(scan)
    lines = [
        "# AESA Guard scan summary",
        "",
        "```text",
        terminal.rstrip(),
        "```",
        "",
        "## Top findings",
        "",
    ]
    if not scan.findings:
        lines.append("No deterministic findings.")
    else:
        for finding in scan.findings:
            lines.append(
                f"- **{finding.finding_id}** [{finding.severity}/{finding.confidence}] "
                f"{finding.title}"
            )
            lines.append(f"  - {finding.recommended_action}")
    lines.extend(
        [
            "",
            "## Executive questions (still require human judgment)",
            "",
            "1. What is the overall situation given coverage limits?",
            "2. What are the three biggest risks above?",
            "3. Can this system be used in the intended context?",
            "4. What must happen before deployment?",
            "",
        ]
    )
    return "\n".join(lines)
