from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError

from aesa.paths import (
    canonical_schema_path,
    published_schema_paths,
    repo_root,
    version_file_path,
    versions_path,
)


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


def load_versions() -> dict:
    return json.loads(versions_path().read_text(encoding="utf-8"))


def check_version_metadata() -> None:
    versions = load_versions()
    product = version_file_path().read_text(encoding="utf-8").strip()
    if versions.get("aesa_product") != product:
        raise SystemExit(
            f"VERSION file ({product}) != canonical/versions.json aesa_product "
            f"({versions.get('aesa_product')})"
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


def check_internal_markdown_links() -> list[str]:
    root = repo_root()
    checked: list[str] = []
    for md in sorted(root.rglob("*.md")):
        if "aesa-independent-assessment" in md.parts:
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


from aesa.prompt_build import write_monolith


def build_all() -> dict[str, list[str] | str]:
    sync = sync_schemas()
    check_schema_parity()
    check_version_metadata()
    validate_json_schema_document()
    examples = validate_examples()
    check_prompt_manifest()
    mono = write_monolith(check_only=True)
    links = check_internal_markdown_links()
    return {
        "schemas": sync,
        "examples": examples,
        "monolith": mono,
        "markdown_files_link_checked": links,
        "status": "ok",
    }
