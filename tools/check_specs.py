#!/usr/bin/env python3
"""Check documentary consistency; this is not an application contract test.

Standard-library checks always run. JSON Schema validation is available with
jsonschema (Draft 2020-12), and mandatory with --require-jsonschema.
"""

import argparse
import base64
import copy
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit


def compact(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def meter(value):
    return (len(compact(value).encode("utf-8")) + 3) // 4


def check(root, require_jsonschema=False):
    problems = []

    def expect(condition, message):
        if not condition:
            problems.append(message)

    def read(relative):
        path = root / relative
        if not path.is_file():
            problems.append(f"Missing required file: {relative}")
            return ""
        return path.read_text(encoding="utf-8")

    def load(relative):
        try:
            return json.loads(read(relative))
        except (ValueError, OSError) as error:
            problems.append(f"{relative}: {error}")
            return None

    docs = sorted(root.glob("*.md"))
    for folder in ("docs", "specs"):
        docs.extend(sorted((root / folder).rglob("*.md")))
    for path in docs:
        text = path.read_text(encoding="utf-8")
        # Fenced examples are not documentary links to local files.
        prose = re.sub(r"```.*?```", "", text, flags=re.S)
        for target in re.findall(r"\[[^\]\n]+\]\(([^)\n]+)\)", prose):
            target = target.strip().strip("<>")
            parts = urlsplit(target)
            if parts.scheme or parts.netloc or not parts.path:
                continue
            resolved = (path.parent / unquote(parts.path)).resolve()
            expect(resolved.is_relative_to(root), f"{path.relative_to(root)}: link escapes repository: {target}")
            expect(resolved.exists(), f"{path.relative_to(root)}: broken local link: {target}")

    spec = read("specs/001-mvp/spec.md")
    requirements = re.findall(r"\*\*FR-(\d{3})\*\*", spec)
    required = set(requirements)
    expect(len(requirements) == len(required), "Duplicate FR definition in MVP spec")
    expect(required == {f"{n:03}" for n in range(1, 43)}, "MVP must define exactly FR-001 through FR-042")
    catalog = read("specs/001-mvp/README.md")
    deliveries, owners, task_coverage, task_ids = {}, {}, set(), set()
    for line in catalog.splitlines():
        cells = [cell.strip() for cell in line.split("|")[1:-1]]
        if len(cells) != 4:
            continue
        match = re.search(r"\[(M\d{2})[^]]*\]\(([^)]+/spec\.md)\)", cells[0])
        if not match:
            continue
        key, relative = match.groups()
        expect(key not in deliveries, f"Duplicate delivery {key}")
        deliveries[key] = re.findall(r"M\d{2}", cells[2])
        for fr in re.findall(r"FR-(\d{3})", cells[3]):
            expect(fr in required, f"{key}: unknown primary FR-{fr}")
            expect(fr not in owners, f"FR-{fr}: multiple primary owners")
            owners[fr] = key
        folder = Path("specs/001-mvp") / Path(relative).parent
        local_spec = read(folder / "spec.md")
        local_plan = read(folder / "plan.md")
        tasks = read(folder / "tasks.md")
        expect("Aceitação" in local_spec, f"{key}: missing acceptance scenarios")
        expect("pendente" in local_spec, f"{key}: missing implementation status")
        expect(bool(local_plan.strip()), f"{key}: empty plan")
        entries = re.findall(r"^- \[([ x])\] (M\d{2}-T\d{2}) (.+)$", tasks, re.M)
        expect(bool(entries), f"{key}: no executable task checklist")
        for _state, task_id, description in entries:
            expect(task_id.startswith(key + "-"), f"{task_id}: wrong namespace")
            expect(task_id not in task_ids, f"Duplicate task ID: {task_id}")
            task_ids.add(task_id)
            refs = re.findall(r"FR-(\d{3})", description)
            expect(bool(refs), f"{task_id}: missing FR traceability")
            for fr in refs:
                expect(fr in required, f"{task_id}: unknown FR-{fr}")
                task_coverage.add(fr)
            # A checkbox may change after implementation; no assumption that docs
            # can prove whether completion claims are true.
    expect(set(deliveries) == {f"M{n:02}" for n in range(1, 8)}, "Catalog must contain M01 through M07")
    expect(set(owners) == required, f"Missing primary owners: {sorted(required - set(owners))}")
    expect(task_coverage == required, f"Missing task FR coverage: {sorted(required - task_coverage)}")

    active, visited = set(), set()

    def visit(key):
        if key in active:
            problems.append(f"Dependency cycle at {key}")
            return
        if key in visited:
            return
        active.add(key)
        for dependency in deliveries.get(key, []):
            expect(dependency in deliveries, f"{key}: unknown dependency {dependency}")
            visit(dependency)
        active.remove(key)
        visited.add(key)

    for key in deliveries:
        visit(key)

    base = Path("specs/001-mvp/contracts")
    tools = load(base / "tools.json")
    envelope_schema = load(base / "envelope.schema.json")
    fixtures = load(base / "examples.json")
    tools = tools if isinstance(tools, list) else []
    fixtures = fixtures if isinstance(fixtures, dict) else {}
    by_name = {tool.get("name"): tool for tool in tools if isinstance(tool, dict)}
    expected_tools = {"morsel_query", "morsel_schema", "morsel_expand"}
    expect(len(tools) == 3 and set(by_name) == expected_tools, "Exactly three canonical MCP tools required")
    descriptions = "".join(tool.get("description", "") for tool in tools)
    description_cost = (len(descriptions.encode("utf-8")) + 3) // 4
    expect(description_cost <= 450, f"Tool description heuristic budget exceeded: {description_cost}")
    for tool in tools:
        expect("outputSchema" not in tool, f"{tool.get('name')}: textual v1 must not advertise structured output")
        expect(tool.get("inputSchema", {}).get("additionalProperties") is False, f"{tool.get('name')}: reject unknown input properties")

    validator = None
    try:
        from jsonschema import Draft202012Validator
        validator = Draft202012Validator
    except ImportError:
        expect(not require_jsonschema, "Draft 2020-12 validation required: use Python with jsonschema installed")
    if validator and envelope_schema:
        try:
            validator.check_schema(envelope_schema)
            for tool in tools:
                validator.check_schema(tool["inputSchema"])
        except Exception as error:
            problems.append(f"Invalid JSON Schema: {error}")

    def validate(value, schema, label):
        if validator and schema:
            try:
                errors = list(validator(schema).iter_errors(value))
                for error in errors[:5]:
                    problems.append(f"{label}: {list(error.path)}: {error.message}")
            except Exception as error:
                problems.append(f"{label}: schema validation error: {error}")

    def walk(value):
        if isinstance(value, dict):
            yield value
            for child in value.values():
                yield from walk(child)
        elif isinstance(value, list):
            for child in value:
                yield from walk(child)

    names = set()
    cases = fixtures.get("cases", [])
    expect(bool(cases), "Missing contract examples")
    for case in cases:
        name = case.get("name", "unnamed")
        expect(name not in names, f"Duplicate fixture: {name}")
        names.add(name)
        request = case.get("input", {})
        tool = by_name.get(request.get("tool"), {})
        expect(bool(tool), f"{name}: unknown input tool")
        validate(request.get("arguments"), tool.get("inputSchema"), f"{name} input")
        envelope = case.get("envelope", {})
        validate(envelope, envelope_schema, f"{name} envelope")
        cost = envelope.get("cost", {})
        expect(cost.get("meter") == "heuristic-v1", f"{name}: unsupported fixture meter")
        expect(cost.get("act") == meter(envelope), f"{name}: act does not count final compact UTF-8 envelope")
        expect(cost.get("act", 0) <= cost.get("budget", -1), f"{name}: over-budget fixture")
        found_crumbs = []
        for obj in walk(envelope.get("data")):
            if "$crumb" not in obj:
                continue
            token = obj["$crumb"]
            if token not in found_crumbs:
                found_crumbs.append(token)
            try:
                encoded = token.removeprefix("frag:")
                decoded = base64.urlsafe_b64decode(encoded + "=" * (-len(encoded) % 4)).decode("utf-8")
                fragment = json.loads(decoded)
                expect(list(fragment) == ["entity", "field", "args"], f"{name}: noncanonical fragment key order")
                expect(compact(fragment) == decoded, f"{name}: fragment JSON must be compact/canonical")
                expect(isinstance(fragment["args"], dict), f"{name}: fragment args must be an object")
            except (ValueError, KeyError, UnicodeError) as error:
                problems.append(f"{name}: invalid fragment: {error}")
        expect(found_crumbs == envelope.get("crumbs", []), f"{name}: crumbs must match first occurrence in data")
        for truncation in envelope.get("truncated", []):
            continuation = truncation.get("next", {})
            next_tool = by_name.get(continuation.get("tool"), {})
            expect(bool(next_tool), f"{name}: invalid continuation tool")
            validate(continuation.get("arguments"), next_tool.get("inputSchema"), f"{name} continuation")

    # Schema rejection examples exercise constraints, not just happy paths.
    if validator and envelope_schema and cases:
        valid = cases[0]["envelope"]
        invalid = []
        extra = copy.deepcopy(valid)
        extra["extra"] = True
        invalid.append(extra)
        wrong_meter = copy.deepcopy(valid)
        wrong_meter["cost"]["meter"] = "provider-billing"
        invalid.append(wrong_meter)
        malformed_crumb = copy.deepcopy(valid)
        malformed_crumb["data"] = {"field": {"$crumb": "frag:x", "v": "short", "d": "bad\nline"}}
        invalid.append(malformed_crumb)
        for index, value in enumerate(invalid):
            expect(not validator(envelope_schema).is_valid(value), f"Envelope schema accepts invalid mutation {index}")
        expand = by_name.get("morsel_expand", {}).get("inputSchema")
        if expand:
            expect(not validator(expand).is_valid({"id": "file:README.md"}), "Expand must require select for entity ID")
            expect(validator(expand).is_valid({"id": "frag:x"}), "Expand input should accept fragment without select; token semantics checked at runtime")

    for relative in ("LICENSE", "CONTRIBUTING.md", "SECURITY.md", "docs/ARCHITECTURE.md", "docs/REPOSITORY-REVIEW.md"):
        read(relative)
    expect("v2.0.0" in spec, "MVP must reference current constitution v2.0.0")
    for legacy, destination in (("specs/spec.md", "001-mvp/spec.md"), ("specs/tasks.md", "001-mvp/tasks.md")):
        text = read(legacy)
        expect(destination in text and len(text.splitlines()) < 12, f"{legacy}: expected short legacy redirect")

    summary = (
        f"{len(docs)} Markdown files, {len(required)} FRs, {len(deliveries)} specs, "
        f"{len(task_ids)} tasks, {len(cases)} synthetic examples; "
        f"descriptions={description_cost}, discovery={meter(tools)} heuristic units; "
        f"JSON Schema={'validated' if validator else 'not run (optional jsonschema unavailable)'}"
    )
    return problems, summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--require-jsonschema", action="store_true")
    args = parser.parse_args()
    try:
        problems, summary = check(args.root.resolve(), args.require_jsonschema)
    except (OSError, ValueError, TypeError, KeyError, AttributeError) as error:
        print(f"ERROR: invalid documentary structure: {error}", file=sys.stderr)
        return 1
    if problems:
        for problem in problems:
            print(f"ERROR: {problem}", file=sys.stderr)
        print(f"FAILED: {len(problems)} documentary checks", file=sys.stderr)
        return 1
    print(f"OK: {summary}")
    print("No application build, GraphQL execution, MCP integration or benchmark was validated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
