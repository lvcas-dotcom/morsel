# Contributing to Morsel

Morsel is in the design phase. There is no runnable application yet. Start with the [spec catalog](specs/README.md), [repository review](docs/REPOSITORY-REVIEW.md) and [architecture](docs/ARCHITECTURE.md).

## Proposing a change

Open an issue describing the concrete problem, expected behavior and examples. Behavior changes start with a spec/contract change. Keep a PR focused on one task or coherent slice; reference its task ID and FR requirements. Avoid speculative frameworks or unrelated cleanup.

For implementation, write the failing behavior test first. Include failure paths, authorization, cancellation and relevant integration evidence. Update contracts and examples together. Do not mark a task complete using documentation or stubs as evidence of working behavior.

## Checks available now

```sh
python3 tools/check_specs.py
```

The checker uses the Python standard library for links, IDs, dependency coverage and semantic fixture checks. If `jsonschema` supporting Draft 2020-12 is installed, it also validates schemas and all fixtures. Require that validation explicitly with:

```sh
python3 tools/check_specs.py --require-jsonschema
```

Use an interpreter with that dependency installed. The implementation foundation will add Go contract tests and CI; Go build/race/integration checks do not exist yet. See [M01](specs/001-mvp/01-foundation/spec.md).

## Review expectations

Explain the user-visible result, relevant design tradeoffs, checks run and unverified limits. Follow the package boundaries; prefer concrete types, small consumer-owned interfaces and explicit ownership/cancellation. Never include credentials, local tool settings, real source content or provider keys in fixtures/logs.

A release requires the [M07 gates](specs/001-mvp/07-evidence/spec.md). Benchmark claims need reproducible evidence and success measurements. Keep synthetic contract fixtures clearly separate from runtime observations.

Contributions are under the project's [Apache-2.0 license](LICENSE). Preserve attribution and review dependency licenses. Security issues follow [SECURITY.md](SECURITY.md). Be respectful, discuss behavior and evidence, and avoid personal attacks. A formal conduct policy with an actual enforcement contact is a release prerequisite, tracked in M01.
