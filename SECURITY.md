# Security

Morsel is pre-alpha and has no released runtime or supported production version. Security requirements are design commitments, not audited guarantees. Do not deploy it against sensitive workspaces on the strength of these documents.

## Reporting

A private reporting channel has not been configured or verified. Do not publish secrets or exploit payloads in a public issue. You may open a minimal issue requesting a private contact, without vulnerability details. Configuring a real private channel and naming its responsible maintainer are release gates in [M01](specs/001-mvp/01-foundation/spec.md) and [M07](specs/001-mvp/07-evidence/spec.md); no response SLA is promised yet.

## Intended boundaries

The v0.1 runtime is local, read-only toward data sources, without network calls or telemetry. Files are confined to the configured root, subject to sensitive-file and ignore policies before any cache access. Init only writes explicitly selected local configuration/instruction files; stats writes bounded aggregate state.

Filesystem confinement is not an operating-system sandbox. A malicious local user, hardlinks, mounts and hostile filesystems require system-level isolation. MCP consumer IDs identify contexts for deduplication; they do not authenticate users.

The optional benchmark runner is separate from the runtime and may send fixture content to the chosen provider. It requires explicit execution with non-sensitive fixtures. Never put production credentials or private repositories into public benchmark artifacts.

Implementation and release security checks remain pending; see [workspace spec](specs/001-mvp/02-workspace/spec.md) for adversarial scenarios.
