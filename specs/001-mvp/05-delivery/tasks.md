# Tarefas M05

- [ ] M05-T01 Testar namespace, argumentos normalizados, alias, versão e threshold; implementar chaves e lookup sem suprimir consumidor omitido — FR-017, FR-018, FR-021.
- [ ] M05-T02 Testar descriptor, fragment token e expansão sob edição/deny; implementar fresh/expand tipado — FR-019, FR-020.
- [ ] M05-T03 Testar TTL/contador/capacidade e concorrência com relógio controlado; implementar histórico limitado — FR-022.
- [ ] M05-T04 Injetar falha de escrita/cancelamento e cortes; implementar prepare/commit sem registrar valores ausentes — FR-017, FR-038.
- [ ] M05-T05 Integrar com o transporte mínimo validado em M01-T06 e comprovar a fronteira de escrita; manter crumbs desativados se não for possível confirmá-la — FR-018, FR-038.

Aceite: G2 e testes de falha via adaptador real; não alegar isolamento entre contextos que usam deliberadamente o mesmo consumer.
