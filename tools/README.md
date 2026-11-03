# AESA Gate tooling

Deterministic build, report validation, passive inventory/preflight, and corpus evaluation.

## Install (local)

```bash
cd tools
python -m pip install -e ".[dev]"
```

## Commands

```bash
aesa preflight PATH     # discovery + coverage + audit-context (writes aesa-out/)
aesa build all          # sync schemas, check versions, validate examples
aesa validate report PATH.json
aesa inventory PATH     # passive read-only discovery JSON
aesa diff report A B
aesa export sarif REPORT.json
aesa corpus run         # tooling corpus harness (not LLM detection benchmark)
```

Resource limits for collectors: `max_files`, `max_depth`, `max_file_bytes` (see `aesa.inventory.limits`).

See [`docs/AESA-GATE.md`](../docs/AESA-GATE.md) and [`docs/MIGRATION-2.0.md`](../docs/MIGRATION-2.0.md).
