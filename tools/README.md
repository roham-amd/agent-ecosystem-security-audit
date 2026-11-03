# AESA tooling

Deterministic build, unified audit profiles, report validation, passive inventory, corpus, and benchmark harness.

## Install (local)

Preferred (constraints prevent resolver drift / collisions):

```bash
cd tools
python -m pip install -c constraints.txt -e ".[dev]"
python -m pip check
```

Equivalent lock install:

```bash
python -m pip install -r requirements.lock.txt
python -m pip install -e .
python -m pip check
```

Requires **Python >= 3.15**.

Pin source of truth: [`constraints.txt`](constraints.txt) (latest compatible set, 2026-11-03).
`pyproject.toml`, [`requirements.txt`](requirements.txt), and [`requirements.lock.txt`](requirements.lock.txt)
must match it — enforced by `aesa build all`.

### Dependency updates (like `ncu` / `ncu -u`)

```bash
aesa deps outdated          # compare pins to latest PyPI (exit 1 if any outdated)
aesa deps upgrade --dry-run # show bumps
aesa deps upgrade           # rewrite constraints + lock + pyproject pins
python -m pip install -c constraints.txt -e ".[dev]"
python -m pip check
```

**Dependabot** (`.github/dependabot.yml`) opens weekly grouped PRs for `pip` (`/tools`) and `github-actions`.
Pin source of truth stays `constraints.txt` — after merging a Dependabot bump that touches
`pyproject.toml` / requirements, re-run `aesa deps upgrade` (or align pins by hand) so
constraints, lock, and `pyproject.toml` match; `aesa build all` enforces that.

## Commands

```bash
aesa audit PATH --profile quick|standard|deployment
aesa preflight PATH     # alias of audit --profile quick
aesa build all          # sync schemas, check versions, validate examples
aesa validate report PATH.json
aesa inventory PATH     # JSON-only passive discovery
aesa diff report A B
aesa export sarif REPORT.json
aesa corpus run         # tooling corpus harness
aesa benchmark run      # detection benchmark scaffold (no LLM)
aesa deps outdated|upgrade
aesa lint                 # Ruff check
aesa lint --fix --format # autofix + format
aesa lint --check-format  # CI: fail on format drift
```

## Code layout (tools/aesa)

| Module | Responsibility |
| --- | --- |
| `cli/` | argparse + command dispatch (SRP) |
| `inventory/` | bounded I/O, adapter registry, collector |
| `audit.py` / `preflight.py` | assessment orchestration + graph seed |
| `deps.py` / `pins.py` | pin check/upgrade (ncu-style) |
| `jsonio.py` | shared JSON/text writers |

Style: Python **3.15+**, Ruff (`pyproject.toml` `[tool.ruff]`), typed public surfaces, adapters registered in `inventory/adapters/registry.py`.

Resource limits for collectors: `max_files`, `max_depth`, `max_file_bytes` (see `aesa.inventory.limits`).

See [`docs/AESA-3.0-PRODUCT-SPEC.md`](../docs/AESA-3.0-PRODUCT-SPEC.md) and [`docs/AESA-GATE.md`](../docs/AESA-GATE.md).
