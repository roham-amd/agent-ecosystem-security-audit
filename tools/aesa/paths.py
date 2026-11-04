from __future__ import annotations

from pathlib import Path

DEFAULT_OUTPUT_DIR_NAME = "aesa-out"


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def canonical_schema_path() -> Path:
    return repo_root() / "canonical" / "schemas" / "audit-report.schema.json"


def published_schema_paths() -> tuple[Path, Path]:
    root = repo_root() / "schemas"
    return (
        root / "audit-report.schema.json",
        root / "AI_Agent_Ecosystem_Security_Audit_v1.schema.json",
    )


def versions_path() -> Path:
    return repo_root() / "canonical" / "versions.json"


def version_file_path() -> Path:
    return repo_root() / "VERSION"


def resolve_default_output_dir() -> Path:
    """Default artifact directory: cwd ``aesa-out``, never under the scan target.

    Writing into the target tree pollutes later inventories and contradicts the
    passive / read-only assessment model when scanning an external repository.
    """
    return (Path.cwd() / DEFAULT_OUTPUT_DIR_NAME).resolve()
