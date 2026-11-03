# AESA tooling

Deterministic build, unified audit profiles, report validation, passive inventory, corpus, and benchmark harness.

## Stack (Python 3.15)

| Responsibility | Choice |
| --- | --- |
| Runtime | CPython 3.15 (`.python-version` = `3.15`; CI/Docker pin patch `3.15.2`) |
| Project / venv / lock | **uv** + `pyproject.toml` + `uv.lock` |
| Dev deps | PEP 735 `[dependency-groups]` |
| Lint / format | Ruff |
| Types | mypy |
| Tests | Pytest (+ pytest-cov) |
| Vuln scan | pip-audit |
| CI | GitHub Actions + `uv sync --locked` |
| Deploy | Docker (`uv sync --locked --no-dev`) |

Do **not** add Poetry, pip-tools, Pipenv, or a separate venv manager.

## Install (local)

```bash
# https://docs.astral.sh/uv/getting-started/installation/
cd tools
uv sync --locked          # creates .venv from uv.lock
uv run aesa --help
```

`.python-version` selects the **minor** interpreter (`3.15`). Patch pins belong in CI (`uv python install 3.15.2`) and the Docker base image.

### Dependency layout

| Requirement | Location / command |
| --- | --- |
| Runtime deps | `pyproject.toml` `[project].dependencies` (constraints via `uv add`) |
| Dev deps | `pyproject.toml` `[dependency-groups] dev` (`uv add --dev …`) |
| Exact versions + hashes | `uv.lock` (commit it) |
| Install | `uv sync --locked` |
| Updates | `uv add` / `uv lock --upgrade` / `aesa deps upgrade` |
| Git | Commit `pyproject.toml`, `uv.lock`, `.python-version` — ignore `.venv/` |

```bash
uv add jsonschema              # runtime constraint + lock
uv add --dev ruff              # PEP 735 group
uv lock --upgrade              # refresh lock
uv lock --upgrade-package ruff # one package
uv sync --locked
uv tree
aesa deps outdated             # compare lock → PyPI
```

### Docker

Root [`Dockerfile`](../Dockerfile) uses `python:3.15.2-slim-trixie@sha256:…` and pinned `ghcr.io/astral-sh/uv:…@sha256:…`, then `uv sync --locked --no-dev`.

```bash
docker compose build
TARGET=/path/to/repo docker compose run --rm aesa \
  audit /work --profile standard -o /work/aesa-out
```

Operator guide for Docker discovery + Cursor / Claude Code / Codex / Antigravity deep review:
[`docs/docker-agent-audit.md`](../docs/docker-agent-audit.md).

### Pre-commit (optional)

```bash
uvx pre-commit install
uvx pre-commit run --all-files
```

Config: [`.pre-commit-config.yaml`](../.pre-commit-config.yaml) (Ruff lint + format). Kept out of the `dev` group so Windows hosts are not forced to build PyYAML.

### Quality gates

```bash
uv run --locked aesa lint --check-format
uv run --locked mypy aesa
uv run --locked pip-audit
uv run --locked pytest -q ../tests
uv run --locked aesa build all
```

**Dependabot** (`.github/dependabot.yml`): weekly `uv`, `docker` (tag@digest), and SHA-pinned `github-actions`.

## Commands

```bash
uv run aesa audit PATH --profile quick|standard|deployment
uv run aesa preflight PATH
uv run aesa build all
uv run aesa validate report PATH.json
uv run aesa inventory PATH
uv run aesa diff report A B
uv run aesa export sarif REPORT.json
uv run aesa corpus run
uv run aesa benchmark run
uv run aesa deps outdated|upgrade
uv run aesa lint [--fix] [--format] [--check-format]
```

## Code layout (tools/aesa)

| Module | Responsibility |
| --- | --- |
| `cli/` | argparse + command dispatch |
| `inventory/` | bounded I/O, adapter registry, collector |
| `audit.py` / `preflight.py` | assessment orchestration + graph seed |
| `deps.py` / `pins.py` | uv.lock check/upgrade helpers |
| `jsonio.py` | shared JSON/text writers |

See [`docs/AESA-3.0-PRODUCT-SPEC.md`](../docs/AESA-3.0-PRODUCT-SPEC.md) and [`docs/AESA-GATE.md`](../docs/AESA-GATE.md).
