"""Argparse construction for the AESA Guard CLI."""

from __future__ import annotations

import argparse
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="aesa",
        description=(
            "AESA Guard — discover what AI-agent ecosystems can access, execute, and trust"
        ),
    )
    sub = parser.add_subparsers(dest="command", required=True)

    scan = sub.add_parser(
        "scan",
        help="One-command Guard scan: inventory + deterministic security findings",
    )
    scan.add_argument("path", type=Path, nargs="?", default=Path("."))
    scan.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        help="Output directory (default: <path>/aesa-out)",
    )
    scan.add_argument(
        "--baseline",
        type=Path,
        help="Prior baseline.json for risk delta",
    )
    scan.add_argument(
        "--save-baseline",
        type=Path,
        help="Write baseline.json after scan",
    )
    scan.add_argument(
        "--fail-on",
        choices=["never", "high", "any"],
        default="never",
        help="Exit non-zero when findings match policy (default: never)",
    )

    explain = sub.add_parser("explain", help="Explain a finding from a prior scan")
    explain.add_argument("finding_id", help="Finding id such as F-001")
    explain.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        default=Path("aesa-out"),
        help="Directory containing findings.json (default: aesa-out)",
    )

    baseline = sub.add_parser("baseline", help="Save or show Guard baselines")
    baseline_sub = baseline.add_subparsers(dest="baseline_cmd", required=True)
    b_save = baseline_sub.add_parser("save", help="Save baseline from findings.json")
    b_save.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        default=Path("aesa-out"),
        help="Scan output directory containing findings.json",
    )
    b_save.add_argument(
        "--path",
        type=Path,
        help="Baseline destination (default: <output-dir>/baseline.json)",
    )
    b_show = baseline_sub.add_parser("show", help="Print a baseline.json")
    b_show.add_argument("path", type=Path, nargs="?", default=Path("aesa-out/baseline.json"))

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
    claim = val_sub.add_parser("claim", help="Validate a structured agent claim JSON object")
    claim.add_argument("path", type=Path)

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
    diff_risk = diff_sub.add_parser(
        "risk",
        help="Diff current findings.json against a baseline.json",
    )
    diff_risk.add_argument("baseline", type=Path)
    diff_risk.add_argument("findings", type=Path)

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
        help="AgentSecBench: detection quality benchmark (fixtures + scoring stubs)",
    )
    bench_sub = bench.add_subparsers(dest="benchmark_cmd", required=True)
    bench_sub.add_parser("run", help="Run benchmark pack cases")

    deps = sub.add_parser(
        "deps",
        help="Check/upgrade dependencies (uv.lock; constraints stay in pyproject.toml)",
    )
    deps_sub = deps.add_subparsers(dest="deps_cmd", required=True)
    deps_sub.add_parser("outdated", help="Compare uv.lock pins to latest PyPI")
    dep_up = deps_sub.add_parser(
        "upgrade",
        help="Bump lock via uv lock --upgrade (does not rewrite pyproject constraints)",
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
