"""Registry of deterministic discovery adapters (extensibility point)."""

from __future__ import annotations

from aesa.inventory.adapters.claude_settings import discover_claude_settings
from aesa.inventory.adapters.hooks import discover_hooks
from aesa.inventory.adapters.host_components import (
    discover_automations,
    discover_plugins,
    discover_subagents,
)
from aesa.inventory.adapters.hosts import discover_host_profiles
from aesa.inventory.adapters.mcp import discover_mcp_configs
from aesa.inventory.adapters.rules_a2a import discover_agent_cards, discover_instruction_rules
from aesa.inventory.adapters.skills import discover_skills
from aesa.inventory.adapters.toml_config import discover_toml_mcp_configs
from aesa.inventory.adapters.workflows import discover_github_workflows
from aesa.inventory.types import DiscoveryAdapter

# Order is stable for component_id assignment across runs on the same tree.
DISCOVERY_ADAPTERS: tuple[DiscoveryAdapter, ...] = (
    discover_skills,
    discover_mcp_configs,
    discover_toml_mcp_configs,
    discover_claude_settings,
    discover_agent_cards,
    discover_instruction_rules,
    discover_hooks,
    discover_plugins,
    discover_subagents,
    discover_automations,
    discover_github_workflows,
    discover_host_profiles,
)
