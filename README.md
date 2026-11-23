<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/morsel-logo-dark.svg">
    <img alt="morsel" src="assets/morsel-logo-light.svg" width="360">
  </picture>
</p>

<h3 align="center">Feed your agents morsels, not feasts.</h3>

<p align="center">
  A context engine for AI agents, inspired by the client side of GraphQL.<br>
  Agents query exactly what they need. Repeated content can become a recoverable reference.<br>
  Every query response declares its local token meter and budget.
</p>

<p align="center">
  <img alt="status" src="https://img.shields.io/badge/status-design%20phase-FF5A36">
  <img alt="go" src="https://img.shields.io/badge/go-single%20binary-17120F">
  <img alt="mcp" src="https://img.shields.io/badge/MCP-native-17120F">
  <img alt="license" src="https://img.shields.io/badge/license-Apache--2.0-17120F">
</p>

---

> **Pre-alpha: design only.** There is no Go implementation, installable release or executed benchmark yet. APIs below are planned. Specs describe commitments to test, not working product guarantees.

## What Morsel is for

Agents often read whole files when they need a signature or a few lines, and can request the same content repeatedly. Morsel aims to make that context explicit: query selected fields, bound the response using a declared local meter, and recover repeated text through short references.

The design borrows field selection, normalized caching and request deduplication from GraphQL clients. It runs as one local MCP server, with files and Go symbols in v0.1. It does not orchestrate agents or call models in the runtime.

```graphql
query @budget(tokens: 4000) {
  symbol(name: "CreateOrder", in: "internal/orders") {
    signature
    doc
    callers(first: 10) { approx items { name line } next }
  }
  file(path: "internal/orders/service.go") {
    outline { name kind line }
    lines(from: 40, to: 72)
  }
}
```

Query results use a compact JSON envelope with `data`, `cost` and optional `crumbs`, `truncated` or `errors`. Cost fields are `est`, `act`, `budget` and `meter`. The default planned meter, `heuristic-v1`, estimates tokens from UTF-8 byte length. Its budget covers the final textual envelope; it does not guarantee provider token counts or billing.

Crumbs replace eligible repeated text only for an explicit consumer within one connection, and only when smaller. Separate agent contexts need separate consumer IDs. Without a consumer, Morsel still projects and caches data but sends complete selected values. `morsel_expand` or `fresh:true` recovers current content.

The query language is a GraphQL selection profile. Crumbs and budget omissions are explicit extensions to the result shape; this is not a general GraphQL endpoint. See the [protocol contract](specs/001-mvp/contracts/protocol.md).

## Construction plan

The MVP is divided into seven specs, each with acceptance scenarios, an implementation plan and pending tasks:

| Spec | Deliverable |
|---|---|
| [M01 Foundation](specs/001-mvp/01-foundation/spec.md) | Module, canonical contracts, reproducible checks and contribution workflow |
| [M02 Workspace](specs/001-mvp/02-workspace/spec.md) | Confined reads, content snapshots, cache and Go symbols |
| [M03 Queries](specs/001-mvp/03-query/spec.md) | Validation, field projection, discovery and pagination |
| [M04 Budget](specs/001-mvp/04-budget/spec.md) | Deterministic output within the declared local meter |
| [M05 Delivery](specs/001-mvp/05-delivery/spec.md) | Consumer isolation, crumbs, expiry and recovery |
| [M06 Interfaces](specs/001-mvp/06-interfaces/spec.md) | MCP stdio, CLI and safe initialization |
| [M07 Evidence](specs/001-mvp/07-evidence/spec.md) | Aggregate stats, independent A/B runner and release gates |

Start with the [repository review](docs/REPOSITORY-REVIEW.md), [architecture](docs/ARCHITECTURE.md) and [dependency catalog](specs/001-mvp/README.md). The architecture is a modular Go monolith, with thin MCP/CLI adapters and explicit package boundaries. No microservices or generic plugin framework are required for v0.1.

## Planned CLI

These commands become available after implementation; they cannot be run from this repository yet:

```sh
morsel init                       # config + printed instructions snippet
morsel init --instructions AGENTS.md  # explicitly apply an idempotent block
morsel serve                      # MCP stdio server
morsel query '{ file(path:"README.md") { lines(from:1,to:10) } }'
morsel stats --session <id>        # local estimates, not provider billing
```

The planned module path follows the current repository: `github.com/lvcas-dotcom/morsel`. Installation instructions will be tested against a real release before publication. The optional A/B runner will live outside the runtime in `bench/`; it may call a user-selected provider only when explicitly run.

## Evidence and roadmap

No savings, latency, accuracy or cross-platform compatibility claims have been validated. The first benchmark must report task-level token use **and success**, using pinned inputs and independent verification. Local stats against naive full-file reads are a separate estimate.

The [vision](docs/VISION.md) defines H1 and the stop criterion. Upstream MCP projection, persistent cache, Postgres, other languages, recipes and a shared daemon remain [reserved future specs](specs/README.md). Their implementation depends on evidence from v0.1.

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md), the [constitution](specs/constitution.md) and the relevant spec. Run the currently available documentary check:

```sh
python3 tools/check_specs.py
```

Design documents are in Brazilian Portuguese. Runtime tests and CI remain tasks in M01; the documentary checker does not validate application behavior. Security status and reporting limitations are in [SECURITY.md](SECURITY.md).

## License

[Apache-2.0](LICENSE).
