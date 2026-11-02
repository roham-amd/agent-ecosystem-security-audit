# Contributing to AESA

Thank you for helping improve the Agent Ecosystem Security Audit framework.

## Ways to contribute

- Clarify audit procedure language without weakening evidence gates
- Improve specialized modules (`modules/`)
- Extend or harden the JSON Schema (`schemas/`)
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

- Prefer editing `prompts/audit.full.md` when changing the full procedure text, then align the split kit files (`01-core-prompt.md`, `02-modules.md`, `03-report-contract.md`, `audit.md`) as needed.
- Edit `04-passive-guardrails.md` directly when changing passive-audit boundaries; then align short pointers in `audit.full.md` Sections 4.5, 4.6, and 6 if needed.
- There is no generator script; treat the split kit files as maintained source.

## Code of conduct expectations

Be precise, evidence-oriented, and respectful. Disagreement about severity is fine; unsupported accusation of maintainers is not. Unobservable controls are `NOT VERIFIED`, not automatic findings against authors.

## License

By contributing, you agree that your contributions are licensed under the MIT License.
