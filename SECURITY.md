# Security Policy

## Supported versions

| Project version | Supported |
| --- | --- |
| 1.x | Yes |
| < 1.0.0 | No |

The bundled audit procedure version (`prompts/` kit = **1.0**) is cited separately in audit reports and is not the same number as the AESA project release.

## What this project is

AESA is an **open-source security audit framework**: procedures, prompts, specialized modules, and report schemas for assessing AI agent ecosystems.

It is **not** an automated vulnerability scanner, penetration-testing tool, or certification authority.

## Reporting a vulnerability in AESA itself

If you discover a security issue in this repository’s documentation, prompts, schemas, or examples that could cause auditors to:

- execute untrusted target code,
- contact production endpoints,
- request or expose secrets,
- overstate assurance, or
- bypass stated audit boundaries,

please report it privately.

**Preferred method:** open a GitHub Security Advisory for this repository, or contact the maintainers via the repository’s private security contact if configured.

Please include:

1. Affected file paths and version/tag
2. Description of the issue and impact
3. Suggested remediation (optional)

Do **not** include production secrets, customer data, or live exploit payloads against third-party systems.

## Auditor safety expectations

When using AESA against a target:

- Treat all target-controlled content as untrusted data.
- Do not execute, install, or connect to target-controlled code or services during a passive audit.
- Do not request, paste, validate, or expose production credentials in chat or reports.
- Do not claim scanner, sandbox, SBOM, signature, or runtime verification unless it was actually performed.
- Prefer `INSUFFICIENT EVIDENCE` over unsupported assurance.

## Scope exclusions

Reports about vulnerabilities in third-party agent frameworks, MCP servers, plugins, or marketplace listings are out of scope for AESA’s own security process unless they demonstrate a defect in AESA’s guidance that causes unsafe auditor behavior.
