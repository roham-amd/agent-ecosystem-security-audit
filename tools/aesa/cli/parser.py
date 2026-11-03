"""Argparse construction for the AESA CLI (separated from dispatch)."""

from __future__ import annotations

import argparse
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="aesa",
        description="AESA — agent ecosystem assessment (inventory, audit profiles, validation)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    build = sub.add_parser("build", help="Run build and consistency checks")
    build.add_argument(
        "target",
        nargs="?",
        default="all",
        choices=["all", "schemas", "prompts"],
        help="Build target (default: all)",
    )
    build.add_argument(
        "--write",
        action="store_true",
        help="Write generated monolith (prompts target)",
    )

    val = sub.add_parser("validate", help="Validate AESA JSON artifacts")
    val_sub = val.add_subparsers(dest="validate_cmd", required=True)
    rep = val_sub.add_parser("report", help="Validate audit report summary JSON")
    rep.add_argument("path", type=Path)
    rep.add_argument("--no-semantic", action="store_true")
    graph = val_sub.add_parser("graph", help="Validate ecosystem graph JSON")
    graph.add_argument("path", type=Path)
    graph.add_argument("--no-semantic", action="store_true")

    graph_cmd = sub.add_parser("graph", help="Graph utilities")
    graph_sub = graph_cmd.add_subparsers(dest="graph_cmd", required=True)
    paths = graph_sub.add_parser("paths", help="List auto-discovered attack paths")
    paths.add_argument("path", type=Path)

    inv = sub.add_parser("inventory", help="Passive read-only inventory of a directory")
    inv.add_argument("path", type=Path)
    inv.add_argument("-o", "--output", type=Path, help="Write JSON to file")

    audit = sub.add_parser(
        "audit",
        help="Unified passive assessment: inventory + profile handoff package",
    )
    audit.add_argument("path", type=Path, nargs="?", default=Path("."))
    audit.add_argument(
        "--profile",
        choices=["quick", "standard", "deployment"],
        default="standard",
        help="Assessment profile (default: standard)",
    )
    audit.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        help="Output directory (default: <path>/aesa-out)",
    )

    pre = sub.add_parser(
        "preflight",
        help="Alias of `aesa audit --profile quick` (2.3 compatibility)",
    )
    pre.add_argument("path", type=Path, nargs="?", default=Path("."))
    pre.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        help="Output directory (default: <path>/aesa-out)",
    )

    verify = sub.add_parser("verify", help="Supply-chain verification helpers")
    verify_sub = verify.add_subparsers(dest="verify_cmd", required=True)
    digest = verify_sub.add_parser("digest", help="Compute or verify SHA-256 of a file")
    digest.add_argument("path", type=Path)
    digest.add_argument("--expected", help="Expected sha256 hex digest")
    manifest = verify_sub.add_parser(
        "manifest", help="Build passive digest manifest for a directory"
    )
    manifest.add_argument("path", type=Path)
    manifest.add_argument("-o", "--output", type=Path)

    diff_parser = sub.add_parser("diff", help="Diff audit artifacts")
    diff_sub = diff_parser.add_subparsers(dest="diff_kind", required=True)
    diff_rep = diff_sub.add_parser("report", help="Diff two audit report JSON files")
    diff_rep.add_argument("base", type=Path)
    diff_rep.add_argument("target", type=Path)
    diff_gr = diff_sub.add_parser("graph", help="Diff two ecosystem graph JSON files")
    diff_gr.add_argument("base", type=Path)
    diff_gr.add_argument("target", type=Path)

    export = sub.add_parser("export", help="Export interoperable formats")
    export_sub = export.add_subparsers(dest="export_cmd", required=True)
    sarif_cmd = export_sub.add_parser(
        "sarif", help="Export SARIF 2.1.0 for findings with file evidence"
    )
    sarif_cmd.add_argument("report", type=Path)
    sarif_cmd.add_argument("-o", "--output", type=Path)

    corp = sub.add_parser("corpus", help="Security regression corpus harness")
    corp_sub = corp.add_subparsers(dest="corpus_cmd", required=True)
    corp_sub.add_parser("run", help="Run all corpus cases")

    bench = sub.add_parser(
        "benchmark",
        help="Agent detection quality benchmark (fixtures + scoring stubs)",
    )
    bench_sub = bench.add_subparsers(dest="benchmark_cmd", required=True)
    bench_sub.add_parser("run", help="Run benchmark pack cases")

    deps = sub.add_parser(
        "deps",
        help="Check/upgrade pinned dependencies (ncu-style for constraints/pyproject)",
    )
    deps_sub = deps.add_subparsers(dest="deps_cmd", required=True)
    deps_sub.add_parser("outdated", help="Compare constraints.txt pins to latest PyPI")
    dep_up = deps_sub.add_parser(
        "upgrade",
        help="Bump pins to latest PyPI across constraints/lock/pyproject (like ncu -u)",
    )
    dep_up.add_argument(
        "--dry-run",
        action="store_true",
        help="Show planned bumps without writing files",
    )

    lint = sub.add_parser("lint", help="Run Ruff linter/formatter on tools + tests")
    lint.add_argument(
        "--fix",
        action="store_true",
        help="Apply safe Ruff lint autofixes",
    )
    lint.add_argument(
        "--format",
        action="store_true",
        dest="format_code",
        help="Apply Ruff formatter",
    )
    lint.add_argument(
        "--check-format",
        action="store_true",
        help="Fail if formatter would change files (CI mode)",
    )

    return parser
