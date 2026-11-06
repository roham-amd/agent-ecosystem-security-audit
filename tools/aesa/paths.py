from __future__ import annotations

from functools import lru_cache
from importlib import resources
from pathlib import Path

DEFAULT_OUTPUT_DIR_NAME = "aesa-out"


def repo_root() -> Path:
    """Return the monorepo root when running from a git checkout.

    Installed wheels do not ship the monorepo layout. Callers that need
    checkout-only assets (schemas, corpus, prompts) must handle ``None`` /
    missing paths — never assume this resolves under site-packages.
    """
    return Path(__file__).resolve().parents[2]


def in_source_checkout() -> bool:
    """True when ``VERSION`` exists two levels above the package (dev tree)."""
    return (Path(__file__).resolve().parents[2] / "VERSION").is_file()


@lru_cache(maxsize=1)
def package_data_root() -> Path | None:
    """Directory of packaged data files, if the wheel shipped them."""
    try:
        base = resources.files("aesa")
        # Traversable may be in a zip; convert when on the filesystem.
        with resources.as_file(base) as path:
            return path
    except (FileNotFoundError, ModuleNotFoundError, TypeError, OSError):
        return None


def canonical_schema_path() -> Path:
    return repo_root() / "canonical" / "schemas" / "audit-report.schema.json"


def published_schema_paths() -> tuple[Path, Path]:
    root = repo_root() / "schemas"
    return (
        root / "audit-report.schema.json",
        root / "AI_Agent_Ecosystem_Security_Audit_v1.schema.json",
    )


def versions_path() -> Path:
    """Prefer checkout canonical versions; fall back to packaged copy."""
    checkout = repo_root() / "canonical" / "versions.json"
    if checkout.is_file():
        return checkout
    packaged = Path(__file__).resolve().parent / "data" / "versions.json"
    return packaged


def version_file_path() -> Path:
    """Prefer checkout VERSION; fall back to packaged copy."""
    checkout = repo_root() / "VERSION"
    if checkout.is_file():
        return checkout
    return Path(__file__).resolve().parent / "data" / "VERSION"


def resolve_default_output_dir() -> Path:
    """Default artifact directory: cwd ``aesa-out``, never under the scan target.

    Writing into the target tree pollutes later inventories and contradicts the
    passive / read-only assessment model when scanning an external repository.
    """
    return (Path.cwd() / DEFAULT_OUTPUT_DIR_NAME).resolve()
