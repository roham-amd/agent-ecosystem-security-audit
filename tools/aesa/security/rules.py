"""Versioned deterministic security rules for AESA Guard.

Rules classify outputs as CAPABILITY, EXPOSURE, or SECURITY_FINDING.
Presence of a security-relevant capability is not automatically a HIGH finding.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from aesa.security.evidence_util import EvidenceContext, build_rule_evidence
from aesa.security.models import (
    Evidence,
    EvidenceStrength,
    Finding,
    FindingClass,
    Severity,
    VerificationStatus,
)

RuleFn = Callable[[dict[str, Any], list[Evidence], list[Finding], EvidenceContext], None]


@dataclass(frozen=True, slots=True)
class RuleSpec:
    rule_id: str
    title: str
    version: str
    apply: RuleFn


def _add_finding(
    findings: list[Finding],
    *,
    rule_id: str,
    title: str,
    severity: Severity,
    confidence: VerificationStatus,
    description: str,
    component: dict[str, Any],
    evidence: Evidence,
    capabilities: list[str],
    attacker_control: str,
    entry_point: str,
    trust_boundary: str,
    impact: str,
    missing_controls: list[str],
    recommended_action: str,
    finding_class: FindingClass,
    exposure: str = "REPO_CONFIG",
    evidence_strength: EvidenceStrength = "INFERRED_HINT",
    verify_in_60s: str = "",
    fix_snippet: str = "",
) -> None:
    fid = f"F-{len(findings) + 1:03d}"
    findings.append(
        Finding(
            finding_id=fid,
            rule_id=rule_id,
            title=title,
            severity=severity,
            confidence=confidence,
            description=description,
            component_ids=[str(component.get("component_id") or "")],
            evidence_ids=[evidence.evidence_id],
            capabilities=capabilities,
            attacker_control=attacker_control,
            entry_point=entry_point,
            trust_boundary=trust_boundary,
            impact=impact,
            missing_controls=missing_controls,
            recommended_action=recommended_action,
            exploitability="UNKNOWN",
            exposure=exposure,
            finding_class=finding_class,
            evidence_strength=evidence_strength,
            verify_in_60s=verify_in_60s,
            fix_snippet=fix_snippet,
        )
    )


def rule_skill_bundled_scripts(
    component: dict[str, Any],
    evidences: list[Evidence],
    findings: list[Finding],
    ctx: EvidenceContext,
) -> None:
    if component.get("type") != "Skill":
        return
    hints = set(component.get("priority_hints") or [])
    if not hints.intersection(
        {"bundled_scripts_directory", "script_reference", "possible_code_execution_reference"}
    ):
        return
    # Capability observation unless stronger host/credential evidence exists.
    finding_class: FindingClass = "CAPABILITY"
    severity: Severity = "INFORMATIONAL"
    if "bundled_scripts_directory" in hints and "secrets_or_credential_handling" in hints:
        finding_class = "SECURITY_FINDING"
        severity = "HIGH"
    elif "bundled_scripts_directory" in hints:
        finding_class = "EXPOSURE"
        severity = "MEDIUM"

    ev = build_rule_evidence(
        evidences,
        component=component,
        summary="Skill references or bundles executable script content.",
        ctx=ctx,
        status="OBSERVED",
        needle="script",
    )
    _add_finding(
        findings,
        rule_id="AESA-RULE-001",
        title="Skill references executable scripts",
        severity=severity,
        confidence="POTENTIAL",
        description=(
            f"Skill `{component.get('name')}` references scripts or a bundled scripts "
            "directory. This establishes an execution *capability*; host inheritance and "
            "approval enforcement remain unverified."
        ),
        component=component,
        evidence=ev,
        capabilities=["execute_commands"],
        attacker_control="Malicious or compromised skill instructions / scripts",
        entry_point=str(component.get("repository_path") or ""),
        trust_boundary="Agent instruction surface → host execution",
        impact="Potential local command execution under the host agent identity",
        missing_controls=[
            "Independent approval for script execution",
            "Host effective environment / secret inheritance",
        ],
        recommended_action=(
            "Treat as an authority surface: verify whether scripts inherit sensitive "
            "environment variables and whether execution requires independent approval."
        ),
        finding_class=finding_class,
        evidence_strength="LITERAL_CONFIG"
        if "bundled_scripts_directory" in hints
        else "INFERRED_HINT",
        verify_in_60s="ls the skill directory; confirm whether scripts/ is present and executed.",
    )


def rule_mcp_local_command(
    component: dict[str, Any],
    evidences: list[Evidence],
    findings: list[Finding],
    ctx: EvidenceContext,
) -> None:
    if component.get("type") != "MCP Server Registration":
        return
    hints = set(component.get("priority_hints") or [])
    if "local_command_transport" not in hints and not component.get("command"):
        return

    inherits_env = "inherits_or_sets_environment" in hints
    broad_args = "broad_or_relative_path_args" in hints

    # Local process alone = capability. Escalate only with exposure conditions.
    if inherits_env:
        finding_class: FindingClass = "SECURITY_FINDING"
        severity: Severity = "CRITICAL"
        confidence: VerificationStatus = "POTENTIAL"
        title = "MCP local command may inherit host credentials"
        exposure = "HOST_ENV_INHERITANCE"
    elif broad_args:
        finding_class = "SECURITY_FINDING"
        severity = "HIGH"
        confidence = "POTENTIAL"
        title = "MCP local command with broad filesystem arguments"
        exposure = "BROAD_PATH_ARGS"
    else:
        finding_class = "CAPABILITY"
        severity = "INFORMATIONAL"
        confidence = "OBSERVED"
        title = "MCP server launched via local command"
        exposure = "REPO_CONFIG"

    command = str(component.get("command") or "")
    ev = build_rule_evidence(
        evidences,
        component=component,
        summary=f"MCP registration launches local command `{command}`.",
        ctx=ctx,
        status="OBSERVED",
        needle=command or None,
    )
    caps = ["execute_commands", "invoke_tools"]
    if inherits_env:
        caps.append("access_secrets")
    if broad_args:
        caps.append("read_files")

    _add_finding(
        findings,
        rule_id="AESA-RULE-002",
        title=title,
        severity=severity,
        confidence=confidence,
        description=(
            f"MCP server `{component.get('name')}` is registered with a local command "
            "transport. "
            + (
                "Environment inheritance or broad path arguments elevate this beyond a "
                "simple capability observation."
                if inherits_env or broad_args
                else "Presence of a local process is a capability observation, not proof of abuse."
            )
        ),
        component=component,
        evidence=ev,
        capabilities=caps,
        attacker_control="Compromised MCP server binary/package or tool-poisoned metadata",
        entry_point=str(component.get("repository_path") or ""),
        trust_boundary="Host agent → MCP child process",
        impact="Tool calls execute under the MCP process identity with host-granted access",
        missing_controls=[
            "Exact artifact digest of the launched binary/package",
            "Host-side authorization binding for tool arguments",
            *(["Verified restriction of inherited environment / secrets"] if inherits_env else []),
            *(["Least-privilege filesystem binding"] if broad_args else []),
        ],
        recommended_action=(
            "Pin and verify the exact MCP server artifact, restrict env inheritance, "
            "and require approval for high-impact tools."
            if inherits_env or broad_args
            else "Record as an execution capability; verify host isolation before treating as risk."
        ),
        finding_class=finding_class,
        exposure=exposure,
        evidence_strength="LITERAL_CONFIG",
        verify_in_60s=f"Open the MCP config and inspect command=`{command}` plus env/args.",
        fix_snippet="Pin the MCP binary/package; drop broad path args; avoid inheriting secrets.",
    )


def rule_mcp_remote_endpoint(
    component: dict[str, Any],
    evidences: list[Evidence],
    findings: list[Finding],
    ctx: EvidenceContext,
) -> None:
    if component.get("type") != "MCP Server Registration":
        return
    if "remote_endpoint" not in set(component.get("priority_hints") or []) and not component.get(
        "url"
    ):
        return
    url = str(component.get("url") or "")
    ev = build_rule_evidence(
        evidences,
        component=component,
        summary=f"MCP registration points at remote URL `{url}`.",
        ctx=ctx,
        status="OBSERVED",
        needle=url or None,
    )
    _add_finding(
        findings,
        rule_id="AESA-RULE-003",
        title="MCP server uses remote endpoint",
        severity="MEDIUM",
        confidence="OBSERVED",
        description=(
            f"MCP server `{component.get('name')}` is configured with a remote URL. "
            "This is an external exposure surface; TLS identity and credential forwarding "
            "are not verified by this rule."
        ),
        component=component,
        evidence=ev,
        capabilities=["access_network", "invoke_tools"],
        attacker_control="Compromised remote MCP endpoint or MITM without transport identity",
        entry_point=str(component.get("repository_path") or ""),
        trust_boundary="Host agent → remote network service",
        impact="Potential exfiltration or tool abuse via remote MCP",
        missing_controls=[
            "Transport identity / TLS pinning",
            "OAuth / credential forwarding scope review",
        ],
        recommended_action=(
            "Verify endpoint identity, TLS, OAuth scopes, and whether secrets are forwarded."
        ),
        finding_class="EXPOSURE",
        exposure="REMOTE_ENDPOINT",
    )


def rule_hook_execution_boundary(
    component: dict[str, Any],
    evidences: list[Evidence],
    findings: list[Finding],
    ctx: EvidenceContext,
) -> None:
    if component.get("type") != "Hook":
        return
    hints = set(component.get("priority_hints") or [])
    if "possible_execution_boundary" not in hints and "pre_execution_lifecycle" not in hints:
        return
    pre_tool = "pre_execution_lifecycle" in hints
    finding_class: FindingClass = "SECURITY_FINDING" if pre_tool else "CAPABILITY"
    severity: Severity = "MEDIUM" if pre_tool else "INFORMATIONAL"
    ev = build_rule_evidence(
        evidences,
        component=component,
        summary="Hook configuration indicates execution or pre-tool lifecycle involvement.",
        ctx=ctx,
        status="OBSERVED",
    )
    _add_finding(
        findings,
        rule_id="AESA-RULE-004",
        title="Hook can intercept or execute around tool use",
        severity=severity,
        confidence="POTENTIAL",
        description=(
            f"Hook `{component.get('name')}` appears to participate in execution or "
            "pre-tool lifecycle events. Presence alone is not privilege abuse; "
            "post-approval argument mutation requires verification."
        ),
        component=component,
        evidence=ev,
        capabilities=["execute_commands", "modify_approvals"],
        attacker_control="Malicious hook definition or poisoned hook input",
        entry_point=str(component.get("repository_path") or ""),
        trust_boundary="User approval → hook mutation → tool execution",
        impact="Approved actions may be altered; privileged commands may run unexpectedly",
        missing_controls=[
            "Argument integrity binding after approval",
            "Hook execution identity isolation",
        ],
        recommended_action=(
            "Confirm whether hooks can mutate tool arguments after approval and what "
            "identity they run as."
        ),
        finding_class=finding_class,
    )


def rule_skill_external_url(
    component: dict[str, Any],
    evidences: list[Evidence],
    findings: list[Finding],
    ctx: EvidenceContext,
) -> None:
    if component.get("type") != "Skill":
        return
    if "external_url_reference" not in set(component.get("priority_hints") or []):
        return
    ev = build_rule_evidence(
        evidences,
        component=component,
        summary="Skill instructions reference external HTTP(S) URLs.",
        ctx=ctx,
        status="OBSERVED",
        needle="https://",
    )
    _add_finding(
        findings,
        rule_id="AESA-RULE-005",
        title="Skill references external URLs",
        severity="LOW",
        confidence="OBSERVED",
        description=(
            f"Skill `{component.get('name')}` references external URLs. A URL is an "
            "exposure indicator, not proof of malicious content."
        ),
        component=component,
        evidence=ev,
        capabilities=["access_network", "modify_agent_instructions"],
        attacker_control="Compromised remote resource referenced by the skill",
        entry_point=str(component.get("repository_path") or ""),
        trust_boundary="Reviewed skill → unreviewed remote content",
        impact="Potential instruction injection or data exfiltration guidance",
        missing_controls=["Pinned remote content digests", "Egress policy for agent fetches"],
        recommended_action="Pin or vendor remote references; treat remote content as untrusted.",
        finding_class="EXPOSURE",
        exposure="EXTERNAL_URL",
    )


def rule_skill_secrets_handling(
    component: dict[str, Any],
    evidences: list[Evidence],
    findings: list[Finding],
    ctx: EvidenceContext,
) -> None:
    if component.get("type") != "Skill":
        return
    hints = set(component.get("priority_hints") or [])
    if "secrets_or_credential_handling" not in hints and "identity_or_auth_workflow" not in hints:
        return
    # Credential-handling instructions need context; treat as potential finding.
    ev = build_rule_evidence(
        evidences,
        component=component,
        summary="Skill text references secrets, credentials, or identity workflows.",
        ctx=ctx,
        status="OBSERVED",
        needle="secret",
    )
    _add_finding(
        findings,
        rule_id="AESA-RULE-006",
        title="Skill references secrets or identity workflows",
        severity="MEDIUM",
        confidence="POTENTIAL",
        description=(
            f"Skill `{component.get('name')}` discusses secrets or authentication workflows. "
            "Confirm whether it can access live credentials and under which identity."
        ),
        component=component,
        evidence=ev,
        capabilities=["access_secrets"],
        attacker_control="Prompt injection causing the agent to follow credential-handling steps",
        entry_point=str(component.get("repository_path") or ""),
        trust_boundary="Agent context → credential stores / identity tooling",
        impact="Potential credential disclosure or misuse",
        missing_controls=["Secret redaction", "Separate credential broker with least privilege"],
        recommended_action="Ensure skills cannot print or forward live secrets; prefer brokers.",
        finding_class="SECURITY_FINDING",
    )


def rule_unattended_automation(
    component: dict[str, Any],
    evidences: list[Evidence],
    findings: list[Finding],
    ctx: EvidenceContext,
) -> None:
    ctype = str(component.get("type") or "")
    if ctype not in {
        "Automation",
        "Automation / Workflow",
        "CI Workflow",
        "Workflow",
    }:
        return
    hints = set(component.get("priority_hints") or [])
    secret_hints = {
        "secrets_or_credential_handling",
        "inherits_or_sets_environment",
        "secret_reference",
        "credential_reference",
    }
    # Unattended operation alone is a capability; escalate when secret hints present.
    if hints.intersection(secret_hints):
        finding_class: FindingClass = "SECURITY_FINDING"
        severity: Severity = "MEDIUM"
    else:
        finding_class = "CAPABILITY"
        severity = "INFORMATIONAL"
    ev = build_rule_evidence(
        evidences,
        component=component,
        summary="Unattended workflow/automation surface discovered.",
        ctx=ctx,
        status="OBSERVED",
    )
    _add_finding(
        findings,
        rule_id="AESA-RULE-007",
        title="Unattended automation or CI workflow present",
        severity=severity,
        confidence="OBSERVED",
        description=(
            f"`{component.get('name')}` is an unattended automation/CI surface. "
            "Legitimate automation can be secure; review triggers, secrets, and cancellation."
        ),
        component=component,
        evidence=ev,
        capabilities=["unattended_operation", "access_secrets"],
        attacker_control="Malicious trigger payload or compromised workflow definition",
        entry_point=str(component.get("repository_path") or ""),
        trust_boundary="Trigger → privileged unattended execution",
        impact="Actions may run without interactive human approval",
        missing_controls=[
            "Webhook authentication / replay protection",
            "Least-privilege workflow tokens",
        ],
        recommended_action="Review triggers, secrets, permissions, and cancellation behavior.",
        finding_class=finding_class,
    )


def rule_subagent_delegation(
    component: dict[str, Any],
    evidences: list[Evidence],
    findings: list[Finding],
    ctx: EvidenceContext,
) -> None:
    if component.get("type") != "Subagent":
        return
    ev = build_rule_evidence(
        evidences,
        component=component,
        summary="Subagent definition discovered; delegated authority not verified.",
        ctx=ctx,
        status="OBSERVED",
    )
    _add_finding(
        findings,
        rule_id="AESA-RULE-008",
        title="Subagent may inherit delegated authority",
        severity="INFORMATIONAL",
        confidence="POTENTIAL",
        description=(
            f"Subagent `{component.get('name')}` can receive delegated tasks. "
            "Delegation alone is not a security defect; verify privilege reduction and isolation."
        ),
        component=component,
        evidence=ev,
        capabilities=["delegate_tasks"],
        attacker_control="Compromised parent agent or poisoned delegated task content",
        entry_point=str(component.get("repository_path") or ""),
        trust_boundary="Parent agent → subagent",
        impact="Excessive authority or cross-tenant data exposure via delegation",
        missing_controls=["Privilege reduction on delegate", "Inter-agent message authentication"],
        recommended_action="Verify inherited credentials, tool allowlists, and memory isolation.",
        finding_class="CAPABILITY",
    )


def rule_example_mcp_config(
    component: dict[str, Any],
    evidences: list[Evidence],
    findings: list[Finding],
    ctx: EvidenceContext,
) -> None:
    if component.get("type") != "MCP Server Registration":
        return
    if "example_or_template_config" not in set(component.get("priority_hints") or []):
        return
    ev = build_rule_evidence(
        evidences,
        component=component,
        summary="MCP registration appears to be an example/template configuration.",
        ctx=ctx,
        status="OBSERVED",
        limitations=["May not be loaded by the host; still a configuration surface to review."],
    )
    _add_finding(
        findings,
        rule_id="AESA-RULE-009",
        title="Example MCP config may be mistaken for production registration",
        severity="LOW",
        confidence="OBSERVED",
        description=(
            f"MCP registration `{component.get('name')}` looks like an example/template. "
            "Confirm it is not loaded by the host agent in production."
        ),
        component=component,
        evidence=ev,
        capabilities=["invoke_tools"],
        attacker_control="Accidental promotion of example config into a live host",
        entry_point=str(component.get("repository_path") or ""),
        trust_boundary="Documentation/example → live agent configuration",
        impact="Unexpected tool surface if example configs are installed",
        missing_controls=["Host config allowlist excluding examples"],
        recommended_action="Ensure example configs are not on the host's MCP search path.",
        finding_class="EXPOSURE",
    )


def rule_instruction_injection_markers(
    component: dict[str, Any],
    evidences: list[Evidence],
    findings: list[Finding],
    ctx: EvidenceContext,
) -> None:
    """Flag skills/rules that look injection-oriented via path/name (weak indicator)."""
    ctype = str(component.get("type") or "")
    if ctype not in {"Skill", "Rule pack"}:
        return
    path = str(component.get("repository_path") or "").lower()
    name = str(component.get("name") or "").lower()
    markers = ("injection", "exfil", "ignore previous", "jailbreak")
    if not any(m in path or m in name for m in markers):
        return
    ev = build_rule_evidence(
        evidences,
        component=component,
        summary="Component path/name suggests prompt-injection oriented content.",
        ctx=ctx,
        status="OBSERVED",
        limitations=[
            "Naming is a weak indicator of exploitation; review instruction text before acting.",
        ],
    )
    _add_finding(
        findings,
        rule_id="AESA-RULE-010",
        title="Potential prompt-injection oriented instruction surface",
        severity="LOW",
        confidence="POTENTIAL",
        description=(
            f"`{component.get('name')}` appears related to prompt-injection patterns by "
            "name/path. Naming alone is a weak signal — treat as triage, not confirmed abuse."
        ),
        component=component,
        evidence=ev,
        capabilities=["modify_agent_instructions"],
        attacker_control="Instruction content in the component itself",
        entry_point=str(component.get("repository_path") or ""),
        trust_boundary="Untrusted instructions → privileged agent tools",
        impact="Agent may follow injected instructions leading to privileged actions",
        missing_controls=["Instruction isolation", "Tool allowlists for untrusted content"],
        recommended_action="Review full instruction text; do not auto-activate in privileged hosts.",
        finding_class="CAPABILITY",
        evidence_strength="NAME_MARKER",
        verify_in_60s="Open the file; naming alone is weak — read the instruction text.",
    )


def rule_unpinned_package_launcher(
    component: dict[str, Any],
    evidences: list[Evidence],
    findings: list[Finding],
    ctx: EvidenceContext,
) -> None:
    if component.get("type") != "MCP Server Registration":
        return
    if "unpinned_package_launcher" not in set(component.get("priority_hints") or []):
        return
    command = str(component.get("command") or "")
    args = component.get("args") or []
    ev = build_rule_evidence(
        evidences,
        component=component,
        summary=f"MCP launcher `{command}` appears unpinned (npx -y / uvx / similar).",
        ctx=ctx,
        status="OBSERVED",
        needle=command or "npx",
    )
    _add_finding(
        findings,
        rule_id="AESA-RULE-011",
        title="MCP server launched via unpinned package installer",
        severity="HIGH",
        confidence="OBSERVED",
        description=(
            f"MCP server `{component.get('name')}` uses an unpinned launcher "
            f"(`{command}` {' '.join(str(a) for a in args)}). A later package publish can "
            "change behavior without a config edit (rug-pull risk)."
        ),
        component=component,
        evidence=ev,
        capabilities=["execute_commands", "invoke_tools"],
        attacker_control="Malicious or compromised package published to the unpinned name",
        entry_point=str(component.get("repository_path") or ""),
        trust_boundary="Host agent → package registry → MCP process",
        impact="Arbitrary code execution under the host agent identity after a registry update",
        missing_controls=["Pinned version or content digest", "Allowlisted package source"],
        recommended_action="Pin an exact version or digest; avoid `npx -y` / floating `uvx` tags.",
        finding_class="SECURITY_FINDING",
        exposure="UNPINNED_LAUNCHER",
        evidence_strength="LITERAL_CONFIG",
        verify_in_60s="grep the MCP JSON for npx -y / uvx and confirm no @version pin.",
        fix_snippet='Use "command": "npx", "args": ["-y", "pkg@1.2.3"] or a local pinned binary.',
    )


def rule_literal_secret_in_mcp_env(
    component: dict[str, Any],
    evidences: list[Evidence],
    findings: list[Finding],
    ctx: EvidenceContext,
) -> None:
    if component.get("type") != "MCP Server Registration":
        return
    if "literal_secret_in_env" not in set(component.get("priority_hints") or []):
        return
    ev = build_rule_evidence(
        evidences,
        component=component,
        summary="MCP registration embeds a literal secret-like value in env.",
        ctx=ctx,
        status="OBSERVED",
        needle="env",
    )
    _add_finding(
        findings,
        rule_id="AESA-RULE-012",
        title="Literal secret-like value in MCP env",
        severity="CRITICAL",
        confidence="OBSERVED",
        description=(
            f"MCP server `{component.get('name')}` appears to embed a literal credential in "
            "`env` rather than a placeholder reference. Committed secrets are an immediate "
            "exposure."
        ),
        component=component,
        evidence=ev,
        capabilities=["access_secrets"],
        attacker_control="Anyone with repo or backup access can read the credential",
        entry_point=str(component.get("repository_path") or ""),
        trust_boundary="Repository contents → MCP process environment",
        impact="Credential theft and downstream account takeover",
        missing_controls=["Secret store / OS keychain", "Placeholder env expansion only"],
        recommended_action="Replace literal values with `${ENV}` references; rotate the secret.",
        finding_class="SECURITY_FINDING",
        exposure="LITERAL_SECRET",
        evidence_strength="LITERAL_CONFIG",
        verify_in_60s="Open the MCP JSON env block; confirm values are placeholders, not literals.",
        fix_snippet='Use "API_KEY": "${API_KEY}" and inject from the host secret store.',
    )


def rule_insecure_http_remote_mcp(
    component: dict[str, Any],
    evidences: list[Evidence],
    findings: list[Finding],
    ctx: EvidenceContext,
) -> None:
    if component.get("type") != "MCP Server Registration":
        return
    if "insecure_http_remote" not in set(component.get("priority_hints") or []):
        return
    url = str(component.get("url") or "")
    ev = build_rule_evidence(
        evidences,
        component=component,
        summary=f"MCP remote endpoint uses cleartext HTTP: `{url}`.",
        ctx=ctx,
        status="OBSERVED",
        needle="http://",
    )
    _add_finding(
        findings,
        rule_id="AESA-RULE-013",
        title="Remote MCP endpoint uses cleartext HTTP",
        severity="HIGH",
        confidence="OBSERVED",
        description=(
            f"MCP server `{component.get('name')}` points at `{url}` over HTTP. Tool traffic "
            "and any forwarded credentials lack transport confidentiality/integrity."
        ),
        component=component,
        evidence=ev,
        capabilities=["access_network", "invoke_tools", "access_secrets"],
        attacker_control="Network MITM on the path to the MCP endpoint",
        entry_point=str(component.get("repository_path") or ""),
        trust_boundary="Host agent → cleartext network → remote MCP",
        impact="Credential and tool-argument interception or modification",
        missing_controls=["HTTPS / TLS", "Certificate pinning where appropriate"],
        recommended_action="Use https:// only; reject plain HTTP remote MCP registrations.",
        finding_class="SECURITY_FINDING",
        exposure="INSECURE_TRANSPORT",
        evidence_strength="LITERAL_CONFIG",
        verify_in_60s="Confirm the url field starts with https://.",
        fix_snippet='Change "url": "http://..." to "https://...".',
    )


def rule_hidden_unicode_instructions(
    component: dict[str, Any],
    evidences: list[Evidence],
    findings: list[Finding],
    ctx: EvidenceContext,
) -> None:
    if component.get("type") != "Skill":
        return
    if "hidden_unicode_in_instructions" not in set(component.get("priority_hints") or []):
        return
    ev = build_rule_evidence(
        evidences,
        component=component,
        summary="Instruction text contains hidden/bidi Unicode code points.",
        ctx=ctx,
        status="OBSERVED",
    )
    _add_finding(
        findings,
        rule_id="AESA-RULE-014",
        title="Hidden or bidi Unicode in skill instructions",
        severity="HIGH",
        confidence="OBSERVED",
        description=(
            f"Skill `{component.get('name')}` contains zero-width or bidirectional Unicode "
            "characters that can hide or reorder instructions to humans while remaining "
            "visible to the model."
        ),
        component=component,
        evidence=ev,
        capabilities=["modify_agent_instructions"],
        attacker_control="Author of the skill instruction file",
        entry_point=str(component.get("repository_path") or ""),
        trust_boundary="Human review → Unicode-obscured model instructions",
        impact="Covert instruction injection past visual review",
        missing_controls=["Unicode normalization / disallowlist on ingest"],
        recommended_action="Strip bidi/zero-width characters; re-review the visible text.",
        finding_class="SECURITY_FINDING",
        exposure="HIDDEN_UNICODE",
        evidence_strength="LITERAL_CONFIG",
        verify_in_60s="hexdump or `python -c` for U+200B/U+202E in the SKILL.md bytes.",
        fix_snippet="Remove zero-width and bidi override characters from the file.",
    )


def rule_download_and_execute(
    component: dict[str, Any],
    evidences: list[Evidence],
    findings: list[Finding],
    ctx: EvidenceContext,
) -> None:
    ctype = str(component.get("type") or "")
    if ctype not in {"Skill", "Hook"}:
        return
    if "download_and_execute" not in set(component.get("priority_hints") or []):
        return
    ev = build_rule_evidence(
        evidences,
        component=component,
        summary="Component text references download-and-execute patterns (curl|sh / similar).",
        ctx=ctx,
        status="OBSERVED",
        needle="curl",
    )
    _add_finding(
        findings,
        rule_id="AESA-RULE-015",
        title="Download-and-execute pattern in agent surface",
        severity="CRITICAL",
        confidence="OBSERVED",
        description=(
            f"`{component.get('name')}` references piping a remote download into a shell. "
            "That is remote code execution under the agent/host identity if followed."
        ),
        component=component,
        evidence=ev,
        capabilities=["execute_commands", "access_network"],
        attacker_control="Remote URL content at fetch time",
        entry_point=str(component.get("repository_path") or ""),
        trust_boundary="Reviewed instructions → unreviewed remote script",
        impact="Arbitrary remote code execution",
        missing_controls=["Pinned script digest", "No pipe-to-shell in agent surfaces"],
        recommended_action="Vendor and pin scripts; never curl|sh from skills or hooks.",
        finding_class="SECURITY_FINDING",
        exposure="DOWNLOAD_EXEC",
        evidence_strength="LITERAL_CONFIG",
        verify_in_60s="Search the file for `curl .*|` / `wget .*|` / `iwr .*| iex`.",
        fix_snippet="Replace with a pinned local script checked into the repo.",
    )


def rule_pull_request_target_with_agent(
    component: dict[str, Any],
    evidences: list[Evidence],
    findings: list[Finding],
    ctx: EvidenceContext,
) -> None:
    if component.get("type") != "CI Workflow":
        return
    if "pull_request_target_with_agent" not in set(component.get("priority_hints") or []):
        return
    ev = build_rule_evidence(
        evidences,
        component=component,
        summary="Workflow combines pull_request_target with agent/MCP-related steps.",
        ctx=ctx,
        status="OBSERVED",
        needle="pull_request_target",
    )
    _add_finding(
        findings,
        rule_id="AESA-RULE-016",
        title="pull_request_target workflow invokes agent-related steps",
        severity="HIGH",
        confidence="POTENTIAL",
        description=(
            f"CI workflow `{component.get('name')}` uses `pull_request_target` together with "
            "agent/MCP-related steps. Fork PRs can often influence checkout/content while "
            "retaining privileged secrets — a classic CI + agent abuse path."
        ),
        component=component,
        evidence=ev,
        capabilities=["unattended_operation", "access_secrets", "execute_commands"],
        attacker_control="Malicious pull request from a fork",
        entry_point=str(component.get("repository_path") or ""),
        trust_boundary="Fork PR content → privileged workflow + agent tools",
        impact="Secret theft or privileged agent actions from untrusted PR content",
        missing_controls=[
            "Avoid pull_request_target for untrusted code",
            "Persist-credentials false + explicit safe checkout",
        ],
        recommended_action="Prefer pull_request; never feed fork PR code to privileged agents.",
        finding_class="SECURITY_FINDING",
        exposure="PR_TARGET_AGENT",
        evidence_strength="INFERRED_HINT",
        verify_in_60s="Confirm `on: pull_request_target` and whether agent steps touch PR code.",
        fix_snippet="Switch to pull_request, or isolate secrets from any PR-controlled checkout.",
    )


RULES: list[RuleSpec] = [
    RuleSpec(
        "AESA-RULE-001", "Skill references executable scripts", "1.2", rule_skill_bundled_scripts
    ),
    RuleSpec("AESA-RULE-002", "MCP local command transport", "1.2", rule_mcp_local_command),
    RuleSpec("AESA-RULE-003", "MCP remote endpoint", "1.2", rule_mcp_remote_endpoint),
    RuleSpec("AESA-RULE-004", "Hook execution boundary", "1.2", rule_hook_execution_boundary),
    RuleSpec("AESA-RULE-005", "Skill external URLs", "1.2", rule_skill_external_url),
    RuleSpec("AESA-RULE-006", "Skill secrets handling", "1.2", rule_skill_secrets_handling),
    RuleSpec("AESA-RULE-007", "Unattended automation", "1.2", rule_unattended_automation),
    RuleSpec("AESA-RULE-008", "Subagent delegation", "1.2", rule_subagent_delegation),
    RuleSpec("AESA-RULE-009", "Example MCP config", "1.2", rule_example_mcp_config),
    RuleSpec(
        "AESA-RULE-010",
        "Prompt-injection oriented surface",
        "1.2",
        rule_instruction_injection_markers,
    ),
    RuleSpec(
        "AESA-RULE-011", "Unpinned MCP package launcher", "1.0", rule_unpinned_package_launcher
    ),
    RuleSpec("AESA-RULE-012", "Literal secret in MCP env", "1.0", rule_literal_secret_in_mcp_env),
    RuleSpec("AESA-RULE-013", "Cleartext HTTP remote MCP", "1.0", rule_insecure_http_remote_mcp),
    RuleSpec(
        "AESA-RULE-014", "Hidden Unicode in instructions", "1.0", rule_hidden_unicode_instructions
    ),
    RuleSpec("AESA-RULE-015", "Download-and-execute pattern", "1.0", rule_download_and_execute),
    RuleSpec(
        "AESA-RULE-016",
        "pull_request_target with agent steps",
        "1.0",
        rule_pull_request_target_with_agent,
    ),
]


def apply_all_rules(
    components: list[dict[str, Any]],
    *,
    ctx: EvidenceContext | None = None,
) -> tuple[list[Evidence], list[Finding]]:
    evidences: list[Evidence] = []
    findings: list[Finding] = []
    context = ctx or EvidenceContext()
    for component in components:
        for rule in RULES:
            rule.apply(component, evidences, findings, context)
    return evidences, findings
