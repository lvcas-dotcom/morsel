# Plano M02

`internal/workspace` concentra política, snapshot e AST, em arquivos por responsabilidade. Começar pela fatia de arquivo, sem interface genérica de fontes. `query` depende de operações estreitas de leitura/projeção; tipos não importam GraphQL.

Captura usa descritor confinado, leitura limitada, hash e checagens de mudança. Diretórios enumerados via raiz; nomes são normalizados em `/` para IDs. Não seguir symlinks no MVP simplifica aliases de política. Gitignore deve cobrir aninhamento, negação, diretórios e escapes com fixtures; escolher biblioteca por fidelidade, sem shell git no runtime.

Manifesto associa caminho → versão. Consultas que enumeram símbolos/relacionamentos capturam o manifesto permitido completo, com limites, e não só arquivos já indexados. Caso o conjunto mude durante captura, falhar `source_changed`; não repetir indefinidamente. Custo de descoberta faz parte da latência.

Parser Go usa stdlib, sem type-check/toolchain externo. Qualificar método por receptor normalizado e arquivo. Símbolos compartilham snapshot imutável por offsets; AST pode ser descartada após extração. Callers têm aproximação de nome documentada, ordenação por ID, nunca filtro implícito de build ativo.

`internal/cache` mantém bytes e pins em uso. Dados retidos para leitores e índice contam no orçamento de memória; LRU sozinho não basta. Usar contador de leituras real e filesystem temporário nos testes; testar cancelamento/eviction com race detector.
