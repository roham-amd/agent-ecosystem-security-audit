# Install AESA Guard

## Recommended: `uv tool install` from Git

Until the PyPI release finishes Trusted Publisher setup, install the CLI as a
user tool from this repository’s `tools/` package:

```bash
uv tool install git+https://github.com/roham-amd/agent-ecosystem-security-audit.git@main#subdirectory=tools

aesa doctor
aesa vet github.com/org/some-skill
aesa scan /path/to/target-repo
```

Pin a release tag when you need reproducibility:

```bash
uv tool install "git+https://github.com/roham-amd/agent-ecosystem-security-audit.git@v3.5.1#subdirectory=tools"
```

(If `v3.5.1` is not published yet, pin a commit SHA or use `@main` knowingly.)

Upgrade:

```bash
uv tool upgrade aesa-tools
```

## PyPI (when published)

```bash
uv tool install aesa-tools
# or: pipx install aesa-tools
aesa doctor
```

Publishing workflow: [`.github/workflows/publish-pypi.yml`](../.github/workflows/publish-pypi.yml)
(OIDC trusted publishing on tagged releases). Requires the PyPI project
`aesa-tools` with GitHub as a trusted publisher.

## From a local clone (development)

```bash
cd tools
uv sync --locked
uv run aesa doctor
uv run aesa scan /path/to/target-repo
# optional: uv tool install . --force
```

## Requirements

- Python **3.15+**
- [uv](https://docs.astral.sh/uv/)
- `git` on PATH for `aesa vet` remote sources

Artifacts default to `./aesa-out` in the current working directory.
