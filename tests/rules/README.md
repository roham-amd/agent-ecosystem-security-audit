# Guard rule-quality pack

Positive, negative, and ambiguous fixtures for every deterministic security rule
in pack **1.2** (`AESA-RULE-001` … `AESA-RULE-016`).

```bash
cd tools && uv run aesa benchmark rules
# or
cd tools && uv run pytest ../tests/test_rule_quality.py -q
```

Separate from:

- `aesa benchmark run` — AgentSecBench inventory/rule smoke cases
- `aesa benchmark llm` — model-agnostic AI submission scoring
- `tests/corpus` — tooling regression corpus
- `tests/test_rules_011_016.py` — focused unit coverage for pack 1.2 additions
