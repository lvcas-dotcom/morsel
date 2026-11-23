# Contrato: ferramentas MCP (spec 001)

O servidor expõe **exatamente três ferramentas** (constituição, princípio IX). As descrições abaixo são enviadas ao agente **literalmente**: são parte do contrato e contam no orçamento de contexto. Mudá-las exige mudar este arquivo. A meta é que as três definições juntas tenham **menos de 450 tokens**.

---

## `morsel_query`

**Descrição (enviada ao agente):**
> Query the codebase graph with a GraphQL selection. Ask only for fields you need (e.g. `signature` instead of `body`, `lines(from,to)` instead of `content`). Every response reports its token cost and stays within budget. Content you already received comes back as a crumb `{id, v, d}`; use morsel_expand to get it again.

**Entrada:**

```json
{
  "type": "object",
  "properties": {
    "query":    { "type": "string", "description": "GraphQL query (read-only)." },
    "budget":   { "type": "integer", "minimum": 100, "description": "Token budget. Default from config." },
    "fresh":    { "type": "boolean", "description": "Ignore crumbs; return full content." },
    "consumer": { "type": "string", "description": "Optional consumer id (e.g. subagent name)." }
  },
  "required": ["query"]
}
```

**Saída:** um envelope ([`envelope.schema.json`](envelope.schema.json)) serializado como **JSON compacto** num único bloco de texto.

**Erros (dentro do envelope, em `errors`):**

| `code` | Quando | Conteúdo extra |
|---|---|---|
| `invalid_query` | Erro de sintaxe ou de validação | `at` (linha:coluna), `suggest` (nomes próximos) |
| `over_budget` | Não cabe nem com cortes | `breakdown`: custo estimado por campo |
| `not_found` | Entidade inexistente | `id` ou `path` |
| `denied` | Caminho fora da raiz ou sensível | `path` (nunca o conteúdo) |

## `morsel_schema`

**Descrição (enviada ao agente):**
> Discover what you can query. Without arguments returns a compact overview; with `search` returns only matching types and fields, with their path from the root.

**Entrada:**

```json
{
  "type": "object",
  "properties": {
    "search": { "type": "string" }
  }
}
```

**Saída:** SDL **minificado** (sem descrições longas), por exemplo: `Query{file(path:S!):File symbol(name:S! in:S kind:SymbolKind):[Symbol!]!…}`. Sem argumentos, a saída tem no máximo 600 tokens.

## `morsel_expand`

**Descrição (enviada ao agente):**
> Get the full content of an entity by id (from a crumb or a previous answer), optionally selecting fields.

**Entrada:**

```json
{
  "type": "object",
  "properties": {
    "id":       { "type": "string" },
    "select":   { "type": "string", "description": "GraphQL selection, e.g. \"{ signature body }\"" },
    "budget":   { "type": "integer", "minimum": 100 },
    "consumer": { "type": "string" }
  },
  "required": ["id"]
}
```

**Semântica:** equivale a `query { ref(id: $id) <select> }` com `fresh: true`.

---

## Snippet de instruções gerado por `morsel init`

Este snippet é adicionado ao `AGENTS.md` ou `CLAUDE.md` (sem sobrescrever conteúdo existente):

```markdown
## Context: use morsel
This repo is served by the `morsel` MCP server. Prefer it over reading whole files:
- Use `morsel_query` to fetch only what you need: `symbol(name:"X"){ signature doc }`,
  `file(path:"…"){ outline{ name kind line } }`, `file(path:"…"){ lines(from:a,to:b) }`.
- Read `body`/`content` only when you will edit or must understand the implementation.
- Crumbs `{id,v,d}` mean you already received that content. Use `morsel_expand` if you no longer have it.
- Run `morsel_schema` once if unsure which fields exist.
```
