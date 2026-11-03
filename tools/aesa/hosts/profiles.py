"""Declarative host profiles for Cursor and Claude Code (extensible).

Profiles describe *where* host configuration usually lives and which permission
claims are **declared** in files versus **effective** only after host runtime
verification. Effective permissions are never inferred from profile presence alone.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

SupportLevel = Literal["SUPPORTED", "PARTIAL", "MANUAL_ONLY", "UNSUPPORTED"]
PermissionKind = Literal["declared", "effective"]


@dataclass(frozen=True, slots=True)
class HostConfigSurface:
    path_glob: str
    description: str
    permission_kind: PermissionKind
    notes: str = ""


@dataclass(frozen=True, slots=True)
class HostProfile:
    host_id: str
    display_name: str
    support: SupportLevel
    config_surfaces: tuple[HostConfigSurface, ...]
    declared_permission_fields: tuple[str, ...]
    effective_permission_requires: tuple[str, ...]
    limitations: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["config_surfaces"] = [asdict(s) for s in self.config_surfaces]
        return data


HOST_PROFILES: dict[str, HostProfile] = {
    "cursor": HostProfile(
        host_id="cursor",
        display_name="Cursor",
        support="PARTIAL",
        config_surfaces=(
            HostConfigSurface(
                ".cursor/mcp.json",
                "MCP server registrations for the Cursor host",
                "declared",
            ),
            HostConfigSurface(
                ".cursor/rules/**",
                "Project rules / instruction packs",
                "declared",
            ),
            HostConfigSurface(
                ".cursorrules",
                "Legacy root instruction file",
                "declared",
            ),
            HostConfigSurface(
                "AGENTS.md",
                "Agent instruction surface often loaded by Cursor workflows",
                "declared",
            ),
            HostConfigSurface(
                "skills/**/SKILL.md",
                "Skill packs discoverable by the host",
                "declared",
            ),
        ),
        declared_permission_fields=(
            "mcpServers.*.command",
            "mcpServers.*.url",
            "mcpServers.*.env",
            "mcpServers.*.args",
        ),
        effective_permission_requires=(
            "Host tool allowlist / approval mode (NOT VERIFIED from repo files alone)",
            "Whether MCP registrations are enabled for the active workspace",
            "OS identity and environment inheritance of the Cursor process",
        ),
        limitations=(
            "Repository files declare intent; Cursor runtime enforcement is MANUAL_ONLY.",
            "Absence of .cursor/ does not prove the host is unused.",
        ),
    ),
    "claude-code": HostProfile(
        host_id="claude-code",
        display_name="Claude Code",
        support="PARTIAL",
        config_surfaces=(
            HostConfigSurface(
                ".claude/**",
                "Claude Code project configuration / local settings",
                "declared",
            ),
            HostConfigSurface(
                "CLAUDE.md",
                "Project memory / instruction file commonly loaded by Claude Code",
                "declared",
            ),
            HostConfigSurface(
                ".mcp.json",
                "MCP registrations (Claude Code / shared layouts)",
                "declared",
            ),
            HostConfigSurface(
                "skills/**/SKILL.md",
                "Skill packs",
                "declared",
            ),
            HostConfigSurface(
                "hooks/**",
                "Lifecycle hooks if present",
                "declared",
            ),
        ),
        declared_permission_fields=(
            "mcp server command/url/env",
            "permission mode declarations in settings when present",
            "hook command registrations",
        ),
        effective_permission_requires=(
            "Claude Code permission mode actually enforced at runtime",
            "Whether hooks run with inherited credentials",
            "Whether CLAUDE.md / skills are auto-loaded for the session",
        ),
        limitations=(
            "Declared settings are SOURCE_STATIC evidence only.",
            "Effective sandbox/approval behavior requires authorized host or runtime validation.",
        ),
    ),
    "github-copilot": HostProfile(
        host_id="github-copilot",
        display_name="GitHub Copilot",
        support="MANUAL_ONLY",
        config_surfaces=(
            HostConfigSurface(
                ".github/copilot-instructions.md",
                "Repository Copilot custom instructions (when used)",
                "declared",
            ),
            HostConfigSurface(
                ".github/instructions/**",
                "Path-scoped instruction files (emerging layouts)",
                "declared",
            ),
        ),
        declared_permission_fields=("instruction markdown only",),
        effective_permission_requires=(
            "Copilot agent / coding-agent tool permissions (org and IDE settings)",
            "Whether custom instructions are enabled for the repository",
        ),
        limitations=(
            "Reliable effective-permission evidence is rarely present in-repo; profile is MANUAL_ONLY.",
            "Do not treat instruction files as proof of tool execution rights.",
        ),
    ),
}


def list_host_profiles() -> list[dict[str, Any]]:
    return [p.to_dict() for p in HOST_PROFILES.values()]


def get_host_profile(host_id: str) -> HostProfile | None:
    return HOST_PROFILES.get(host_id)
