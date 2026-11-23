# Análise do repositório

Data: 2026-11-23. Base examinada: `2d6a526`. Escopo: documentos versionados, contratos, árvore e histórico local. Não havia implementação, `go.mod`, testes, CI nem releases versionados. Os arquivos locais de ferramentas já existentes não foram alterados. Ferramentas de grafo citadas em `CLAUDE.md` não estão disponíveis nesta sessão; a análise foi feita nas fontes.

## Diagnóstico

O projeto tem uma tese de produto clara, escopo de leitura e uma boa intenção de desenvolvimento por contratos. Seu risco atual está na consistência do desenho, não em qualidade de código executável. Não há evidência runtime de desempenho, segurança operacional ou economia.

| Prioridade | Evidência na base examinada | Consequência | Tratamento nesta revisão |
|---|---|---|---|
| Alta | `specs/spec.md` e `specs/tasks.md` duplicam o MVP | Duas fontes normativas podem divergir | Redirecionamentos para catálogo único |
| Alta | FR-011 usa `estimated/actual`; envelope usa `est/act` | Contratos incompatíveis | Vocabulário unificado |
| Alta | R5 usa heurística, mas `act` é apresentado como custo real | Teto local confundido com limite do provedor | Medidor identificado; garantia limitada ao texto medido localmente |
| Alta | `plan.md` §3 limita guard a três tentativas; custo inclui o próprio `act` | Sem prova de término ou orçamento | Progresso estrito e reserva dos campos numéricos |
| Alta | Chave de crumb não inclui argumentos | `lines(1,10)` pode suprimir `lines(50,60)` | Argumentos normalizados e versão na chave |
| Alta | FR-021 depende da sessão MCP e de experimento com um cliente | Subagentes podem receber referências que nunca viram | Consumidor explícito; omissão devolve conteúdo |
| Alta | Revalidação por `mtime+size` | Edição com mesmo tamanho e timestamp conserva versão antiga | Snapshots por conteúdo e manifestos de busca |
| Alta | R8 usa oito caracteres de hash e símbolo sem arquivo | Colisões de versão e de declarações sob build tags | SHA-256 completo e símbolo qualificado por arquivo |
| Alta | `stale` do índice inválido não existe no SDL | Conteúdo antigo parece atual | Retirar símbolos inválidos e emitir erro explícito |
| Alta | `String` vira crumb; expand aplica seleção concreta sobre interface | Não é resposta GraphQL convencional | Perfil de projeção e expansão tipada explícitos |
| Média | Sem limites de profundidade, aliases, consumidores ou indexação | Orçamento de saída não limita CPU/memória | Limites independentes e cancelamento |
| Média | Cursor sem consulta, política ou snapshot | Paginação mistura versões | Cursor opaco vinculado ao snapshot |
| Média | Embed planejado de `internal/` para `specs/` | `go:embed` não aceita caminhos ascendentes | Pacote Go na pasta canônica dos contratos |
| Média | Meta de 450 tokens cobre só descrições | Discovery subestimado | Medir definições completas separadamente |
| Média | `stats` de outro processo sem contrato de persistência | Sessões ativas e arquivos parciais indefinidos | Contadores atômicos e seleção explícita de sessão |
| Média | Benchmark aceita arquivo com palavra `repository` | Sucesso sem demonstrar entendimento | Verificadores independentes e rubrica cega |
| Média | README mostra `morsel-dev`; origin é `lvcas-dotcom/morsel` | Instalação aponta para módulo não confirmado | Caminho alinhado ao origin; instalação segue planejada |
| Média | Apache-2.0 sem `LICENSE`; sem guias de contribuição e segurança | Base open source incompleta | Materializar licença já declarada, guias e gates |

## Direção recomendada

Construir uma fatia completa de arquivos antes do índice: política segura, projeção, orçamento e stdio. Acrescentar símbolos e depois crumbs. Isso reduz o risco de integrar muitos pacotes sem comportamento utilizável.

Usar monólito modular. Planner e executor permanecem juntos em `query` até haver motivo para separar. Não criar microserviços, SDK público, registry de plugins ou abstração de banco antes de uma segunda fonte real.

O [catálogo do MVP](../specs/001-mvp/README.md) divide a construção em sete specs. A [arquitetura](ARCHITECTURE.md) define dependências e invariantes. Todas as tarefas de implementação permanecem pendentes.

## Limites desta entrega

Foram revisados documentos e contratos. A validação documental verifica links locais, estrutura, IDs, dependências e exemplos. Testes de aplicação, integração MCP, corrida, fuzz, benchmarks, builds e compatibilidade por sistema operacional dependem da implementação e não foram executados. H1 continua em aberto.
