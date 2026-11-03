"""Versioned deterministic security rules for AESA Guard.

Rules emit OBSERVED/POTENTIAL findings with evidence references. They never
promote claims to CONFIRMED without stronger verification.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from aesa.security.models import Evidence, Finding, VerificationStatus

RuleFn = Callable[[dict[str, Any], list[Evidence], list[Finding]], None]


@dataclass(frozen=True, slots=True)
class RuleSpec:
    rule_id: str
    title: str
    version: str
    apply: RuleFn


def _evidence_for(
    evidences: list[Evidence],
    *,
    component: dict[str, Any],
    summary: str,
    status: VerificationStatus = "OBSERVED",
    limitations: list[str] | None = None,
) -> Evidence:
    cid = str(component.get("component_id") or "UNKNOWN")
    eid = f"E-{len(evidences) + 1:03d}"
    ev = Evidence(
        evidence_id=eid,
        component_id=cid,
        evidence_class="SOURCE_STATIC",
        verification_status=status,
        file_path=component.get("repository_path"),
        collection_method="deterministic_rule",
        summary=summary,
        limitations=limitations
        or [
            "Static configuration observation only; host effective permissions not verified.",
        ],
    )
    evidences.append(ev)
    return ev


def _add_finding(
    findings: list[Finding],
    *,
    rule_id: str,
    title: str,
    severity: str,
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
) -> None:
    fid = f"F-{len(findings) + 1:03d}"
    findings.append(
        Finding(
            finding_id=fid,
            rule_id=rule_id,
            title=title,
            severity=severity,  # type: ignore[arg-type]
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
            exposure="REPO_CONFIG",
        )
    )


def rule_skill_bundled_scripts(
    component: dict[str, Any], evidences: list[Evidence], findings: list[Finding]
) -> None:
    if component.get("type") != "Skill":
        return
    hints = set(component.get("priority_hints") or [])
    if not hints.intersection(
        {"bundled_scripts_directory", "script_reference", "possible_code_execution_reference"}
    ):
        return
    ev = _evidence_for(
        evidences,
        component=component,
        summary="Skill references or bundles executable script content.",
        status="OBSERVED",
    )
    _add_finding(
        findings,
        rule_id="AESA-RULE-001",
        title="Skill references executable scripts",
        severity="HIGH",
        confidence="POTENTIAL",
        description=(
            f"Skill `{component.get('name')}` references scripts or a bundled scripts "
            "directory. Execution authority and environment inheritance are not verified."
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
            "Verify whether scripts inherit sensitive environment variables and whether "
            "execution requires independent human approval."
        ),
    )


def rule_mcp_local_command(
    component: dict[str, Any], evidences: list[Evidence], findings: list[Finding]
) -> None:
    if component.get("type") != "MCP Server Registration":
        return
    hints = set(component.get("priority_hints") or [])
    if "local_command_transport" not in hints and not component.get("command"):
        return
    ev = _evidence_for(
        evidences,
        component=component,
        summary=f"MCP registration launches local command `{component.get('command')}`.",
        status="OBSERVED",
    )
    severity = "HIGH"
    if "inherits_or_sets_environment" in hints:
        severity = "CRITICAL"
    _add_finding(
        findings,
        rule_id="AESA-RULE-002",
        title="MCP server launched via local command",
        severity=severity,
        confidence="OBSERVED",
        description=(
            f"MCP server `{component.get('name')}` is registered with a local command "
            "transport. The host agent can invoke tools implemented by that process."
        ),
        component=component,
        evidence=ev,
        capabilities=["execute_commands", "invoke_tools"]
        + (["access_secrets"] if "inherits_or_sets_environment" in hints else []),
        attacker_control="Compromised MCP server binary/package or tool-poisoned metadata",
        entry_point=str(component.get("repository_path") or ""),
        trust_boundary="Host agent → MCP child process",
        impact="Tool calls execute under the MCP process identity with host-granted access",
        missing_controls=[
            "Exact artifact digest of the launched binary/package",
            "Host-side authorization binding for tool arguments",
        ],
        recommended_action=(
            "Pin and verify the exact MCP server artifact, restrict env inheritance, "
            "and require approval for high-impact tools."
        ),
    )


def rule_mcp_remote_endpoint(
    component: dict[str, Any], evidences: list[Evidence], findings: list[Finding]
) -> None:
    if component.get("type") != "MCP Server Registration":
        return
    if "remote_endpoint" not in set(component.get("priority_hints") or []) and not component.get(
        "url"
    ):
        return
    ev = _evidence_for(
        evidences,
        component=component,
        summary=f"MCP registration points at remote URL `{component.get('url')}`.",
        status="OBSERVED",
    )
    _add_finding(
        findings,
        rule_id="AESA-RULE-003",
        title="MCP server uses remote endpoint",
        severity="HIGH",
        confidence="OBSERVED",
        description=(
            f"MCP server `{component.get('name')}` is configured with a remote URL. "
            "Credentials, tool results, and prompts may leave the local trust boundary."
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
    )


def rule_hook_execution_boundary(
    component: dict[str, Any], evidences: list[Evidence], findings: list[Finding]
) -> None:
    if component.get("type") != "Hook":
        return
    hints = set(component.get("priority_hints") or [])
    if "possible_execution_boundary" not in hints and "pre_execution_lifecycle" not in hints:
        return
    ev = _evidence_for(
        evidences,
        component=component,
        summary="Hook configuration indicates execution or pre-tool lifecycle involvement.",
        status="OBSERVED",
    )
    _add_finding(
        findings,
        rule_id="AESA-RULE-004",
        title="Hook can intercept or execute around tool use",
        severity="HIGH",
        confidence="POTENTIAL",
        description=(
            f"Hook `{component.get('name')}` appears to participate in execution or "
            "pre-tool lifecycle events. Argument mutation after approval is a known risk."
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
    )


def rule_skill_external_url(
    component: dict[str, Any], evidences: list[Evidence], findings: list[Finding]
) -> None:
    if component.get("type") != "Skill":
        return
    if "external_url_reference" not in set(component.get("priority_hints") or []):
        return
    ev = _evidence_for(
        evidences,
        component=component,
        summary="Skill instructions reference external HTTP(S) URLs.",
        status="OBSERVED",
    )
    _add_finding(
        findings,
        rule_id="AESA-RULE-005",
        title="Skill references external URLs",
        severity="MEDIUM",
        confidence="OBSERVED",
        description=(
            f"Skill `{component.get('name')}` references external URLs. Remote content "
            "may introduce instructions or data outside the reviewed repository."
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
    )


def rule_skill_secrets_handling(
    component: dict[str, Any], evidences: list[Evidence], findings: list[Finding]
) -> None:
    if component.get("type") != "Skill":
        return
    hints = set(component.get("priority_hints") or [])
    if "secrets_or_credential_handling" not in hints and "identity_or_auth_workflow" not in hints:
        return
    ev = _evidence_for(
        evidences,
        component=component,
        summary="Skill text references secrets, credentials, or identity workflows.",
        status="OBSERVED",
    )
    _add_finding(
        findings,
        rule_id="AESA-RULE-006",
        title="Skill references secrets or identity workflows",
        severity="HIGH",
        confidence="POTENTIAL",
        description=(
            f"Skill `{component.get('name')}` discusses secrets or authentication workflows. "
            "Confirm whether it can access live credentials."
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
    )


def rule_unattended_automation(
    component: dict[str, Any], evidences: list[Evidence], findings: list[Finding]
) -> None:
    if component.get("type") not in {"Automation", "CI Workflow", "Workflow"}:
        return
    ev = _evidence_for(
        evidences,
        component=component,
        summary="Unattended workflow/automation surface discovered.",
        status="OBSERVED",
    )
    _add_finding(
        findings,
        rule_id="AESA-RULE-007",
        title="Unattended automation or CI workflow present",
        severity="MEDIUM",
        confidence="OBSERVED",
        description=(
            f"`{component.get('name')}` is an unattended automation/CI surface. "
            "Webhook replay, secret inheritance, and cancellation controls need review."
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
    )


def rule_subagent_delegation(
    component: dict[str, Any], evidences: list[Evidence], findings: list[Finding]
) -> None:
    if component.get("type") != "Subagent":
        return
    ev = _evidence_for(
        evidences,
        component=component,
        summary="Subagent definition discovered; delegated authority not verified.",
        status="OBSERVED",
    )
    _add_finding(
        findings,
        rule_id="AESA-RULE-008",
        title="Subagent may inherit delegated authority",
        severity="MEDIUM",
        confidence="POTENTIAL",
        description=(
            f"Subagent `{component.get('name')}` can receive delegated tasks. "
            "Confirm privilege reduction, message authentication, and shared memory isolation."
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
    )


def rule_example_mcp_config(
    component: dict[str, Any], evidences: list[Evidence], findings: list[Finding]
) -> None:
    if component.get("type") != "MCP Server Registration":
        return
    if "example_or_template_config" not in set(component.get("priority_hints") or []):
        return
    ev = _evidence_for(
        evidences,
        component=component,
        summary="MCP registration appears to be an example/template configuration.",
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
    )


def rule_instruction_injection_markers(
    component: dict[str, Any], evidences: list[Evidence], findings: list[Finding]
) -> None:
    """Flag skills/rules that the corpus marks as injection-oriented via path/name."""
    ctype = str(component.get("type") or "")
    if ctype not in {"Skill", "Rule pack"}:
        return
    path = str(component.get("repository_path") or "").lower()
    name = str(component.get("name") or "").lower()
    markers = ("injection", "exfil", "ignore previous", "jailbreak")
    if not any(m in path or m in name for m in markers):
        return
    ev = _evidence_for(
        evidences,
        component=component,
        summary="Component path/name suggests prompt-injection oriented content.",
        status="OBSERVED",
    )
    _add_finding(
        findings,
        rule_id="AESA-RULE-010",
        title="Potential prompt-injection oriented instruction surface",
        severity="HIGH",
        confidence="POTENTIAL",
        description=(
            f"`{component.get('name')}` appears related to prompt-injection patterns by "
            "name/path. Treat instructions as untrusted and verify activation breadth."
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
    )


RULES: list[RuleSpec] = [
    RuleSpec(
        "AESA-RULE-001", "Skill references executable scripts", "1.0", rule_skill_bundled_scripts
    ),
    RuleSpec("AESA-RULE-002", "MCP local command transport", "1.0", rule_mcp_local_command),
    RuleSpec("AESA-RULE-003", "MCP remote endpoint", "1.0", rule_mcp_remote_endpoint),
    RuleSpec("AESA-RULE-004", "Hook execution boundary", "1.0", rule_hook_execution_boundary),
    RuleSpec("AESA-RULE-005", "Skill external URLs", "1.0", rule_skill_external_url),
    RuleSpec("AESA-RULE-006", "Skill secrets handling", "1.0", rule_skill_secrets_handling),
    RuleSpec("AESA-RULE-007", "Unattended automation", "1.0", rule_unattended_automation),
    RuleSpec("AESA-RULE-008", "Subagent delegation", "1.0", rule_subagent_delegation),
    RuleSpec("AESA-RULE-009", "Example MCP config", "1.0", rule_example_mcp_config),
    RuleSpec(
        "AESA-RULE-010",
        "Prompt-injection oriented surface",
        "1.0",
        rule_instruction_injection_markers,
    ),
]


def apply_all_rules(
    components: list[dict[str, Any]],
) -> tuple[list[Evidence], list[Finding]]:
    evidences: list[Evidence] = []
    findings: list[Finding] = []
    for component in components:
        for rule in RULES:
            rule.apply(component, evidences, findings)
    return evidences, findings
