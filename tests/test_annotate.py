from pathlib import Path

from aesa.export.annotate import render_github_annotations, render_text_annotations
from aesa.jsonio import read_json


def test_github_annotations_from_sample_findings():
    path = Path(__file__).resolve().parents[1] / "examples" / "guard-scan" / "findings.json"
    doc = read_json(path)
    text = render_github_annotations(doc)
    assert "::error" in text or "::warning" in text
    assert "file=" in text
    assert "F-" in text


def test_text_annotations_non_empty():
    path = Path(__file__).resolve().parents[1] / "examples" / "guard-scan" / "findings.json"
    doc = read_json(path)
    text = render_text_annotations(doc)
    assert "SECURITY_FINDING" in text or "EXPOSURE" in text
