"""Pre-install verdict for a candidate skill/MCP package (`aesa vet`).

Clones a remote Git URL into a throwaway directory with hooks disabled, no
submodules, and no LFS smudge — then runs a Guard scan. Never executes target
application code.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from aesa.security.gating import is_gate_finding
from aesa.security.scan import run_scan

_GITHUB_SHORTHAND = re.compile(
    r"^(?:https?://github\.com/|git@github\.com:)?([\w.-]+)/([\w.-]+?)(?:\.git)?(?:/.*)?$",
    re.IGNORECASE,
)


def resolve_vet_source(source: str) -> tuple[str, str]:
    """Return (kind, normalized) where kind is ``path`` or ``git``."""
    raw = source.strip()
    as_path = Path(raw).expanduser()
    if as_path.exists():
        return "path", str(as_path.resolve())
    if "://" in raw or raw.startswith("git@") or _GITHUB_SHORTHAND.match(raw):
        return "git", _normalize_git_url(raw)
    raise ValueError(
        f"Cannot resolve vet source {source!r}: expected a local path or GitHub URL/shorthand"
    )


def _normalize_git_url(raw: str) -> str:
    match = _GITHUB_SHORTHAND.match(raw)
    if match and "://" not in raw and not raw.startswith("git@"):
        owner, repo = match.group(1), match.group(2)
        return f"https://github.com/{owner}/{repo}.git"
    return raw


def _safe_clone(url: str, dest: Path) -> None:
    """Shallow clone with supply-chain safety flags; never run remote hooks."""
    dest.mkdir(parents=True, exist_ok=True)
    # Empty hooks dir works on Windows and POSIX (avoids /dev/null hooksPath).
    hooks = dest.parent / "empty-hooks"
    hooks.mkdir(parents=True, exist_ok=True)
    cmd = [
        "git",
        "-c",
        f"core.hooksPath={hooks}",
        "-c",
        "filter.lfs.smudge=",
        "-c",
        "filter.lfs.required=false",
        "clone",
        "--depth",
        "1",
        "--single-branch",
        "--no-recurse-submodules",
        url,
        str(dest),
    ]
    subprocess.run(cmd, check=True, capture_output=True, text=True)


def _verdict(scan: Any) -> str:
    gated = [f for f in scan.findings if is_gate_finding(f)]
    critical = [f for f in gated if f.severity == "CRITICAL"]
    high = [f for f in gated if f.severity == "HIGH"]
    if critical:
        return "REJECT"
    if high:
        return "REVIEW"
    if gated:
        return "REVIEW"
    return "ACCEPT_WITH_COVERAGE_GAPS"


def render_vet_report(
    *,
    source: str,
    resolved: str,
    scan: Any,
    coverage_note: str,
) -> str:
    gated = [f for f in scan.findings if is_gate_finding(f)]
    verdict = _verdict(scan)
    lines = [
        "AESA vet — pre-install authority verdict",
        f"source: {source}",
        f"resolved: {resolved}",
        f"verdict: {verdict}",
        coverage_note,
        "",
        "Authority introduced (gated findings first):",
    ]
    show = gated or [f for f in scan.findings if f.finding_class != "CAPABILITY"][:5]
    if not show:
        lines.append("  (no gated EXPOSURE/SECURITY_FINDING — still check coverage gaps)")
    for finding in show[:12]:
        pin = f" [{finding.evidence_strength}]" if finding.evidence_strength else ""
        lines.append(f"  - {finding.severity}{pin} {finding.rule_id}: {finding.title}")
        if finding.fix_snippet:
            lines.append(f"    fix: {finding.fix_snippet}")
        if finding.verify_in_60s:
            lines.append(f"    verify: {finding.verify_in_60s}")
    caps = sum(1 for f in scan.findings if f.finding_class == "CAPABILITY")
    lines.append("")
    lines.append(
        f"summary: components="
        f"{len(scan.inventory.get('components') or [])} "
        f"gated={len(gated)} capabilities={caps}"
    )
    lines.append("Passive scan only — did not install packages, start MCP servers, or run hooks.")
    return "\n".join(lines)


def run_vet(
    source: str,
    *,
    output_dir: Path | None = None,
    keep_clone: bool = False,
) -> tuple[str, int]:
    kind, resolved = resolve_vet_source(source)
    tmp_root: Path | None = None
    target: Path
    try:
        if kind == "path":
            target = Path(resolved)
        else:
            tmp_root = Path(tempfile.mkdtemp(prefix="aesa-vet-"))
            target = tmp_root / "src"
            try:
                _safe_clone(resolved, target)
            except subprocess.CalledProcessError as exc:
                err = (exc.stderr or exc.stdout or str(exc)).strip()
                return f"AESA vet failed to clone {resolved}: {err}", 2
            except FileNotFoundError:
                return "AESA vet requires `git` on PATH for remote sources.", 2

        out = output_dir or (tmp_root / "aesa-out" if tmp_root else Path("aesa-out"))
        scan, _payload, code = run_scan(target, output_dir=out, fail_on="high", policy=None)
        cov = scan.coverage or {}
        supported = cov.get("deterministically_discovered") or cov.get("supported") or "?"
        not_verified = cov.get("not_verified") or []
        coverage_note = (
            f"coverage: deterministic={supported}; "
            f"NOT VERIFIED families={len(not_verified)} "
            "(no findings ≠ safe on MANUAL_ONLY/PARTIAL surfaces)"
        )
        text = render_vet_report(
            source=source,
            resolved=resolved,
            scan=scan,
            coverage_note=coverage_note,
        )
        # Exit: 0 accept-ish, 1 review/reject gated, 2 tooling failure
        verdict = _verdict(scan)
        exit_code = 0 if verdict == "ACCEPT_WITH_COVERAGE_GAPS" else 1
        if code and exit_code == 0:
            exit_code = code
        return text, exit_code
    finally:
        if tmp_root is not None and not keep_clone:
            shutil.rmtree(tmp_root, ignore_errors=True)
