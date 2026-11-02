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
7. **Preserve technical identifiers in English** even when narrative translations are added.

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
| Changed decision enums, hard gates, or mandatory workflow meaning | Major (`prompts/vN/`) |

When adding a new major procedure, keep prior versions under `prompts/` for reproducibility of historical audits.

## Code of conduct expectations

Be precise, evidence-oriented, and respectful. Disagreement about severity is fine; unsupported accusation of maintainers is not. Unobservable controls are `NOT VERIFIED`, not automatic findings against authors.

## License

By contributing, you agree that your contributions are licensed under the MIT License.
