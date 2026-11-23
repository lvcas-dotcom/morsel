# M02 — Workspace, snapshots e símbolos

Estado: especificado; implementação pendente. Depende de M01. Requisitos: FR-007, FR-008, FR-009, FR-010, FR-023, FR-024, FR-025, FR-026, FR-027, FR-035, FR-036, FR-041.

## Objetivo e escopo

Ler arquivos permitidos e representar símbolos Go a partir de bytes coerentes. Segurança e frescor valem também para cache, descoberta, outline, relações e `ref`.

## Requisitos locais

- **WSP-01** A raiz vem da configuração confiável, nunca de argumento da query. Recusar absolutos, traversal, volumes Windows, symlinks em qualquer componente no MVP e arquivos especiais. Usar `os.Root` no acesso, não só validação lexical.
- **WSP-02** Negação sensível, `.gitignore` e `.git` são aplicados em todos os caminhos antes de cache/indexação. Mudança de política invalida snapshot/cursor/cache. Exceção sensível só por configuração local explícita, nunca por query.
- **WSP-03** Capturar bytes e versão SHA-256 na mesma leitura limitada; offsets de linha, AST e símbolos referem-se a esses bytes. Consultas novas revalidam por conteúdo; timestamp e tamanho iguais não dispensam verificação.
- **WSP-04** IDs seguem o protocolo. Indexar funções, métodos, tipos/interfaces, constantes e variáveis de pacote, incluindo `_test.go` e arquivos sob build tags permitidos. Relações aproximadas vêm com `approx:true`, sem fingir resolução de tipos.
- **WSP-05** Arquivo sintaticamente inválido não fornece símbolos antigos. Exclusão/rename desaparece do manifesto na próxima busca. Busca global e callers/callees revalidam o conjunto de candidatos antes de responder.
- **WSP-06** Cache é LRU por bytes retidos, chave com raiz/política/ID/versão; símbolos retêm referência contabilizada ao buffer, não cópias ocultas. Item maior que capacidade não entra. Singleflight deduplica materialização e não autorização.
- **WSP-07** Limites rejeitam trabalho excessivo com `limit`, sem resposta silenciosamente incompleta. Buffers temporários e trabalho concorrente possuem limite separado do LRU.

## Defaults propostos e verificáveis

Config inválida falha no startup. Valores são limites de trabalho, não promessas de performance.

| Chave | Default |
|---|---|
| `limits.query_bytes` | 65.536 |
| `limits.depth` / `limits.fields` (após fragments e aliases) | 12 / 500 |
| `limits.first_default` / `limits.first_max` | 20 / 100 |
| `limits.unpaginated_items` | 1.000 por lista sem paginação |
| `limits.request_timeout` | 5s |
| `limits.max_file_bytes` | 32 MiB |
| `limits.workspace_files` / `limits.index_bytes` | 50.000 / 512 MiB por captura |
| `limits.concurrent_requests` / `limits.concurrent_reads` | 8 / 4 |
| `limits.inflight_bytes` | 128 MiB, backpressure antes de alocar |
| `cache.max_bytes` | 256 MiB |
| `crumbs.max_consumers` / `crumbs.entries_per_consumer` | 128 / 10.000 |
| `crumbs.ttl` / `crumbs.max_queries` / `crumbs.min_tokens` | 30m / 40 / 30 |
| `limits.cursor_bytes` / `limits.cursor_entries` / `limits.cursor_ttl` | 2 KiB / 1.024 / 10m |
| `stats.retention_days` / `stats.max_sessions` | 7 / 100 |

## Aceitação

1. Traversal codificado, caminho absoluto, arquivo especial, symlink trocado durante leitura e alias para `.env` são recusados sem expor conteúdo ou caminho externo. Rodar casos por SO suportado.
2. Edição de mesmo tamanho com timestamp restaurado muda versão e símbolos. Arquivo apagado, novo e renomeado altera busca global e callers.
3. Syntax error após versão válida produz erro de índice e nunca corpo/posição antigo; texto autorizado continua legível.
4. Declarações em arquivos distintos sob build tags têm IDs distintos; IDs não dependem da ordem do parse nem de caminho absoluto da máquina.
5. N leitores concorrentes da mesma versão compartilham materialização; dois consumidores recebem conteúdo completo. Cancelar um leitor não quebra os outros; cancelar todos libera recursos.
6. Cache esgota capacidade, evicta deterministamente e continua autorizado; alteração de ignore/deny bloqueia também valores aquecidos.

## Limites de confiança

A raiz local é escolhida pelo operador. Hardlinks, mounts, filesystem hostil e processos com o mesmo usuário não são isolados como num sandbox de SO. Para conteúdo não confiável, usar isolamento do sistema. Não anunciar uma garantia que `os.Root` não oferece.
