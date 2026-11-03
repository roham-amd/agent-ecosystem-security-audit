from pathlib import Path

from aesa.corpus.runner import run_corpus
from aesa.inventory.collector import collect_inventory, inventory_to_json
from aesa.inventory.limits import CollectorLimits
from aesa.preflight import run_preflight
from aesa.validate_report import analyze_graph_paths


def test_corpus_harness_passes():
    summary = run_corpus()
    assert summary["failed"] == 0, summary


def test_attack_path_search():
    graph = (
        Path(__file__).resolve().parents[1]
        / "tests"
        / "validation"
        / "positive"
        / "attack-path-graph.json"
    )
    paths = analyze_graph_paths(graph)
    assert len(paths) >= 1


def test_inventory_finds_skill_and_mcp():
    root = Path(__file__).resolve().parents[1] / "tests" / "corpus" / "fixtures" / "benign-skill-mcp"
    inv = collect_inventory(root)
    names = {c["name"] for c in inv.components}
    assert "benign-readonly-helper" in names
    assert "filesystem-readonly" in names
    payload = inventory_to_json(inv)
    assert "coverage" in payload
    assert "adapter_matrix" in payload["coverage"]


def test_preflight_writes_outputs(tmp_path: Path):
    root = Path(__file__).resolve().parents[1] / "tests" / "corpus" / "fixtures" / "benign-skill-mcp"
    out = tmp_path / "aesa-out"
    result = run_preflight(root, output_dir=out)
    assert result["component_count"] >= 2
    assert (out / "inventory.json").is_file()
    assert (out / "ecosystem-graph.json").is_file()
    assert (out / "audit-context.md").is_file()
    assert "NOT VERIFIED" in result["summary"]


def test_inventory_skips_oversize_before_read(tmp_path: Path):
    huge = tmp_path / "SKILL.md"
    huge.write_bytes(b"x" * 5000)
    inv = collect_inventory(tmp_path, limits=CollectorLimits(max_file_bytes=100))
    assert inv.components == []
    assert any(e.get("type") == "parse_skipped_size" for e in inv.parser_events)
