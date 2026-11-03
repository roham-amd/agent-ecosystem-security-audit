# Runtime validation (R-009)

**Status:** Schema and procedure boundary only — **no executable runtime harness ships in this repository.**

Passive AESA audits must not execute target-controlled code. When organizational policy requires behavioral proof:

1. Complete a separate written authorization (see `prompts/01-core-prompt.md` Phase 8).
2. Run tests only in an isolated staging environment with synthetic data and default-deny egress.
3. Record outcomes using [`schemas/runtime-test-record.schema.json`](../../schemas/runtime-test-record.schema.json).

Do not set `trust_chain.runtime_behavior_tested=true` in the passive JSON summary unless matching `RUNTIME` evidence exists.

See [`docs/recipes/staging-boundary.md`](../recipes/staging-boundary.md).
