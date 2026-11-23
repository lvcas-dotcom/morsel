# Ferramentas MCP v1

Definições canônicas de nome, descrição, inputSchema e annotations: [tools.json](tools.json). Sem cópias literais neste documento. Envelope textual: [envelope.schema.json](envelope.schema.json); regras de execução: [protocol.md](protocol.md).

| Tool | Semântica |
|---|---|
| morsel_query | Seleção, variáveis e operação opcional; budget explícito prevalece sobre diretiva; consumer omitido desativa crumbs |
| morsel_schema | Guia textual compacto gerado do SDL; busca opcional, teto de 600 unidades |
| morsel_expand | Fragmento repete campo original; ID de entidade exige select; retorna versão atual com fresh |

As três descrições têm meta conjunta de 450 unidades heurísticas; discovery completo (schemas e annotations incluídos) é medido separadamente. Não há `outputSchema` MCP no perfil textual v1; o JSON Schema valida o bloco de texto decodificado. Evitar fornecer envelope duplicado em structuredContent.

## Snippet gerado por init

Init imprime o snippet por padrão. Só grava com `--instructions <path>` explícito e seguro. Bloco delimitado é idempotente e não substitui conteúdo alheio.

```markdown
<!-- morsel:begin -->
## Context: use morsel
This repository can be served by the morsel MCP server.
- Use morsel_query for selected signatures, docs, outlines or line ranges.
- Read body/content when implementation detail is needed.
- Omit consumer unless you can assign a stable ID to this shared context.
- Different contexts/subagents must use different consumer IDs.
- {$crumb,v,d} refers to previously delivered text; use morsel_expand with
  the exact $crumb token, or fresh:true, to recover current content.
- Use morsel_schema to discover supported fields and paths.
- Token cost is measured locally; heuristic values are not provider billing.
<!-- morsel:end -->
```

O snippet não promete que clientes distinguem subagentes automaticamente. Validar a configuração real na M06 antes de ativar supressão.
