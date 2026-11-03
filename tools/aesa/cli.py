from __future__ import annotations

import argparse
import json
from pathlib import Path

from aesa.build import build_all, sync_schemas
from aesa.corpus.runner import run_corpus
from aesa.inventory.collector import collect_inventory, inventory_to_json
from aesa.preflight import run_preflight
from aesa.prompt_build import write_monolith
from aesa.audit_diff import diff_graphs, diff_reports
from aesa.export.sarif import report_to_sarif
from aesa.supply_chain.digest import sha256_file, verify_file_digest
from aesa.supply_chain.manifest import build_digest_manifest
from aesa.validate_report import analyze_graph_paths, validate_graph_file, validate_report_file


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="aesa",
        description="AESA Gate — agent ecosystem inventory, preflight, and audit tooling",
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
    build.add_argument("--write", action="store_true", help="Write generated monolith (prompts target)")

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

    pre = sub.add_parser(
        "preflight",
        help="Passive discovery + coverage map + audit-context for AI deep review",
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
    manifest = verify_sub.add_parser("manifest", help="Build passive digest manifest for a directory")
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
    sarif_cmd = export_sub.add_parser("sarif", help="Export SARIF 2.1.0 for findings with file evidence")
    sarif_cmd.add_argument("report", type=Path)
    sarif_cmd.add_argument("-o", "--output", type=Path)

    corp = sub.add_parser("corpus", help="Security regression corpus harness")
    corp_sub = corp.add_subparsers(dest="corpus_cmd", required=True)
    corp_sub.add_parser("run", help="Run all corpus cases")

    args = parser.parse_args(argv)

    if args.command == "build":
        if args.target == "schemas":
            for line in sync_schemas():
                print(line)
        elif args.target == "prompts":
            result = write_monolith(check_only=not args.write)
            print(json.dumps(result, indent=2))
        else:
            print(json.dumps(build_all(), indent=2))
        return 0

    if args.command == "validate":
        if args.validate_cmd == "report":
            sem = validate_report_file(args.path, semantic=not args.no_semantic)
            if not sem.ok:
                for issue in sem.issues:
                    loc = f" ({issue.path})" if issue.path else ""
                    print(f"{issue.code}{loc}: {issue.message}")
                return 1
            print(f"OK: {args.path}")
            return 0
        if args.validate_cmd == "graph":
            sem = validate_graph_file(args.path, semantic=not args.no_semantic)
            if not sem.ok:
                for issue in sem.issues:
                    loc = f" ({issue.path})" if issue.path else ""
                    print(f"{issue.code}{loc}: {issue.message}")
                return 1
            print(f"OK: {args.path}")
            return 0

    if args.command == "graph" and args.graph_cmd == "paths":
        found = analyze_graph_paths(args.path)
        print(json.dumps([p.__dict__ for p in found], indent=2))
        return 0

    if args.command == "inventory":
        result = collect_inventory(args.path)
        payload = inventory_to_json(result)
        text = json.dumps(payload, indent=2)
        if args.output:
            args.output.write_text(text + "\n", encoding="utf-8")
            print(f"Wrote {args.output}")
        else:
            print(text)
        return 0

    if args.command == "preflight":
        payload = run_preflight(args.path, output_dir=args.output_dir)
        print(payload["summary"])
        return 0

    if args.command == "verify" and args.verify_cmd == "digest":
        if args.expected:
            ok, actual = verify_file_digest(args.path, args.expected)
            print(json.dumps({"ok": ok, "sha256": actual}, indent=2))
            return 0 if ok else 1
        print(json.dumps({"sha256": sha256_file(args.path)}, indent=2))
        return 0

    if args.command == "verify" and args.verify_cmd == "manifest":
        payload = build_digest_manifest(args.path)
        text = json.dumps(payload, indent=2)
        if args.output:
            args.output.write_text(text + "\n", encoding="utf-8")
            print(f"Wrote {args.output}")
        else:
            print(text)
        return 0

    if args.command == "diff":
        if args.diff_kind == "report":
            base = json.loads(args.base.read_text(encoding="utf-8"))
            target = json.loads(args.target.read_text(encoding="utf-8"))
            print(json.dumps(diff_reports(base, target), indent=2))
            return 0
        if args.diff_kind == "graph":
            base = json.loads(args.base.read_text(encoding="utf-8"))
            target = json.loads(args.target.read_text(encoding="utf-8"))
            print(json.dumps(diff_graphs(base, target), indent=2))
            return 0

    if args.command == "export" and args.export_cmd == "sarif":
        report = json.loads(args.report.read_text(encoding="utf-8"))
        sarif_doc = report_to_sarif(report)
        text = json.dumps(sarif_doc, indent=2)
        if args.output:
            args.output.write_text(text + "\n", encoding="utf-8")
            print(f"Wrote {args.output} ({len(sarif_doc['runs'][0]['results'])} results)")
        else:
            print(text)
        return 0

    if args.command == "corpus":
        summary = run_corpus()
        print(json.dumps(summary, indent=2))
        return 0 if summary.get("failed", 0) == 0 else 1

    return 2
