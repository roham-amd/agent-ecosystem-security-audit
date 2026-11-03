# Contributing to AESA

Thank you for helping improve the Agent Ecosystem Security Audit framework.

## Ways to contribute

- Clarify audit procedure language without weakening evidence gates
- Improve specialized modules (`modules/`)
- Extend or harden the JSON Schema (`canonical/schemas/` → `aesa build schemas`)
- Add corpus cases (`tests/corpus/`) and validation fixtures
- Improve tooling adapters (`tools/aesa/inventory/`)
- Add anonymized examples under `examples/`
- Improve usage docs and translator notes
- Report documentation defects that could cause unsafe auditor behavior (see `SECURITY.md`)

## Contribution principles

1. **Do not weaken hard gates.** Missing evidence must remain `NOT VERIFIED` / `INSUFFICIENT EVIDENCE`.
2. **Do not add execution advice** that installs, runs, or contacts target-controlled code/services during a passive audit.
3. **Do not request secrets** in prompts, examples, or docs.
4. **Keep enums stable** unless a major version bump is intentional.
5. **Separate evidence classes.** Do not conflate source review, artifact verification, host configuration, and runtime observation.
6. **No numeric score invention.** Qualitative risk, confidence, and coverage stay separate.
7. **English only:** narrative reports and procedure-facing text use **English**. Technical identifiers (paths, enums, JSON keys, CVE IDs) stay in English.

## Pull request checklist

- [ ] Change targets the correct procedure version under `prompts/`
- [ ] `aesa build all` and `aesa corpus run` pass when tooling changes are included
- [ ] Schema and example updates remain consistent with Section 22 enums
- [ ] New modules state applicability and `N/A` / `NOT VERIFIED` rules
- [ ] Docs do not market AESA as an automated scanner or certification
- [ ] No production credentials, customer data, or live exploit payloads

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
- Prefer editing `prompts/01-core-prompt.md`, `02-modules.md`, and `03-report-contract.md` for procedure changes; align `prompts/audit.full.md` when changing monolithic consumers (full regeneration automation is planned — do not let monolith drift silently).
- Edit `04-passive-guardrails.md` directly when changing passive-audit boundaries; then align short pointers in `audit.full.md` Sections 4.5, 4.6, and 6 if needed.
- CI runs `aesa build all` — generated schema aliases must match canonical.

## Code of conduct expectations

Be precise, evidence-oriented, and respectful. Disagreement about severity is fine; unsupported accusation of maintainers is not. Unobservable controls are `NOT VERIFIED`, not automatic findings against authors.

## Corpus contributions (R-001 / R-014 pilot)

1. Add fixtures under `tests/corpus/fixtures/` — synthetic only, no secrets or working exploits.
2. Add a case manifest in `tests/corpus/cases/*.json` with expected validator outcomes.
3. Run `aesa corpus run` and `pytest`.
4. Document ground truth and intentional `NOT VERIFIED` gaps in the case title/description.

## License

By contributing, you agree that your contributions are licensed under the MIT License.
