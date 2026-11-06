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
        help="Output directory (default: ./aesa-out in the current working directory)",
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
        default=None,
        help="Exit non-zero when findings match policy (default: never, or .aesa.yml)",
    )
    scan.add_argument(
        "--policy",
        type=Path,
        help="Path to .aesa.yml (default: only inside the scan target tree)",
    )
    scan.add_argument(
        "--no-policy",
        action="store_true",
        help="Ignore .aesa.yml even if present",
    )
    scan.add_argument(
        "--agent",
        action="store_true",
        help="Emit compact agent JSON digest (fenced evidence; token-bounded)",
    )

    doctor = sub.add_parser(
        "doctor",
        help="Map authority on this machine's Cursor/Claude/VS Code host configs",
    )
    doctor.add_argument(
        "--home",
        type=Path,
        help="Override home directory (default: user home; local-only)",
    )
    doctor.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        help="Optional directory for per-surface scan artifacts",
    )
    doctor.add_argument(
        "--fail-on",
        choices=["never", "high", "any"],
        default=None,
        help="Optional exit policy across host surfaces",
    )
    doctor.add_argument(
        "--agent",
        action="store_true",
        help="Emit compact agent JSON digest instead of the text map",
    )

    vet = sub.add_parser(
        "vet",
        help="Pre-install verdict for a local path or GitHub URL (safe shallow clone)",
    )
    vet.add_argument("source", help="Local path, Git URL, or owner/repo GitHub shorthand")
    vet.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        help="Optional output directory for scan artifacts",
    )
    vet.add_argument(
        "--keep-clone",
        action="store_true",
        help="Keep the temporary clone directory (remote sources only)",
    )
    vet.add_argument(
        "--agent",
        action="store_true",
        help="Emit compact agent JSON digest (verdict + gated findings)",
    )

    harden = sub.add_parser(
        "harden",
        help="Propose least-privilege config patches from a prior findings.json (dry-run)",
    )
    harden.add_argument(
        "--findings",
        type=Path,
        default=Path("aesa-out/findings.json"),
        help="Path to findings.json (default: aesa-out/findings.json)",
    )
    harden.add_argument(
        "--apply",
        action="store_true",
        help="Request automatic apply (disabled; always dry-run in this release)",
    )

    init_manifest = sub.add_parser(
        "init-manifest",
        help="Draft AUTHORITY.yml from observed inventory (declared vs observed)",
    )
    init_manifest.add_argument("path", type=Path, nargs="?", default=Path("."))
    init_manifest.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing AUTHORITY.yml",
    )

    verify_manifest = sub.add_parser(
        "verify-manifest",
        help="Diff observed inventory against AUTHORITY.yml",
    )
    verify_manifest.add_argument("path", type=Path, nargs="?", default=Path("."))
    verify_manifest.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Optional path to write the verify report JSON",
    )

    init_gate = sub.add_parser(
        "init-gate",
        help="Write a starter .aesa.yml and consumer workflow stub into a repo",
    )
    init_gate.add_argument("path", type=Path, nargs="?", default=Path("."))
    init_gate.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing .aesa.yml / workflow stub",
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
    explain.add_argument(
        "--agent",
        action="store_true",
        help="Emit structured remediation JSON for agents",
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
        help="Output directory (default: ./aesa-out in the current working directory)",
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
        help="Output directory (default: ./aesa-out in the current working directory)",
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

    annotate = sub.add_parser(
        "annotate",
        help="Emit CI annotations from findings.json (GitHub Actions workflow commands)",
    )
    annotate.add_argument(
        "findings",
        type=Path,
        nargs="?",
        default=Path("aesa-out/findings.json"),
        help="Path to findings.json (default: aesa-out/findings.json)",
    )
    annotate.add_argument(
        "--format",
        choices=["github", "text", "pr-comment"],
        default="github",
        dest="annotate_format",
        help="Annotation format (default: github; pr-comment = ≤12-line Authority Diff)",
    )
    annotate.add_argument(
        "--risk-delta",
        type=Path,
        help="Optional risk-delta.json for delta-first PR comments",
    )

    pilots = sub.add_parser("pilots", help="Run curated pilot-repository Guard scans")
    pilots_sub = pilots.add_subparsers(dest="pilots_cmd", required=True)
    pilots_run = pilots_sub.add_parser("run", help="Scan all enabled pilots in the manifest")
    pilots_run.add_argument(
        "--manifest",
        type=Path,
        help="Pilot manifest path (default: docs/pilots/manifest.json)",
    )
    pilots_run.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        help="Results directory (default: docs/pilots/results)",
    )
    pilots_run.add_argument(
        "--only",
        nargs="+",
        help="Optional pilot ids to run",
    )
    pilots_list = pilots_sub.add_parser("list", help="List pilots from the manifest")
    pilots_list.add_argument(
        "--manifest",
        type=Path,
        help="Pilot manifest path (default: docs/pilots/manifest.json)",
    )

    hosts = sub.add_parser("hosts", help="List or show agent-host assessment profiles")
    hosts_sub = hosts.add_subparsers(dest="hosts_cmd", required=True)
    hosts_sub.add_parser("list", help="List built-in host profiles")
    hosts_show = hosts_sub.add_parser("show", help="Show one host profile")
    hosts_show.add_argument("host_id", help="Host id such as cursor or claude-code")

    corp = sub.add_parser("corpus", help="Security regression corpus harness")
    corp_sub = corp.add_subparsers(dest="corpus_cmd", required=True)
    corp_sub.add_parser("run", help="Run all corpus cases")

    bench = sub.add_parser(
        "benchmark",
        help="AgentSecBench: deterministic + LLM detection-quality benchmarks",
    )
    bench_sub = bench.add_subparsers(dest="benchmark_cmd", required=True)
    bench_sub.add_parser(
        "run",
        help="Deterministic inventory + Guard rule expectations (no models)",
    )
    bench_sub.add_parser(
        "rules",
        help="Rule-quality pack: positive/negative/ambiguous fixtures per rule",
    )
    bench_llm = bench_sub.add_parser(
        "llm",
        help="Score model-agnostic agent submission JSON against ground truth",
    )
    bench_llm.add_argument(
        "--submissions",
        type=Path,
        help="Directory of agent submission *.json files (required for scoring)",
    )
    bench_llm.add_argument(
        "--validate-only",
        action="store_true",
        help="Validate LLM case/ground-truth fixtures without scoring submissions",
    )
    bench_llm.add_argument(
        "--split",
        choices=["public", "held_out", "all"],
        default="all",
        help="Score/validate only public, held-out, or all cases (default: all)",
    )
    bench_llm.add_argument(
        "--report",
        action="store_true",
        help="Emit a transparent per-agent/per-case evaluation report (requires --submissions)",
    )
    bench_llm.add_argument(
        "--provenance",
        choices=["external", "pilot", "sample", "template", "any"],
        default="any",
        help="Label the report's provenance class (default: any). Use external for credibility reports.",
    )
    bench_sub.add_parser(
        "governance",
        help="Verify AgentSecBench-LLM dataset checksums and pinned versions",
    )
    bench_contract = bench_sub.add_parser(
        "contract",
        help="Verify the frozen AgentSecBench-LLM evaluation contract",
    )
    contract_sub = bench_contract.add_subparsers(dest="contract_cmd", required=True)
    contract_sub.add_parser("verify", help="Verify pins, freeze flag, and dataset integrity")
    bench_intake = bench_sub.add_parser(
        "intake",
        help="Validate and preserve a submission directory into the external vault",
    )
    bench_intake.add_argument("source", type=Path, help="Directory of LLM-*.json submission files")
    bench_intake.add_argument("--agent-id", required=True, help="Submitter / agent identifier")
    bench_intake.add_argument(
        "--provenance",
        choices=["external", "pilot", "sample", "template"],
        default="external",
        help="Provenance class (only external counts as external evidence)",
    )
    bench_intake.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate without writing to the vault",
    )
    bench_sub.add_parser(
        "intakes",
        help="List vault registry entries and valid external evidence counts",
    )
    bench_sub.add_parser(
        "collection-status",
        help="Honest outreach funnel: invitations vs responses vs valid intakes",
    )
    bench_pkg = bench_sub.add_parser(
        "submitter-package",
        help="Build task cards without ground truth for external submitters",
    )
    bench_pkg.add_argument(
        "-o",
        "--output",
        type=Path,
        required=True,
        help="Output directory for the submitter package",
    )

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
