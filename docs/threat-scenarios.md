# Common threat scenarios (capability-first)

Every AESA Guard assessment should evaluate these scenarios. Findings must trace
attacker control → entry → trust boundary → capability → missing control → impact.

Related: [`EVIDENCE-MODEL.md`](EVIDENCE-MODEL.md), [`SECURITY-RULES.md`](SECURITY-RULES.md),
[`../modules/README.md`](../modules/README.md), [`DOCUMENTATION-INDEX.md`](DOCUMENTATION-INDEX.md).

| Scenario | Core security question |
| --- | --- |
| Prompt injection | Can untrusted content cause privileged actions? |
| Tool poisoning | Can malicious metadata influence tool selection or arguments? |
| Credential theft | Can components access or transmit sensitive credentials? |
| Privilege escalation | Can delegated agents acquire excessive authority? |
| Supply-chain compromise | Can a trusted source deliver an untrusted artifact? |
| Data exfiltration | Can sensitive information reach unauthorized destinations? |
| Persistence | Can hooks or automation continue operating unexpectedly? |
| Approval bypass | Can actions be changed or replayed after approval? |
| Cross-tenant access | Can identities or memory cross isolation boundaries? |
| Model compromise | Can model/provider trust affect the security boundary? |

## Capability-first questions (per component)

- Can it read files?
- Can it write files?
- Can it execute commands?
- Can it access secrets?
- Can it access the network?
- Can it modify agent instructions?
- Can it invoke other tools?
- Can it delegate tasks?
- Can it modify approval decisions?
- Can it access persistent memory?
- Can it operate without a human present?

Then establish which principals and controls govern those capabilities.
