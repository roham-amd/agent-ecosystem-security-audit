# Contributing to authdiff

Thanks for helping improve **authdiff** (product line formerly branded AESA Guard).

Product contract: [`docs/PRODUCT.md`](docs/PRODUCT.md) · Docs index:
[`docs/DOCUMENTATION-INDEX.md`](docs/DOCUMENTATION-INDEX.md).

## Development setup

```bash
cd tools
uv sync --locked
uv run authdiff-dev lint --check-format
uv run mypy aesa
uv run pytest -q ../tests
uv run authdiff-dev build all
uv run pip-audit
```

CI mirrors this in [`.github/workflows/aesa-validate.yml`](.github/workflows/aesa-validate.yml)
(plus corpus harness and wheel smoke).

## Conventions

- Python: declare constraints in [`tools/pyproject.toml`](tools/pyproject.toml) via `uv add` / `uv add --dev`; lock exact versions + hashes in [`tools/uv.lock`](tools/uv.lock); interpreter minor in [`tools/.python-version`](tools/.python-version) (`3.12`). Commit all three; ignore `.venv/`.
- Docker: [`Dockerfile`](Dockerfile) pins `python:3.12.16-slim-trixie@sha256:…` + `ghcr.io/astral-sh/uv:…@sha256:…`; `uv sync --locked --no-dev`.
- Actions: full commit SHAs with version comments; CI uses `uv python install 3.12.16` + `uv sync --locked` + `uv run --locked …`.
- Product CLI name is **`authdiff`**; keep **`aesa`** as a console-script alias. Maintainer commands live on **`authdiff-dev`**.
- Methodology kit lives under [`archive/methodology/`](archive/methodology/) — do not resurrect root `prompts/` / `modules/` trees. Root [`kit/`](kit/) is a stub only.
- Passive scans must remain read-only. Opt-in execute paths (`run`, `snapshot --execute`) scrub env only and must document sandbox limits.
- Lock I/O lives in `aesa.lock_io`; lock build/diff in `aesa.authority_lock`. Do not pull the scanner into the broker path.

## Pull requests

- Prefer small, reviewable PRs.
- Update `CHANGELOG.md` for user-visible changes.
- Keep `VERSION`, `canonical/versions.json`, `tools/pyproject.toml`, `tools/aesa/__init__.py`, and release/skill pins aligned when cutting a release.
