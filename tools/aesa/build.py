from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from jsonschema import Draft202012Validator

from aesa.deps import ensure_lock_in_sync, parse_declared_requirements, parse_lock_pins
from aesa.paths import (
    canonical_schema_path,
    published_schema_paths,
    repo_root,
    version_file_path,
)
from aesa.pins import normalize_package_name
from aesa.prompt_build import write_monolith
from aesa.versioning import load_versions as load_canonical_versions


def _sha256(path: Path) -> str:
    return hashlib.file_digest(path.open("rb"), "sha256").hexdigest()


def sync_schemas() -> list[str]:
    """Copy canonical schema to published aliases; return actions."""
    src = canonical_schema_path()
    if not src.is_file():
        raise FileNotFoundError(f"Missing canonical schema: {src}")
    actions: list[str] = []
    for dest in published_schema_paths():
        dest.parent.mkdir(parents=True, exist_ok=True)
        data = src.read_bytes()
        if dest.is_file() and dest.read_bytes() == data:
            actions.append(f"unchanged {dest.relative_to(repo_root())}")
        else:
            dest.write_bytes(data)
            actions.append(f"updated {dest.relative_to(repo_root())}")
    return actions


def check_schema_parity() -> None:
    src = canonical_schema_path()
    for dest in published_schema_paths():
        if not dest.is_file():
            raise SystemExit(f"Missing published schema: {dest}")
        if _sha256(src) != _sha256(dest):
            raise SystemExit(
                f"Schema drift: {dest} does not match canonical {src}. Run: aesa build schemas"
            )


def load_versions() -> dict[str, object]:
    """Compatibility wrapper — prefer ``aesa.versioning.load_versions``."""
    data = load_canonical_versions()
    if not isinstance(data, dict):
        raise SystemExit(f"Invalid versions.json: expected object, got {type(data).__name__}")
    return dict(data)


def check_requires_python() -> None:
    pyproject = (repo_root() / "tools" / "pyproject.toml").read_text(encoding="utf-8")
    match = re.search(r'^requires-python\s*=\s*"([^"]+)"', pyproject, re.MULTILINE)
    if not match:
        raise SystemExit("tools/pyproject.toml missing requires-python")
    required = match.group(1).strip()
    if required != ">=3.15":
        raise SystemExit(
            f"tools/pyproject.toml requires-python must be '>=3.15' (found {required!r})"
        )


def check_version_metadata() -> None:
    versions = load_versions()
    product = version_file_path().read_text(encoding="utf-8").strip()
    if versions.get("aesa_product") != product:
        raise SystemExit(
            f"VERSION file ({product}) != canonical/versions.json aesa_product "
            f"({versions.get('aesa_product')})"
        )

    # Keep tooling package metadata aligned with canonical build_tool tag.
    build_tool = str(versions.get("build_tool") or "")
    expected_pkg = build_tool.removeprefix("aesa-tools-")
    pyproject = (repo_root() / "tools" / "pyproject.toml").read_text(encoding="utf-8")
    match = re.search(r'^version\s*=\s*"([^"]+)"', pyproject, re.MULTILINE)
    if not match:
        raise SystemExit("tools/pyproject.toml missing version")
    if expected_pkg and match.group(1) != expected_pkg:
        raise SystemExit(
            f"tools/pyproject.toml version ({match.group(1)}) != "
            f"canonical build_tool package version ({expected_pkg})"
        )

    init_text = (repo_root() / "tools" / "aesa" / "__init__.py").read_text(encoding="utf-8")
    init_match = re.search(r'__version__\s*=\s*"([^"]+)"', init_text)
    if not init_match:
        raise SystemExit("tools/aesa/__init__.py missing __version__")
    if expected_pkg and init_match.group(1) != expected_pkg:
        raise SystemExit(
            f"tools/aesa/__init__.py __version__ ({init_match.group(1)}) != "
            f"canonical build_tool package version ({expected_pkg})"
        )

    # Release-blocking: release-manifest must agree with VERSION + package version.
    manifest_path = repo_root() / "canonical" / "release-manifest.json"
    if not manifest_path.is_file():
        raise SystemExit("Missing canonical/release-manifest.json")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("product_version") != product:
        raise SystemExit(
            f"release-manifest product_version ({manifest.get('product_version')}) != "
            f"VERSION ({product})"
        )
    if expected_pkg and manifest.get("package_version") != expected_pkg:
        raise SystemExit(
            f"release-manifest package_version ({manifest.get('package_version')}) != "
            f"canonical build_tool package version ({expected_pkg})"
        )
    for key in ("findings_contract", "baseline_contract", "rule_pack"):
        if key in versions and manifest.get("contracts", {}).get(key) != versions.get(key):
            raise SystemExit(
                f"release-manifest contracts.{key} "
                f"({manifest.get('contracts', {}).get(key)}) != "
                f"versions.json {key} ({versions.get(key)})"
            )


def validate_json_schema_document() -> None:
    path = canonical_schema_path()
    schema = json.loads(path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)


def validate_examples() -> list[str]:
    root = repo_root()
    schema = json.loads(canonical_schema_path().read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    results: list[str] = []
    for example in sorted((root / "examples").glob("*.json")):
        if example.name in ("sample-component-inventory.json", "sample-runtime-test-record.json"):
            continue
        doc = json.loads(example.read_text(encoding="utf-8"))
        errors = sorted(validator.iter_errors(doc), key=lambda e: e.path)
        if errors:
            msgs = "; ".join(f"{list(e.path)}: {e.message}" for e in errors[:5])
            raise SystemExit(f"Example failed schema validation: {example.name}: {msgs}")
        results.append(f"ok {example.name}")
    return results


_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


_SKIP_MD_PARTS = frozenset(
    {
        ".venv",
        "venv",
        "node_modules",
        "site-packages",
        ".git",
        "aesa-independent-assessment",
    }
)


def check_internal_markdown_links() -> list[str]:
    root = repo_root()
    checked: list[str] = []
    for md in sorted(root.rglob("*.md")):
        if _SKIP_MD_PARTS.intersection(md.parts):
            continue
        text = md.read_text(encoding="utf-8")
        for target in _LINK_RE.findall(text):
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            resolved = (md.parent / target.split("#", 1)[0]).resolve()
            if not resolved.exists():
                raise SystemExit(f"Broken link in {md.relative_to(root)}: {target}")
        checked.append(str(md.relative_to(root)))
    return checked


def check_prompt_manifest() -> None:
    manifest_path = repo_root() / "canonical" / "prompt-kit.manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for seg in manifest.get("segments", []):
        rel = seg["file"]
        path = repo_root() / rel
        if not path.is_file():
            raise SystemExit(f"Prompt manifest references missing file: {rel}")


def check_dependency_pins() -> list[str]:
    """Ensure ``uv.lock`` is in sync and satisfies declared ``pyproject.toml`` constraints."""
    ensure_lock_in_sync()
    lock = parse_lock_pins()
    normalized = {normalize_package_name(name): ver for name, ver in lock.items()}

    try:
        from packaging.requirements import Requirement
        from packaging.version import Version
    except ImportError as exc:  # pragma: no cover
        raise SystemExit(f"packaging is required for pin checks: {exc}") from exc

    actions: list[str] = [f"ok uv.lock present ({len(lock)} packages)"]
    for req in parse_declared_requirements():
        key = normalize_package_name(req.name)
        locked = normalized.get(key)
        if locked is None:
            raise SystemExit(f"declared requirement {req} missing from uv.lock")
        if req.specifier and not req.specifier.contains(Version(locked), prereleases=True):
            raise SystemExit(f"uv.lock {key}=={locked} does not satisfy {req}")
        actions.append(f"ok {req} -> {locked}")

    # Declared requirement compatibility among locked packages (subset used by AESA).
    declared: dict[str, list[str]] = {
        "jsonschema": [
            "attrs>=22.2.0",
            "jsonschema-specifications>=2023.03.6",
            "referencing>=0.28.4",
            "rpds-py>=0.25.0",
        ],
        "jsonschema-specifications": ["referencing>=0.31.0"],
        "referencing": ["attrs>=22.2.0", "rpds-py>=0.7.0"],
        "pytest": [
            "iniconfig>=2",
            "packaging>=24",
            "pluggy>=1.6,<2",
            "pygments>=2.15",
        ],
    }

    for parent, reqs in declared.items():
        for raw in reqs:
            req = Requirement(raw)
            key = normalize_package_name(req.name)
            pinned = normalized.get(key)
            if pinned is None:
                raise SystemExit(f"uv.lock missing {key} required by {parent}")
            if not req.specifier.contains(Version(pinned), prereleases=True):
                raise SystemExit(
                    f"collision: {parent} needs {raw}, but uv.lock pins {key}=={pinned}"
                )
        actions.append(f"ok {parent} requirements satisfied by uv.lock")

    return actions


def build_all() -> dict[str, object]:
    sync = sync_schemas()
    check_schema_parity()
    check_version_metadata()
    check_requires_python()
    dep_pins = check_dependency_pins()
    validate_json_schema_document()
    examples = validate_examples()
    check_prompt_manifest()
    mono = write_monolith(check_only=True)
    links = check_internal_markdown_links()
    return {
        "schemas": sync,
        "examples": examples,
        "dependency_pins": dep_pins,
        "monolith": mono,
        "markdown_files_link_checked": links,
        "status": "ok",
    }
