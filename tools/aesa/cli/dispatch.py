"""Command handlers — one cohesive module, low coupling to argparse construction."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, cast

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
from aesa.security.baseline import (
    baseline_path,
    diff_against_baseline,
    load_baseline,
    save_baseline,
)
from aesa.security.engine import ScanResult, run_security_scan
from aesa.security.models import Finding
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
    fail_on = None if args.fail_on == "never" else args.fail_on
    _scan, payload, code = run_scan(
        args.path,
        output_dir=args.output_dir,
        baseline=args.baseline,
        save_baseline_path=args.save_baseline,
        fail_on=fail_on,
    )
    print(payload["summary"])
    if payload.get("risk_delta"):
        print_json({"risk_delta": payload["risk_delta"]})
    if payload.get("baseline_saved"):
        print(f"Baseline saved: {payload['baseline_saved']}")
    print(f"Artifacts: {payload['output_dir']}")
    return code


def _scan_from_findings_doc(doc: dict[str, Any]) -> ScanResult:
    """Rebuild a minimal ScanResult for explain from findings.json."""
    findings = [
        Finding(
            finding_id=str(f.get("finding_id") or ""),
            rule_id=str(f.get("rule_id") or ""),
            title=str(f.get("title") or ""),
            severity=f.get("severity") or "INFORMATIONAL",  # type: ignore[arg-type]
            confidence=f.get("confidence") or "POTENTIAL",  # type: ignore[arg-type]
            description=str(f.get("description") or ""),
            component_ids=list(f.get("component_ids") or []),
            evidence_ids=list(f.get("evidence_ids") or []),
            capabilities=list(f.get("capabilities") or []),
            attacker_control=str(f.get("attacker_control") or ""),
            entry_point=str(f.get("entry_point") or ""),
            trust_boundary=str(f.get("trust_boundary") or ""),
            impact=str(f.get("impact") or ""),
            missing_controls=list(f.get("missing_controls") or []),
            recommended_action=str(f.get("recommended_action") or ""),
            exploitability=str(f.get("exploitability") or "UNKNOWN"),
            exposure=str(f.get("exposure") or "UNKNOWN"),
        )
        for f in doc.get("findings") or []
    ]
    from aesa.security.models import Evidence

    evidences = [
        Evidence(
            evidence_id=str(e.get("evidence_id") or ""),
            component_id=e.get("component_id"),
            evidence_class=e.get("evidence_class") or "SOURCE_STATIC",  # type: ignore[arg-type]
            verification_status=e.get("verification_status") or "OBSERVED",  # type: ignore[arg-type]
            file_path=e.get("file_path"),
            line_start=e.get("line_start"),
            line_end=e.get("line_end"),
            content_digest=e.get("content_digest"),
            collection_method=str(e.get("collection_method") or "deterministic_rule"),
            source_commit=e.get("source_commit"),
            observed_at=e.get("observed_at"),
            limitations=list(e.get("limitations") or []),
            summary=str(e.get("summary") or ""),
        )
        for e in doc.get("evidence_registry") or []
    ]
    return ScanResult(
        repository_path=str(doc.get("repository") or ""),
        commit=doc.get("audited_commit"),
        collected_at_utc=str(doc.get("collected_at_utc") or ""),
        inventory={"components": []},
        graph={},
        capabilities=[],
        evidences=evidences,
        findings=findings,
        coverage=doc.get("coverage") or {},
        authority_bearing_count=int(
            (doc.get("summary") or {}).get("authority_bearing_components") or 0
        ),
        external_destination_count=int(
            (doc.get("summary") or {}).get("external_data_destinations") or 0
        ),
        product_version=str(doc.get("product_version") or ""),
        package_version=str(doc.get("package_version") or ""),
        rules_applied=list(doc.get("rules_applied") or []),
    )


def _cmd_explain(args: argparse.Namespace) -> int:
    findings_path = args.output_dir / "findings.json"
    if not findings_path.is_file():
        print(f"Missing findings.json at {findings_path}. Run `aesa scan` first.")
        return 1
    doc = read_json(findings_path)
    scan = _scan_from_findings_doc(doc)
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
            scan = run_security_scan(Path(doc.get("repository") or args.output_dir.parent))
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
            scan = _scan_from_findings_doc(findings)
            # Prefer re-scan if repository path exists for richer component keys.
            repo = findings.get("repository")
            if repo and Path(repo).is_dir():
                scan = run_security_scan(Path(repo))
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
