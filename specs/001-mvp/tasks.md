# Índice de tarefas 001

Todas as tarefas de implementação estão pendentes. Execute os checklists locais, na sequência do [catálogo](README.md). Este arquivo não duplica checkboxes.

| Prefixo estável | Checklist |
|---|---|
| M01-T | [Fundação](01-foundation/tasks.md) |
| M02-T | [Workspace](02-workspace/tasks.md) |
| M03-T | [Consulta](03-query/tasks.md) |
| M04-T | [Orçamento](04-budget/tasks.md) |
| M05-T | [Entregas](05-delivery/tasks.md) |
| M06-T | [Interfaces](06-interfaces/tasks.md) |
| M07-T | [Evidência](07-evidence/tasks.md) |

## Migração da lista anterior

T001–T052 descreviam o plano monolítico na base `2d6a526`; não representam trabalho realizado. O mapeamento preserva a localização das intenções, não equivalência automática de comportamento.

| IDs anteriores | Destino |
|---|---|
| T001–T004, T006, T009, T011–T013, T016 | M01, com CLI adiada para M06 |
| T005 | Retirada como bloqueio: consumidor explícito é decisão normativa; experimento de cliente em M06 |
| T007, T014, T018, T020, T022, T023 | M02 |
| T010, T017, T021, T024, T025, T036, T037 | M03 |
| T008, T015, T027–T031, T047, T048 | M04 e medição M07; lint customizado substituído por testes de bytes |
| T032–T035 | M05 |
| T019, T026, T045, T046 | M06 |
| T038–T044, T050–T052 | M07; publicação não é automática |
| T049 | Fora do MVP: calibração remota exige spec própria e opt-in |

## Definition of done

Uma tarefa requer aceitação demonstrada, checks pertinentes, revisão do diff, FR citados e limites explícitos. Uma entrega exige todos os cenários relevantes e integração real. Nunca marcar `[x]` por escrever documentação ou criar stub.

O catálogo atribui os FR às entregas; cada tarefa local cita seus FR. Mudança no contrato atualiza exemplos e consumidores no mesmo PR. Falhas fora do escopo são registradas com evidência, sem ampliar silenciosamente a tarefa.
