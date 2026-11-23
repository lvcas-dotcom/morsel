# Specs do Morsel

O projeto segue desenvolvimento por especificação. O estado atual é design: nenhuma tarefa de runtime foi implementada. Comece pela [análise](../docs/REPOSITORY-REVIEW.md), pela [constituição v2](constitution.md) e pelo [catálogo do MVP](001-mvp/README.md).

## Fontes de verdade

| Documento | Autoridade |
|---|---|
| [constitution.md](constitution.md) | Princípios globais |
| [001-mvp/spec.md](001-mvp/spec.md) | Produto, histórias, FR e critérios de sucesso |
| [001-mvp/contracts/protocol.md](001-mvp/contracts/protocol.md) | Semântica de wire |
| [001-mvp/contracts/](001-mvp/contracts/) | SDL, JSON Schema, tools e exemplos canônicos |
| [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md) | Fronteiras e dependências |
| [001-mvp/README.md](001-mvp/README.md) | Specs menores, dependências e cobertura de FR |
| `001-mvp/0*/{spec,plan,tasks}.md` | Aceitação, desenho local e tarefas de cada entrega |

Não resolver conflito escolhendo um documento silenciosamente. Corrigir requisitos, contrato e testes afetados juntos, antes de implementar. `specs/spec.md` e `specs/tasks.md` são somente links legados.

## Fluxo de contribuição

1. Ler a constituição, a spec da entrega e os contratos envolvidos.
2. Alterar requisitos antes de comportamento novo; registrar decisão relevante em research.
3. Selecionar uma tarefa pequena com dependências concluídas. Implementação começa por teste de comportamento que falha.
4. Implementar apenas a fatia selecionada, rodar checks pertinentes e revisar diff/casos de borda.
5. Marcar tarefa somente com evidência de aceite. PR referencia IDs de tarefa e FR; documentação pronta não significa runtime pronto.

Specs estão em português; README e guias de contribuição são em inglês. Tradução das instruções de instalação é gate de release. IDs são estáveis e não se repetem entre entregas.

## Execução com agentes

```text
Leia specs/constitution.md, specs/001-mvp/README.md e docs/ARCHITECTURE.md.
Leia spec.md, plan.md e tasks.md da entrega selecionada e os contratos afetados.
Implemente somente M0X-T0Y e suas dependências já autorizadas.
Comece pelo teste, verifique os critérios de aceite e reporte limitações.
Não marque entrega ou benchmark como concluído sem evidência executada.
```

## Depois do MVP

IDs existentes permanecem reservados. São ideias, sem especificação implementável ou compromisso de API. Só avançar após o gate H1 da M07.

| ID reservado | Escopo futuro | Versão pretendida |
|---|---|---|
| 002-upstream-mcp | Proxy com projeção e fronteira de confiança | v0.2 |
| 003-persistent-pantry | Cache persistente, permissões e migração | v0.2 |
| 004-postgres | Fonte SQL somente leitura e autorização | v0.3 |
| 005-multilang-symbols | Outras linguagens, sem assumir cgo no núcleo | v0.3 |
| 006-recipes | Consultas persistidas e versionadas | v0.3 |
| 007-daemon | HTTP, autenticação, quotas e isolamento | v0.4 |

Validação documental disponível agora: `python3 tools/check_specs.py`. Os comandos Go serão adicionados na M01, junto da implementação.
