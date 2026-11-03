# Contributing to AESA Guard

Thank you for helping improve the Agent Ecosystem Security Assessment framework
(AESA Guard).

**Docs map:** [`docs/DOCUMENTATION-INDEX.md`](docs/DOCUMENTATION-INDEX.md)

## Ways to contribute

- Clarify audit procedure language without weakening evidence gates
- Improve specialized modules (`modules/`) — update `modules/README.md` and skill tables
- Extend Guard rules (`tools/aesa/security/rules.py`) — update [`docs/SECURITY-RULES.md`](docs/SECURITY-RULES.md) and AgentSecBench expectations
- Extend or harden the JSON Schema (`canonical/schemas/` → `aesa build schemas`)
- Add corpus cases (`tests/corpus/`) and AgentSecBench cases (`tests/benchmark/`)
- Improve tooling adapters (`tools/aesa/inventory/`)
- Add anonymized examples under `examples/`
- Improve usage docs (keep English; sync CLI changes to `docs/CLI-REFERENCE.md`)
- Report documentation defects that could cause unsafe auditor behavior (see `SECURITY.md`)

## Contribution principles

1. **Do not weaken hard gates.** Missing evidence must remain `NOT VERIFIED` / `INSUFFICIENT EVIDENCE`.
2. **Do not add execution advice** that installs, runs, or contacts target-controlled code/services during a passive audit.
3. **Do not request secrets** in prompts, examples, or docs.
4. **Keep enums stable** unless a major version bump is intentional.
5. **Separate evidence classes.** Do not conflate source review, artifact verification, host configuration, and runtime observation.
6. **No numeric score invention.** Qualitative risk, confidence, and coverage stay separate.
7. **English only:** narrative reports and procedure-facing text use **English**. Technical identifiers (paths, enums, JSON keys, CVE IDs) stay in English.

## Dependency updates (Dependabot)

GitHub Dependabot is configured in [`.github/dependabot.yml`](.github/dependabot.yml):

| Ecosystem | Directory | Cadence |
| --- | --- | --- |
| `uv` | `/tools` | Weekly (Monday UTC) |
| `docker` | `/` | Weekly (Monday UTC) |
| `github-actions` | `/` | Weekly (Monday UTC) |

Stack: **uv + pyproject.toml + uv.lock + Ruff + Pytest + mypy** (no Poetry / pip-tools / Pipenv).

- Python: declare constraints in [`tools/pyproject.toml`](tools/pyproject.toml) via `uv add` / `uv add --dev`; lock exact versions + hashes in [`tools/uv.lock`](tools/uv.lock); interpreter minor in [`tools/.python-version`](tools/.python-version) (`3.15`). Commit all three; ignore `.venv/`.
- Docker: [`Dockerfile`](Dockerfile) pins `python:3.15.2-slim-trixie@sha256:…` + `ghcr.io/astral-sh/uv:…@sha256:…`; `uv sync --locked --no-dev`.
- Actions: full commit SHAs with version comments; CI uses `uv python install 3.15.2` + `uv sync --locked` + `uv run --locked …`.
- Cooldown delays non-security version PRs; **security updates are not delayed**.
- After uv PRs: `cd tools && uv sync --locked && uv run --locked aesa build all`.
- After Docker PRs: `docker compose build`.
- Optional hooks: `uvx pre-commit install` (Ruff via [`.pre-commit-config.yaml`](.pre-commit-config.yaml)).

## Pull request checklist

- [ ] Change targets the correct procedure version under `prompts/`
- [ ] `aesa build all`, `aesa corpus run`, and (when relevant) `aesa benchmark run` pass
- [ ] New CLI surface documented in `docs/CLI-REFERENCE.md` + `tools/README.md` + `DOCUMENTATION-INDEX.md`
- [ ] New Guard rules documented in `docs/SECURITY-RULES.md` with bench expectations
- [ ] Schema and example updates remain consistent with report enums
- [ ] New modules listed in `modules/README.md`, `prompts/02-modules.md`, and the auditor skill
- [ ] Docs do not market AESA as an automated scanner or certification
- [ ] No production credentials, customer data, or live exploit payloads
- [ ] Dependabot / pin PRs leave `pyproject.toml` + `uv.lock` consistent (`uv sync --locked`); Docker digests still build
- [ ] Version streams stay aligned (`VERSION`, `canonical/versions.json`, package metadata)

## Procedure versioning

| Change type | Version impact |
| --- | --- |
| Typo / clarification with no semantic change | Patch |
| New optional module guidance; additive schema fields with defaults | Minor |
| Changed decision enums, hard gates, or mandatory workflow meaning | Major (new `prompts/` tree or versioned kit directory) |

When adding a new major procedure, keep prior versions under `prompts/` for reproducibility of historical audits.

Keep kit files under `prompts/` consistent with each other:

- **Canonical schema:** edit `canonical/schemas/audit-report.schema.json`, then run `aesa build schemas`.
- **Prompt kit composition:** declared in `canonical/prompt-kit.manifest.json` (split kit files remain editable sources).
- Prefer editing `prompts/01-core-prompt.md`, `02-modules.md`, and `03-report-contract.md` for procedure changes; regenerate the monolith with `aesa build prompts --write` (see `docs/architecture/ADR-003-monolith-generation.md`). CI runs a parity check so the monolith must not drift silently.
- Edit `04-passive-guardrails.md` directly when changing passive-audit boundaries; then regenerate or align `audit.full.md`.
- CI runs `aesa build all` — generated schema aliases must match canonical; `VERSION`, `canonical/versions.json`, `tools/pyproject.toml`, and `tools/aesa/__init__.py` must stay aligned.

## Code of conduct expectations

Be precise, evidence-oriented, and respectful. Disagreement about severity is fine; unsupported accusation of maintainers is not. Unobservable controls are `NOT VERIFIED`, not automatic findings against authors.

## Corpus contributions (R-001 / R-014 pilot)

1. Add fixtures under `tests/corpus/fixtures/` — synthetic only, no secrets or working exploits.
2. Add a case manifest in `tests/corpus/cases/*.json` with expected validator outcomes.
3. Run `aesa corpus run` and `pytest`.
4. Document ground truth and intentional `NOT VERIFIED` gaps in the case title/description.

## License

By contributing, you agree that your contributions are licensed under the MIT License.
