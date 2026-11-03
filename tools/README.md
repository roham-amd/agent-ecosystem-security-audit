# AESA tooling

Deterministic build, report validation, passive inventory, and corpus evaluation (assessment R-001, R-002, R-003, R-005).

## Install (local)

```bash
cd tools
python -m pip install -e ".[dev]"
```

## Commands

```bash
aesa build all          # sync schemas, check versions, validate examples
aesa validate report PATH.json
aesa inventory PATH     # passive read-only discovery
aesa corpus run         # run corpus harness (fixtures + validators)
```

See [`docs/MIGRATION-2.0.md`](../docs/MIGRATION-2.0.md) for upgrade notes.
