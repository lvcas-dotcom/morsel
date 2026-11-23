# Plano M03

Manter parser, plano e executor no pacote `internal/query`, com arquivos separados. Não expor AST de biblioteca a workspace ou delivery. Normalizar campo/argumentos para uma identidade interna; manter response key (alias) separado da identidade semântica.

Gqlparser valida SDL e regras antes da execução. Após seleção da operação e coerção de variáveis, construir plano limitado, preservando a ordem de seleção após merge compatível. Prever custo na M04, sem acesso extra a fonte só por alias.

Result tree representa explicitamente valor, null, corte e erro. O protocolo de projeção permite crumb em folha textual, portanto não encaminhar para cliente como se fosse resposta GraphQL padrão.

Cursores usam token derivado deterministicamente dos dados de paginação e registro na conexão; entrada desconhecida é rejeitada. Hash não é tratado como autorização. Aplicar limites/TTL do registro e invalidar com política/snapshot. Reconexão não promete conservar cursor.

Verificar com parser real: documentos com variáveis/operationName, diretivas, fragments, interfaces, erros e profundidade; fuzz focado em pânico, expansão e limites. Filesystem real nos testes de paginação e mudança de snapshot.
