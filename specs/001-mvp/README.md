# MVP 001: catálogo de construção

Estado: especificado, implementação pendente. O MVP continua sendo a feature 001; M01–M07 são entregas internas e não ocupam os IDs 002–007 do roadmap.

## Entregas

| Spec | Resultado verificável | Depende de | Requisitos primários |
|---|---|---|---|
| [M01 — Fundação](01-foundation/spec.md) | Contratos empacotáveis, build e checks open source | — | FR-039, FR-040 |
| [M02 — Workspace](02-workspace/spec.md) | Leitura confinada e snapshots coerentes | M01 | FR-007, FR-008, FR-009, FR-010, FR-023, FR-024, FR-025, FR-026, FR-027, FR-035, FR-036, FR-041 |
| [M03 — Consultas](03-query/spec.md) | Projeção tipada, descoberta e paginação | M02 | FR-001, FR-002, FR-003, FR-004, FR-005, FR-006, FR-037 |
| [M04 — Orçamento](04-budget/spec.md) | JSON final dentro do medidor declarado | M03 | FR-011, FR-012, FR-013, FR-014, FR-015, FR-016, FR-029 |
| [M05 — Entregas](05-delivery/spec.md) | Crumbs isolados e recuperação sem perda | M04 | FR-017, FR-018, FR-019, FR-020, FR-021, FR-022, FR-038 |
| [M06 — Interfaces](06-interfaces/spec.md) | Fluxo real via MCP e CLI, init seguro | M05 | FR-028, FR-032, FR-034 |
| [M07 — Evidência e release](07-evidence/spec.md) | Stats, A/B reproduzível e decisão de lançamento | M06 | FR-030, FR-031, FR-033, FR-042 |

A tabela atribui um dono primário a cada FR; invariantes atravessam módulos. M02 deve testar limites também pelo executor em M03 e pelo transporte em M06. M01 só é concluída quando os contratos incorporados e checks Go existem; documentação isolada não satisfaz o gate.

## Sequência dentro das entregas

M02 começa por arquivos. M03/M04 devem produzir a primeira consulta de arquivo completa antes de ampliar o índice de símbolos previsto na M02. Depois, fechar os cenários de símbolos e só então encerrar M02–M04. Essa intercalação é permitida; nenhuma entrega é marcada pronta parcialmente.

Cada pasta contém `spec.md` (o quê/aceitação), `plan.md` (como/testes) e `tasks.md` (trabalho pendente). Uma tarefa de construção inclui testes de erro antes da implementação e uma evidência de aceite. Não publicar stubs como release.

## Gates

| Gate | Evidência obrigatória |
|---|---|
| G0 — Fundação | M01: CI real, licença, dependências fixadas e verificação dos contratos |
| G1 — Primeira bite | Arquivo → seleção → orçamento → JSON via teste integrado; sem crumbs |
| G2 — Correção do MVP | Símbolos, aliases/fragments, cursores, frescor, expiração e falhas de escrita |
| G3 — Integração | Cliente MCP via subprocesso, cancelamento, CLI e init idempotente |
| G4 — Evidência | A/B com manifests fixados, verificadores independentes e relatório inconclusivo/positivo/negativo |
| G5 — Publicação | Builds por alvo, licenças de dependências, checksums, canal de segurança e documentação testada |

G0–G5 estão pendentes. Uma release não depende de obter economia positiva, mas de publicar honestamente o resultado e aplicar o critério de parada. Roadmap 002+ não começa com H1 negativa ou inconclusiva.

## Leitura

- [Requisitos globais](spec.md), [plano de integração](plan.md), [decisões](research.md), [índice de tarefas](tasks.md).
- [Semântica do protocolo](contracts/protocol.md), [SDL](contracts/schema.graphql), [envelope](contracts/envelope.schema.json), [tools](contracts/tools.json).
