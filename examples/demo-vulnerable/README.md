# Demo vulnerable repo (AESA Authority Diff walkthrough)

Seeded fixtures that **should** produce gated findings. Not for production use.

```bash
aesa scan examples/demo-vulnerable -o /tmp/aesa-demo --fail-on high
aesa annotate /tmp/aesa-demo/findings.json --format pr-comment
aesa harden --findings /tmp/aesa-demo/findings.json
```

Expected rule hits include: RULE-011 (unpinned), RULE-012 (literal secret),
RULE-013 (HTTP MCP), RULE-015 (curl|sh), RULE-016 (`pull_request_target` + agent),
RULE-017 (permission bypass), and content-based RULE-010.
