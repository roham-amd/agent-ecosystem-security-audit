"""Core AESA Guard objects: Component capabilities, evidence, findings, relationships.

Strategic model (3.1.1+):
- Capability: what a component can potentially do
- Exposure: how reachable that capability is / under which identity
- Security finding: evidenced violation of a defined security property
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

EvidenceClass = Literal[
    "SOURCE_STATIC",
    "ARTIFACT",
    "PROVENANCE",
    "HOST_CONFIGURATION",
    "RUNTIME",
    "EXTERNAL_INTELLIGENCE",
    "USER_ASSERTION",
]

VerificationStatus = Literal[
    "OBSERVED",
    "CONFIRMED",
    "POTENTIAL",
    "NOT VERIFIED",
    "NOT ASSESSED",
    "NOT APPLICABLE",
]

Severity = Literal["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFORMATIONAL"]

# Capability vs exposure vs finding — keep these distinct in reports and policy.
FindingClass = Literal["CAPABILITY", "EXPOSURE", "SECURITY_FINDING"]

# How a capability was established. Type defaults are never "effective".
CapabilityOrigin = Literal[
    "DECLARED",  # Explicitly present in configuration / instructions
    "POTENTIAL",  # Hint-derived or inferred; not independently verified
    "TYPE_DEFAULT",  # Assumed from component type alone
    "EFFECTIVE",  # Host/integration evidence of actual authority
    "VERIFIED",  # Independently verified (e.g. authorized runtime test)
]

CapabilityKind = Literal[
    "read_files",
    "write_files",
    "execute_commands",
    "access_secrets",
    "access_network",
    "modify_agent_instructions",
    "invoke_tools",
    "delegate_tasks",
    "modify_approvals",
    "access_persistent_memory",
    "unattended_operation",
]


@dataclass(slots=True)
class Capability:
    kind: CapabilityKind
    status: VerificationStatus
    component_id: str
    evidence_ids: list[str] = field(default_factory=list)
    notes: str = ""
    origin: CapabilityOrigin = "POTENTIAL"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class Evidence:
    evidence_id: str
    component_id: str | None
    evidence_class: EvidenceClass
    verification_status: VerificationStatus
    file_path: str | None = None
    line_start: int | None = None
    line_end: int | None = None
    content_digest: str | None = None
    collection_method: str = "deterministic_rule"
    source_commit: str | None = None
    observed_at: str | None = None
    limitations: list[str] = field(default_factory=list)
    summary: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class Finding:
    finding_id: str
    rule_id: str
    title: str
    severity: Severity
    confidence: VerificationStatus
    description: str
    component_ids: list[str]
    evidence_ids: list[str]
    capabilities: list[str] = field(default_factory=list)
    attacker_control: str = ""
    entry_point: str = ""
    trust_boundary: str = ""
    impact: str = ""
    missing_controls: list[str] = field(default_factory=list)
    recommended_action: str = ""
    exploitability: str = "UNKNOWN"
    exposure: str = "UNKNOWN"
    finding_class: FindingClass = "SECURITY_FINDING"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class Relationship:
    relationship_id: str
    kind: str
    from_component_id: str
    to_component_id: str
    evidence_ids: list[str] = field(default_factory=list)
    status: VerificationStatus = "POTENTIAL"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class StructuredClaim:
    """Intermediate agent claim that a deterministic validator can check."""

    claim: str
    status: VerificationStatus
    evidence_ids: list[str]
    impact: str = ""
    missing_evidence: list[str] = field(default_factory=list)
    component_ids: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
