from pathlib import Path

from aesa.corpus.runner import run_corpus
from aesa.inventory.collector import collect_inventory
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
