"""Human-readable terminal and markdown reports for AESA Guard scans."""

from __future__ import annotations

from aesa.security.engine import ScanResult
from aesa.security.models import Finding


def _evidence_path(scan: ScanResult, finding: Finding) -> str:
    if not finding.evidence_ids:
        return ""
    for ev in scan.evidences:
        if ev.evidence_id == finding.evidence_ids[0]:
            parts = [ev.file_path or ""]
            if ev.line_start:
                span = str(ev.line_start)
                if ev.line_end and ev.line_end != ev.line_start:
                    span = f"{ev.line_start}-{ev.line_end}"
                parts.append(f":{span}")
            return "".join(parts)
    return ""


def _authority_path_example(scan: ScanResult) -> list[str]:
    """First high-value finding rendered as a short authority path."""
    candidates = [
        f
        for f in scan.findings
        if f.finding_class in {"SECURITY_FINDING", "EXPOSURE"}
        and f.severity in {"CRITICAL", "HIGH", "MEDIUM"}
    ]
    if not candidates:
        candidates = list(scan.findings[:1])
    if not candidates:
        return []
    finding = candidates[0]
    path = _evidence_path(scan, finding)
    return [
        "",
        "EXAMPLE AUTHORITY PATH",
        f"  {finding.entry_point or path or finding.title}",
        f"  → {finding.trust_boundary or 'trust boundary not established'}",
        f"  → {finding.impact or 'impact not established'}",
        f"  [{finding.finding_class}] {finding.finding_id}: {finding.title}",
        f"  Next: {finding.recommended_action}",
    ]


def render_terminal_report(scan: ScanResult) -> str:
    counts = scan.inventory.get("coverage", {}).get("component_counts_by_type") or {}
    sev = scan.findings_by_severity()
    by_class = scan.findings_by_class()
    high_priority = sum(
        1
        for f in scan.findings
        if f.severity in {"CRITICAL", "HIGH"}
        and f.finding_class in {"SECURITY_FINDING", "EXPOSURE"}
    )
    unverified = len(scan.coverage.get("not_verified") or [])
    lines = [
        "AESA Guard — Continuous Agent Ecosystem Security",
        f"Product: AESA Guard {scan.product_version}  (tooling {scan.package_version})",
        f"Repository: {scan.repository_path}",
        f"Commit: {scan.commit or 'unknown'}",
        "",
        "AUTHORITY SNAPSHOT",
        f"  Components discovered              {len(scan.inventory.get('components') or [])}",
        f"  Authority-bearing components       {scan.authority_bearing_count}",
        f"  External connections               {scan.external_destination_count}",
        f"  High-priority review items         {high_priority}",
        f"  Unverified control surfaces        {unverified}",
        "",
        "OBSERVATION CLASSES",
        f"  Security findings                  {by_class.get('SECURITY_FINDING', 0)}",
        f"  Exposure observations              {by_class.get('EXPOSURE', 0)}",
        f"  Capability observations            {by_class.get('CAPABILITY', 0)}",
    ]
    lines.extend(_authority_path_example(scan))

    lines.extend(
        [
            "",
            "COMPONENTS BY TYPE",
        ]
    )
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
            f"MEDIUM {sev.get('MEDIUM', 0)}  LOW {sev.get('LOW', 0)}  "
            f"INFO {sev.get('INFORMATIONAL', 0)}",
        ]
    )
    if not scan.findings:
        lines.append("  No deterministic rule findings. This is NOT a clean bill of health.")
    else:
        # Show security findings first, then exposures, then capabilities.
        ordered = sorted(
            scan.findings,
            key=lambda f: (
                {"SECURITY_FINDING": 0, "EXPOSURE": 1, "CAPABILITY": 2}.get(f.finding_class, 9),
                {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFORMATIONAL": 4}.get(
                    f.severity, 9
                ),
            ),
        )
        for finding in ordered[:12]:
            lines.append(
                f"  [{finding.finding_class}/{finding.severity}/{finding.confidence}] "
                f"{finding.finding_id} {finding.title}"
            )
            path = _evidence_path(scan, finding)
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
            "  Capability ≠ vulnerability. Exposure ≠ confirmed exploit.",
            "  Incomplete coverage never equals safety. Use `aesa explain F-00N` for detail.",
            "  Save a baseline (`aesa baseline save`) then gate PRs with the GitHub Action.",
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
                loc = ev.file_path or "(no path)"
                if ev.line_start:
                    loc = f"{loc}:{ev.line_start}"
                    if ev.line_end and ev.line_end != ev.line_start:
                        loc = f"{loc}-{ev.line_end}"
                digest = f" digest={ev.content_digest}" if ev.content_digest else ""
                commit = f" commit={ev.source_commit}" if ev.source_commit else ""
                evidence_lines.append(
                    f"- `{ev.evidence_id}` [{ev.evidence_class}/{ev.verification_status}] "
                    f"{loc}{digest}{commit}: {ev.summary}"
                )
                for lim in ev.limitations:
                    evidence_lines.append(f"  limitation: {lim}")
    lines = [
        f"# {finding.finding_id}: {finding.title}",
        "",
        f"- Rule: `{finding.rule_id}`",
        f"- Class: **{finding.finding_class}** "
        f"(CAPABILITY = what it can do; EXPOSURE = reachability; "
        f"SECURITY_FINDING = evidenced security concern)",
        f"- Severity: **{finding.severity}**",
        f"- Confidence: **{finding.confidence}**",
        f"- Exposure: {finding.exposure}",
        f"- Components: {', '.join(finding.component_ids) or '(none)'}",
        f"- Capabilities: {', '.join(finding.capabilities) or '(none)'}",
        "",
        "## What was observed",
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
        "## What is not yet verified",
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
                f"- **{finding.finding_id}** "
                f"[{finding.finding_class}/{finding.severity}/{finding.confidence}] "
                f"{finding.title}"
            )
            lines.append(f"  - {finding.recommended_action}")
    lines.extend(
        [
            "",
            "## Executive questions (still require human judgment)",
            "",
            "1. What can agents in this repository access, execute, and trust?",
            "2. Which combinations create dangerous authority paths?",
            "3. What changed since the last baseline?",
            "4. What remains unverified before deployment?",
            "",
        ]
    )
    return "\n".join(lines)
