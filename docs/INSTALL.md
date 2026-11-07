# Install authdiff

## Requirements

- Python **3.12+** (uv can fetch a managed interpreter)
- Git (for `authdiff open` / `vet` of remote URLs)
- Optional: Docker for the digest-pinned image

## Recommended: uv tool

```bash
uv tool install --python 3.12 \
  "git+https://github.com/roham-amd/agent-ecosystem-security-audit.git@v3.7.0#subdirectory=tools"

# Prefer PyPI when published:
#   pip install aesa-tools==0.10.0

authdiff --help
authdiff doctor
authdiff lock
```

The `aesa` console script remains a compatibility alias.
Maintainer commands (`build`, `lint`, `corpus`, …): `authdiff-dev`.

## From a checkout

```bash
cd tools
uv sync --locked
uv run authdiff scan ../examples/demo-vulnerable
```

## Docker

```bash
docker compose build
TARGET=/path/to/repo docker compose run --rm authdiff scan /work -o /tmp/authdiff-out
```

Image base: `python:3.12.16-slim-trixie` (digest-pinned in `Dockerfile`).

## GitHub Action

See [`AESA-GATE.md`](AESA-GATE.md) and `authdiff init` (writes an advisory workflow stub).

## PyPI

Trusted-publishing workflow: [`.github/workflows/publish-pypi.yml`](../.github/workflows/publish-pypi.yml).
Package name: `aesa-tools` (CLI: `authdiff` / `aesa`).
