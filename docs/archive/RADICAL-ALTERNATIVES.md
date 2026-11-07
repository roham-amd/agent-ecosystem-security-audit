# Radical alternatives (MVP status)

From the November 2026 strategic review §F. Shipped as **opt-in MVPs** under
`authdiff`, not as the default product path.

## 1. Authority broker — `authdiff run`

```bash
authdiff run --lock AUTHORITY.lock.json -- npx -y @modelcontextprotocol/server-everything
```

Scrubs secret-shaped env vars and records the lock path for the child. Full
stdio MCP frame proxy is deferred; pair with `authdiff snapshot` to pin tool
description hashes.

## 2. Attack-replay corpus — `examples/attack-replay/`

Inert malicious configs aimed at `127.0.0.1:9/canary`. Use as the regression
suite other scanners measure against:

```bash
authdiff scan examples/attack-replay/01-sessionstart-curl-env
```

## 3. AUTHORITY spec + LSP stub — `authdiff lsp-validate`

JSON Schemas:

- [`schemas/authority-lock.schema.json`](../schemas/authority-lock.schema.json)
- [`schemas/authority-policy.schema.json`](../schemas/authority-policy.schema.json)

```bash
authdiff lsp-validate AUTHORITY.lock.json
```

A full language server (diagnostics-on-type, CodeActions) remains deferred;
this stub is the schema reference implementation entry point.
