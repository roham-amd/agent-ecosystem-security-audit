"""Command handlers — one cohesive module, low coupling to argparse construction."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import cast

from aesa.audit import ProfileName, run_audit
from aesa.audit_diff import diff_graphs, diff_reports
from aesa.benchmark.runner import run_benchmark
from aesa.build import build_all, sync_schemas
from aesa.corpus.runner import run_corpus
from aesa.deps import outdated_report, upgrade_pins
from aesa.export.sarif import report_to_sarif
from aesa.inventory.collector import collect_inventory, inventory_to_json
from aesa.jsonio import print_json, read_json, write_json
from aesa.lint import run_ruff
from aesa.prompt_build import write_monolith
from aesa.supply_chain.digest import sha256_file, verify_file_digest
from aesa.supply_chain.manifest import build_digest_manifest
from aesa.validate_report import (
    analyze_graph_paths,
    validate_graph_file,
    validate_report_file,
)


def _print_validation(path: Path, *, ok: bool, issues: list) -> int:
    if not ok:
        for issue in issues:
            loc = f" ({issue.path})" if issue.path else ""
            print(f"{issue.code}{loc}: {issue.message}")
        return 1
    print(f"OK: {path}")
    return 0


def _write_or_print(data: object, output: Path | None) -> int:
    if output is not None:
        write_json(output, data)
        print(f"Wrote {output}")
    else:
        print_json(data)
    return 0


def dispatch(args: argparse.Namespace) -> int:
    command = args.command

    match command:
        case "build":
            return _cmd_build(args)
        case "validate":
            return _cmd_validate(args)
        case "graph":
            return _cmd_graph(args)
        case "inventory":
            return _cmd_inventory(args)
        case "audit":
            return _cmd_audit(args.path, args.profile, args.output_dir)
        case "preflight":
            return _cmd_audit(args.path, "quick", args.output_dir)
        case "verify":
            return _cmd_verify(args)
        case "diff":
            return _cmd_diff(args)
        case "export":
            return _cmd_export(args)
        case "corpus":
            return _cmd_corpus()
        case "benchmark":
            return _cmd_benchmark(args)
        case "deps":
            return _cmd_deps(args)
        case "lint":
            return _cmd_lint(args)
        case _:
            return 2


def _cmd_build(args: argparse.Namespace) -> int:
    match args.target:
        case "schemas":
            for line in sync_schemas():
                print(line)
        case "prompts":
            print_json(write_monolith(check_only=not args.write))
        case _:
            print_json(build_all())
    return 0


def _cmd_validate(args: argparse.Namespace) -> int:
    semantic = not args.no_semantic
    match args.validate_cmd:
        case "report":
            report_result = validate_report_file(args.path, semantic=semantic)
            return _print_validation(args.path, ok=report_result.ok, issues=report_result.issues)
        case "graph":
            graph_result = validate_graph_file(args.path, semantic=semantic)
            return _print_validation(args.path, ok=graph_result.ok, issues=graph_result.issues)
        case _:
            return 2


def _cmd_graph(args: argparse.Namespace) -> int:
    if args.graph_cmd != "paths":
        return 2
    found = analyze_graph_paths(args.path)
    print_json([path.__dict__ for path in found])
    return 0


def _cmd_inventory(args: argparse.Namespace) -> int:
    result = collect_inventory(args.path)
    return _write_or_print(inventory_to_json(result), args.output)


def _cmd_audit(path: Path, profile: str, output_dir: Path | None) -> int:
    payload = run_audit(
        path,
        profile=cast(ProfileName, profile),
        output_dir=output_dir,
    )
    print(payload["summary"])
    return 0


def _cmd_verify(args: argparse.Namespace) -> int:
    match args.verify_cmd:
        case "digest":
            if args.expected:
                ok, actual = verify_file_digest(args.path, args.expected)
                print_json({"ok": ok, "sha256": actual})
                return 0 if ok else 1
            print_json({"sha256": sha256_file(args.path)})
            return 0
        case "manifest":
            return _write_or_print(build_digest_manifest(args.path), args.output)
        case _:
            return 2


def _cmd_diff(args: argparse.Namespace) -> int:
    base = read_json(args.base)
    target = read_json(args.target)
    match args.diff_kind:
        case "report":
            print_json(diff_reports(base, target))
            return 0
        case "graph":
            print_json(diff_graphs(base, target))
            return 0
        case _:
            return 2


def _cmd_export(args: argparse.Namespace) -> int:
    if args.export_cmd != "sarif":
        return 2
    sarif_doc = report_to_sarif(read_json(args.report))
    if args.output:
        write_json(args.output, sarif_doc)
        count = len(sarif_doc["runs"][0]["results"])
        print(f"Wrote {args.output} ({count} results)")
    else:
        print_json(sarif_doc)
    return 0


def _cmd_corpus() -> int:
    summary = run_corpus()
    print_json(summary)
    return 0 if summary.get("failed", 0) == 0 else 1


def _cmd_benchmark(args: argparse.Namespace) -> int:
    if args.benchmark_cmd != "run":
        return 2
    summary = run_benchmark()
    print_json(summary)
    return 0 if summary.get("failed", 0) == 0 else 1


def _cmd_deps(args: argparse.Namespace) -> int:
    match args.deps_cmd:
        case "outdated":
            report = outdated_report()
            print_json(report)
            return 1 if report.get("outdated_count") or report.get("errors") else 0
        case "upgrade":
            result = upgrade_pins(dry_run=args.dry_run, requires_python=">=3.15")
            print_json(result)
            return 0 if result.get("ok") else 1
        case _:
            return 2


def _cmd_lint(args: argparse.Namespace) -> int:
    summary = run_ruff(
        fix=args.fix,
        format_code=args.format_code,
        check_format=args.check_format and not args.format_code,
    )
    return 0 if summary.get("ok") else 1
