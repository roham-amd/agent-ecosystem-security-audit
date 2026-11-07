# Install authdiff

## Requirements

- Python **3.12+** (uv can fetch a managed interpreter)
- Git (for `authdiff open` / `vet` of remote URLs)
- Optional: Docker for the digest-pinned image

## Canonical install (one command)

Prefer this path. It is the only install we treat as documented for new users.

```bash
uvx --from "git+https://github.com/roham-amd/agent-ecosystem-security-audit.git@v3.8.0#subdirectory=tools" authdiff
```

Persistent tool install:

```bash
uv tool install --python 3.12 \
  "git+https://github.com/roham-amd/agent-ecosystem-security-audit.git@v3.8.0#subdirectory=tools"

authdiff --help
authdiff doctor
authdiff lock
```

### PyPI (when published)

```bash
pip install aesa-tools==0.11.0
# or: uv pip install aesa-tools==0.11.0
```

Package name remains **`aesa-tools`** (AESA-era package id). CLI names:
**`authdiff`** (primary) and **`aesa`** (compatibility alias).
Maintainer commands: **`authdiff-dev`**.

Until the package is published to PyPI, use the git-tag `uvx` / `uv tool install`
path above. Do not treat an undocumented registry URL as canonical.

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

See [`AESA-GATE.md`](AESA-GATE.md) and `authdiff ci init` (writes an advisory workflow stub).
Consumer recipe: [`aesa-consumer-gate.example.yml`](aesa-consumer-gate.example.yml).

## Version alignment

| Surface | Version |
| --- | --- |
| Product (`VERSION`) | 3.8.0 |
| Package `aesa-tools` | 0.11.0 |
| `AUTHORITY.lock` schema | 2 |
| Rule pack | 1.4 |
