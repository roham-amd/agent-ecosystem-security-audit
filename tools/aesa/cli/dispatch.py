"""Command handlers — one cohesive module, low coupling to argparse construction."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, cast

from aesa.audit import ProfileName, run_audit
from aesa.audit_diff import diff_graphs, diff_reports
from aesa.benchmark.governance import verify_dataset_integrity
from aesa.benchmark.intake import (
    build_submitter_package,
    collection_status,
    intake_submission_dir,
    list_external_intakes,
    verify_evaluation_contract,
)
from aesa.benchmark.llm_runner import _load_dataset_manifest, run_llm_benchmark
from aesa.benchmark.report import build_evaluation_report
from aesa.benchmark.runner import run_benchmark
from aesa.build import build_all, sync_schemas
from aesa.corpus.runner import run_corpus
from aesa.deps import outdated_report, upgrade_pins
from aesa.export.annotate import render_github_annotations, render_text_annotations
from aesa.export.sarif import report_to_sarif
from aesa.hosts.profiles import get_host_profile, list_host_profiles
from aesa.inventory.collector import collect_inventory, inventory_to_json
from aesa.jsonio import print_json, read_json, write_json
from aesa.lint import run_ruff
from aesa.pilots.runner import load_manifest, run_pilots
from aesa.policy import apply_policy_defaults, discover_policy_file, load_policy
from aesa.prompt_build import write_monolith
from aesa.rules_quality.runner import run_rule_quality
from aesa.security.baseline import (
    baseline_path,
    diff_against_baseline,
    load_baseline,
    save_baseline,
)
from aesa.security.engine import ScanResult, run_security_scan
from aesa.security.report import render_finding_explanation
from aesa.security.scan import run_scan
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
        case "scan":
            return _cmd_scan(args)
        case "explain":
            return _cmd_explain(args)
        case "baseline":
            return _cmd_baseline(args)
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
        case "annotate":
            return _cmd_annotate(args)
        case "pilots":
            return _cmd_pilots(args)
        case "hosts":
            return _cmd_hosts(args)
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


def _cmd_scan(args: argparse.Namespace) -> int:
    policy = None
    if not getattr(args, "no_policy", False):
        policy_path = getattr(args, "policy", None) or discover_policy_file(args.path)
        if policy_path is not None:
            policy = load_policy(policy_path)

    fail_on = apply_policy_defaults(
        policy=policy,
        fail_on=args.fail_on,
        fail_on_from_cli=args.fail_on is not None,
    )
    output_dir = args.output_dir
    if output_dir is None and policy is not None and policy.output_dir is not None:
        output_dir = policy.output_dir
    baseline = args.baseline
    if baseline is None and policy is not None and policy.baseline is not None:
        baseline = policy.baseline

    _scan, payload, code = run_scan(
        args.path,
        output_dir=output_dir,
        baseline=baseline,
        save_baseline_path=args.save_baseline,
        fail_on=fail_on,
        policy=policy,
    )
    print(payload["summary"])
    if payload.get("risk_delta"):
        print_json({"risk_delta": payload["risk_delta"]})
    if payload.get("baseline_saved"):
        print(f"Baseline saved: {payload['baseline_saved']}")
    if payload.get("policy_path"):
        print(f"Policy: {payload['policy_path']}")
    if payload.get("suppressions"):
        print(f"Suppressions applied: {len(payload['suppressions'])}")
    print(f"Artifacts: {payload['output_dir']}")
    return code


def _cmd_explain(args: argparse.Namespace) -> int:
    findings_path = args.output_dir / "findings.json"
    if not findings_path.is_file():
        print(f"Missing findings.json at {findings_path}. Run `aesa scan` first.")
        return 1
    doc = read_json(findings_path)
    scan = ScanResult.from_findings_doc(doc)
    finding = scan.finding_by_id(args.finding_id)
    if finding is None:
        print(f"Finding {args.finding_id} not found in {findings_path}")
        return 1
    print(render_finding_explanation(scan, finding))
    return 0


def _cmd_baseline(args: argparse.Namespace) -> int:
    match args.baseline_cmd:
        case "save":
            findings_path = args.output_dir / "findings.json"
            if not findings_path.is_file():
                print(f"Missing {findings_path}; run `aesa scan` first.")
                return 1
            doc = read_json(findings_path)
            # Prefer re-scan of the recorded repository so fingerprints stay current.
            repo = Path(str(doc.get("repository") or ""))
            scan = run_security_scan(repo) if repo.is_dir() else ScanResult.from_findings_doc(doc)
            dest = args.path or baseline_path(args.output_dir)
            saved = save_baseline(scan, dest)
            print(
                f"Wrote baseline with {len(saved.get('finding_keys') or [])} finding keys: {dest}"
            )
            return 0
        case "show":
            if not args.path.is_file():
                print(f"Baseline not found: {args.path}")
                return 1
            print_json(load_baseline(args.path))
            return 0
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


def _validate_claim(path: Path) -> tuple[bool, list[Any]]:
    from dataclasses import dataclass

    @dataclass
    class Issue:
        code: str
        message: str
        path: str = ""

    doc = read_json(path)
    issues: list[Issue] = []
    required = ("claim", "status", "evidence_ids")
    for key in required:
        if key not in doc:
            issues.append(Issue("CLAIM_MISSING_FIELD", f"Missing required field `{key}`"))
    status = doc.get("status")
    allowed = {
        "OBSERVED",
        "CONFIRMED",
        "POTENTIAL",
        "NOT VERIFIED",
        "NOT ASSESSED",
        "NOT APPLICABLE",
    }
    if status is not None and status not in allowed:
        issues.append(Issue("CLAIM_BAD_STATUS", f"Invalid status {status!r}"))
    evidence_ids = doc.get("evidence_ids")
    if evidence_ids is not None and not isinstance(evidence_ids, list):
        issues.append(Issue("CLAIM_BAD_EVIDENCE", "evidence_ids must be a list"))
    if status == "CONFIRMED" and (not evidence_ids):
        issues.append(
            Issue(
                "CLAIM_UNSUPPORTED_CONFIRMED",
                "CONFIRMED claims require non-empty evidence_ids",
            )
        )
    return (len(issues) == 0, issues)


def _cmd_validate(args: argparse.Namespace) -> int:
    semantic = not getattr(args, "no_semantic", False)
    match args.validate_cmd:
        case "report":
            report_result = validate_report_file(args.path, semantic=semantic)
            return _print_validation(args.path, ok=report_result.ok, issues=report_result.issues)
        case "graph":
            graph_result = validate_graph_file(args.path, semantic=semantic)
            return _print_validation(args.path, ok=graph_result.ok, issues=graph_result.issues)
        case "claim":
            ok, issues = _validate_claim(args.path)
            return _print_validation(args.path, ok=ok, issues=issues)
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
    match args.diff_kind:
        case "report":
            print_json(diff_reports(read_json(args.base), read_json(args.target)))
            return 0
        case "graph":
            print_json(diff_graphs(read_json(args.base), read_json(args.target)))
            return 0
        case "risk":
            findings = read_json(args.findings)
            repo = findings.get("repository")
            if repo and Path(repo).is_dir():
                scan = run_security_scan(Path(repo))
            else:
                scan = ScanResult.from_findings_doc(findings)
            print_json(diff_against_baseline(scan, load_baseline(args.baseline)))
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


def _cmd_annotate(args: argparse.Namespace) -> int:
    if not args.findings.is_file():
        print(f"Findings not found: {args.findings}")
        return 1
    doc = read_json(args.findings)
    if args.annotate_format == "text":
        text = render_text_annotations(doc)
    else:
        text = render_github_annotations(doc)
    if text:
        print(text, end="" if text.endswith("\n") else "\n")
    else:
        print("No SECURITY_FINDING/EXPOSURE annotations.")
    return 0


def _cmd_pilots(args: argparse.Namespace) -> int:
    match args.pilots_cmd:
        case "list":
            manifest = load_manifest(args.manifest)
            print_json(
                {
                    "pilots": [
                        {
                            "id": p.get("id"),
                            "path": p.get("path"),
                            "kind": p.get("kind"),
                            "enabled": p.get("enabled", True),
                            "notes": p.get("notes"),
                        }
                        for p in manifest.get("pilots") or []
                    ]
                }
            )
            return 0
        case "run":
            report = run_pilots(
                manifest_path=args.manifest,
                output_dir=args.output_dir,
                only=args.only,
            )
            print_json(
                {
                    "ok_count": report["ok_count"],
                    "pilot_count": report["pilot_count"],
                    "summary": report.get("summary_md"),
                    "results": [
                        {
                            "id": r.get("id"),
                            "status": r.get("status"),
                            "finding_count": r.get("finding_count"),
                            "component_count": r.get("component_count"),
                        }
                        for r in report["results"]
                    ],
                }
            )
            hard_fail = {"missing", "error"}
            return 1 if any(r.get("status") in hard_fail for r in report["results"]) else 0
        case _:
            return 2


def _cmd_hosts(args: argparse.Namespace) -> int:
    match args.hosts_cmd:
        case "list":
            print_json({"hosts": list_host_profiles()})
            return 0
        case "show":
            profile = get_host_profile(args.host_id)
            if profile is None:
                print(f"Unknown host profile: {args.host_id}")
                print("Known:", ", ".join(sorted(p["host_id"] for p in list_host_profiles())))
                return 1
            print_json(profile.to_dict())
            return 0
        case _:
            return 2


def _cmd_corpus() -> int:
    summary = run_corpus()
    print_json(summary)
    return 0 if summary.get("failed", 0) == 0 else 1


def _cmd_benchmark(args: argparse.Namespace) -> int:
    match args.benchmark_cmd:
        case "run":
            summary = run_benchmark()
        case "rules":
            summary = run_rule_quality()
        case "governance":
            summary = verify_dataset_integrity(_load_dataset_manifest())
            print_json(summary)
            return 0 if summary.get("ok") else 1
        case "contract":
            if getattr(args, "contract_cmd", None) != "verify":
                return 2
            summary = verify_evaluation_contract()
            print_json(summary)
            return 0 if summary.get("ok") else 1
        case "intake":
            summary = intake_submission_dir(
                args.source,
                agent_id=args.agent_id,
                provenance=args.provenance,
                dry_run=bool(getattr(args, "dry_run", False)),
            )
            print_json(summary)
            return 0 if summary.get("ok") else 1
        case "intakes":
            summary = list_external_intakes()
            print_json(summary)
            return 0
        case "collection-status":
            summary = collection_status()
            print_json(summary)
            return 0
        case "submitter-package":
            summary = build_submitter_package(args.output)
            print_json(summary)
            return 0 if summary.get("ok") else 1
        case "llm":
            if getattr(args, "report", False):
                if not getattr(args, "submissions", None):
                    print("--report requires --submissions DIR")
                    return 2
                summary = build_evaluation_report(
                    submissions=args.submissions,
                    split=getattr(args, "split", "all"),
                    provenance=getattr(args, "provenance", "any"),
                )
                print_json(summary)
                return 0 if summary.get("dataset_integrity", {}).get("ok") else 1
            summary = run_llm_benchmark(
                submissions=getattr(args, "submissions", None),
                validate_only=bool(getattr(args, "validate_only", False)),
                split=getattr(args, "split", "all"),
            )
        case _:
            return 2
    print_json(summary)
    # governance-style integrity failures are embedded for llm validate
    if summary.get("dataset_integrity") and not summary["dataset_integrity"].get("ok"):
        return 1
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
