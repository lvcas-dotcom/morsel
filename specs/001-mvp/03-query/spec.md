# M03 — Consultas e projeção

Estado: especificado; implementação pendente. Depende da fatia de arquivos M02; conclusão exige índice M02. Requisitos: FR-001, FR-002, FR-003, FR-004, FR-005, FR-006, FR-037.

## Objetivo

Pedir exatamente campos necessários, com sintaxe conhecida e erro útil, sem permitir que a expressividade da consulta cause trabalho ilimitado.

## Requisitos locais

- **QRY-01** Validar sintaxe, schema, operação, variáveis e diretivas antes de ler fontes. Suportar aliases, named/inline fragments, variáveis e include/skip. Rejeitar mutações, subscriptions, introspecção `__schema`/`__type` e diretivas desconhecidas; `__typename` é permitido.
- **QRY-02** Expandir fragments com detecção de ciclos e contabilização de profundidade/campos/aliases. Múltiplas operações exigem `operationName`; coerção de argumentos segue SDL.
- **QRY-03** Somente campos selecionados são emitidos, inclusive em múltiplos símbolos. Valores nulos selecionados permanecem nulos; omitir null globalmente destruiria a distinção entre ausência e corte.
- **QRY-04** `lines` é inclusivo, 1-indexado, exige `1 <= from <= to`; preservar bytes UTF-8/terminadores originais. `to` além do fim usa a última linha; `from` além do fim produz string vazia. Não criar linha extra por newline terminal.
- **QRY-05** `first` positivo e limitado; ordenação de files por path, symbols e relações por ID; busca substring case-sensitive, sem ranking indefinido. `total` é o número de itens permitidos antes da página. Listas sem paginação (symbol, outline, imports) obedecem ao teto de itens de trabalho; excedê-lo produz limit em vez de esconder itens.
- **QRY-06** Cursor é opaco, validado por registro limitado da conexão e vinculado à consulta normalizada, snapshot e política. Seleção/variáveis/limite alterados, estado alterado ou cursor expirado geram `invalid_cursor`.
- **QRY-07** `morsel_schema` é gerado do SDL canônico; visão geral cabe em 600 unidades do medidor local, busca retorna caminhos relevantes, sem inventar SDL parseável se a saída for apenas resumo.

## Aceitação

1. Assinatura sem corpo, intervalo de 41 linhas, outline e dois símbolos homônimos retornam exatamente os campos selecionados.
2. Aliases duplicados incompatíveis, fragment cíclico, variável errada, seleção vazia e operação não selecionada falham antes de I/O.
3. Fragments válidos sobre File/Symbol e `ref` com type conditions funcionam. Não permitir `ref { body }` diretamente na interface Entity.
4. Duas páginas não repetem/perdem itens no mesmo snapshot; edição ou alteração de ignore impede continuar cursor anterior.
5. CRLF, Unicode, arquivo vazio, newline terminal e limites de intervalo têm golden files.
6. Discovery sem argumentos e busca `callers` usam SDL real, ordem estável e custo medido; erro de campo oferece nomes próximos sem expandir resposta ilimitadamente.

## Fora de escopo

GraphQL HTTP, conformidade completa do executor GraphQL, resolvers de banco, busca semântica e plano genérico para fontes futuras.
