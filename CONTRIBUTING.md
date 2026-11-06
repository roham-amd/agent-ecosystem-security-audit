# Contributing to authdiff

Thanks for helping improve **authdiff** (product line formerly branded AESA Guard).

## Development setup

```bash
cd tools
uv sync --locked
uv run authdiff lint --check-format
uv run mypy aesa
uv run pytest -q ../tests
uv run authdiff build all
```

## Conventions

- Python: declare constraints in [`tools/pyproject.toml`](tools/pyproject.toml) via `uv add` / `uv add --dev`; lock exact versions + hashes in [`tools/uv.lock`](tools/uv.lock); interpreter minor in [`tools/.python-version`](tools/.python-version) (`3.12`). Commit all three; ignore `.venv/`.
- Docker: [`Dockerfile`](Dockerfile) pins `python:3.12.16-slim-trixie@sha256:…` + `ghcr.io/astral-sh/uv:…@sha256:…`; `uv sync --locked --no-dev`.
- Actions: full commit SHAs with version comments; CI uses `uv python install 3.12.16` + `uv sync --locked` + `uv run --locked …`.
- Product CLI name is **`authdiff`**; keep **`aesa`** as a console-script alias.
- Methodology kit lives under [`archive/methodology/`](archive/methodology/) — do not resurrect root `prompts/` / `modules/` trees.
- Passive scans must remain read-only. Opt-in execute paths (`run`, `snapshot --execute`) scrub env only and must document sandbox limits.

## Pull requests

- Prefer small, reviewable PRs.
- Update `CHANGELOG.md` for user-visible changes.
- Keep `VERSION`, `canonical/versions.json`, `tools/pyproject.toml`, and `tools/aesa/__init__.py` aligned when cutting a release.
