"""Single source of product / package version resolution.

Works from a git checkout *and* from an installed wheel. Never assumes
``Path(__file__).parents[2]/VERSION`` exists.
"""

from __future__ import annotations

import json
from functools import lru_cache
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as pkg_version

from aesa.paths import version_file_path, versions_path

# Embedded fallbacks — kept in sync by ``aesa build`` / release checklist.
_EMBEDDED_PRODUCT_VERSION = "3.6.1"
_EMBEDDED_VERSIONS: dict[str, str] = {
    "aesa_product": "3.6.1",
    "audit_procedure": "1.0",
    "audit_report_schema": "1.0",
    "ecosystem_graph_schema": "1.0",
    "audit_manifest_schema": "1.0",
    "test_corpus": "0.3.0",
    "agent_benchmark": "0.3.0",
    "agent_benchmark_llm": "0.3.0",
    "rule_quality_pack": "1.1.0",
    "build_tool": "aesa-tools-0.9.1",
    "findings_contract": "1.2",
    "baseline_contract": "1.3",
    "rule_pack": "1.4",
    "host_profiles": "1.0.0",
    "policy_contract": "1.1",
    "authority_snapshot": "1.0",
}


@lru_cache(maxsize=1)
def load_versions() -> dict[str, str]:
    try:
        path = versions_path()
        if path.is_file():
            data = json.loads(path.read_text(encoding="utf-8"))
            return {str(k): str(v) for k, v in data.items()}
    except (OSError, json.JSONDecodeError):
        pass
    return dict(_EMBEDDED_VERSIONS)


def product_version() -> str:
    try:
        path = version_file_path()
        if path.is_file():
            file_ver = path.read_text(encoding="utf-8").strip()
            if file_ver:
                return file_ver
    except OSError:
        pass
    return load_versions().get("aesa_product") or _EMBEDDED_PRODUCT_VERSION


def package_version() -> str:
    try:
        return pkg_version("aesa-tools")
    except PackageNotFoundError:
        from aesa import __version__

        return __version__
