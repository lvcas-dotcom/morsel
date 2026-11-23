# Protocolo de projeção v1

Estado: contrato de design, não implementação. Fontes canônicas: [SDL](schema.graphql), [envelope](envelope.schema.json), [tools](tools.json) e [exemplos](examples.json). Mudar contrato atualiza todos no mesmo PR. Versões de SDK/protocolo MCP são fixadas pela M01/M06.

## 1. Perfil GraphQL

Morsel aceita linguagem de seleção GraphQL, não oferece endpoint GraphQL nem executor de conformidade completa. Query, aliases, fragments, variáveis, type conditions, `@include`, `@skip`, `@budget` e `@brief` compõem o perfil. Mutations, subscriptions, introspecção de schema e outras diretivas são recusadas. `__typename` é permitido; seleção vazia é inválida.

`query`, `variables` e `operationName` selecionam e validam uma operação antes de I/O. Variável ausente/coerção inválida e múltiplas operações sem nome são `invalid_query`. Profundidade/campos expandidos são limitados, mesmo com aliases e fragments reutilizados. Aplicação de `@brief` em campo não textual elegível é erro de validação.

**Desvio explícito do resultado GraphQL:** folhas textuais `File.content`, `File.lines`, `Symbol.signature`, `Symbol.doc` e `Symbol.body` podem retornar crumb em vez de string. Cortes de orçamento podem omitir campos, inclusive `non-null`, desde que constem em `truncated`. Não executar propagação convencional de null para cortes. Clientes não devem validar `data` como resposta GraphQL padrão. A validação de seleção continua usando o SDL; validação de resultado usa envelope + invariantes do perfil.

`null` selecionado e lista vazia são preservados; não omitir globalmente valores nulos/vazios. Omitir `crumbs`, `truncated` e `errors` apenas quando vazios; `data` pode faltar quando não há resultado útil. `crumbs` contém os tokens `$crumb` distintos usados na resposta, por primeira ocorrência.

`outline` não injeta corpo, mas aceita campos de Symbol explicitamente pedidos, incluindo body. Não proibir uma seleção válida silenciosamente. `symbol` não injeta pacote/arquivo: o cliente deve selecioná-los se quiser desambiguar.

## 2. Identidade e versões

- Arquivo: `file:<path>`, caminho relativo à raiz, separador `/`; normalizar segmentos e percent-encode UTF-8 de `%`, `#` e caracteres de controle. Decodificar uma vez e revalidar. ID nunca concede acesso.
- Símbolo: `sym:go:<path>#<kind>:<receiver>:<name>`, com kind minúsculo do SDL, receiver vazio fora de método, receptor normalizado pelo nome do tipo sem `*` e sem parâmetros genéricos. Escapar delimitadores dos componentes. Arquivo faz parte da identidade para distinguir build tags e testes.
- Versão: `sha256:<64 hex minúsculos>` dos bytes integrais do snapshot do arquivo. Símbolos herdam versão do arquivo. Sem timestamp, prefixo truncado ou hash de texto reformatado.
- Fragmento: `frag:<base64url sem padding do JSON canônico>`, JSON com chaves em ordem `entity`, `field`, `args`. Argumentos são coerced/defaulted, chaves lexicais, sem alias ou `after` de outro campo. Token é endereço, nunca credencial. Limitar tamanho a 2 KiB antes de decodificar.

Exemplo de identidade lógica de fragmento: `{"entity":"file:README.md","field":"lines","args":{"from":1,"to":10}}`. Campos sem argumentos usam `args:{}`. Somente texto completo pode ser registrado; prefixo brief não representa entrega integral. Byte offsets/AST sempre correspondem à versão capturada. Symbol.body é a declaração completa nos bytes originais, sem o comentário doc; não é somente o bloco entre chaves. File.tokens estima o arquivo legível inteiro, Symbol.tokens a declaração; binário tem tokens=0 porque seu conteúdo não é servível.

## 3. Consumidores, crumbs e expansão

Sem `consumer`, não há lookup nem registro de histórico de entrega; cache/materialização seguem funcionando. Com consumer explícito, namespace inclui conexão. Cliente atribui IDs diferentes a contextos que não compartilham conhecimento. Não usar consumer como autenticação ou nome de arquivo.

Crumb: `{"$crumb":"frag:…","v":"sha256:…","d":"descritor"}`. Descriptor de uma linha, até 120 caracteres e limitado pelo medidor. Substituir somente se for menor que texto original e atender `min_tokens`. Alias não muda identidade, mas muda caminho dos marcadores. TTL conta desde última entrega completa; referência repetida não renova TTL.

`morsel_expand` aceita ID de entidade ou token de fragmento. Entidade exige `select`, para não haver leitura integral implícita. Fragmento sem select repete o campo/argumentos originais; com select resolve a entidade e valida seleção contra tipo concreto. Expand de entidade equivale conceitualmente a `ref` com inline fragment do tipo concreto, com `fresh:true`. Não concatenar seleção arbitrária diretamente na interface Entity.

Expansão retorna versão atual; versão antiga do crumb é informativa, não pedido para recuperar histórico. Reautorizar sempre, inclusive cache quente. Exclusão retorna `not_found`; erro sintático na resolução de símbolo retorna `index_unavailable`. Resultado de fonte alterada durante captura retorna `source_changed` e pode ser repetido.

Preparar histórico durante resolução; efetivar só valores completos ainda presentes no payload e após escrita confirmada. Duas consultas concorrentes podem ambas servir texto. Reconexão zera namespace de consumidor. `fresh:true` evita supressão e, se consumer existe, confirma nova entrega completa.

## 4. Orçamento e custo

Precedência: argumento da tool/CLI `budget` > diretiva selecionada `@budget` > default 4.000. Intervalo 256–16.000 por padrão; configuração pode reduzir teto, nunca mínimo abaixo do envelope de erro suportado. Valores inválidos são rejeitados antes da execução. `morsel_schema` tem limite independente de 600 unidades, resumo ou busca truncada com indicação textual de refinamento.

`cost.est`: previsão antes da projeção, pode incluir metadados já lidos/indexados. `cost.act`: contagem do JSON textual final, inclusive cost, erros, descriptors e marcadores, no medidor `cost.meter`. `heuristic-v1 = ceil(bytes_UTF8/4)`. Ambos são estimativas de tokens, não uso do provedor. `cost.budget`: teto efetivo no mesmo medidor. `cost.saved` não faz parte do envelope v1; stats calcula a economia estimada após finalizar a resposta.

Limite cobre um único bloco textual de query/expand; não inclui framing JSON-RPC, definição das tools, histórico do cliente nem tokens de raciocínio. Não há dupla representação em structuredContent. Medir discovery completo separadamente; meta de 450 unidades para descrições não é limite total de discovery.

Finalização repete medição com `act` inserido até ponto fixo (M04). A cada redução remover item/folha elegível, desempate por JSON Pointer lexical. Cortes não podem produzir JSON inválido ou texto partido. Escalares não redutíveis levam a erro mínimo se necessário. Marcadores também são limitados; se não couberem todos, descartar `data` e retornar `over_budget` em vez de ocultar cortes.

`truncated.path` é JSON Pointer relativo à raiz do envelope, considerando aliases e índices; caminho aponta para o valor afetado, mesmo se omitido. Razões: `budget`, `brief` ou `limit` (página solicitada). `next` é objeto tipado com tool e argumentos, diretamente executável; nenhum texto que se passe por cursor. Conexões usam `next: Cursor` no próprio data para paginação explícita.

## 5. Paginação e ordenação

Files por path crescente; symbols e relações por ID crescente; substring case-sensitive sem ranking oculto. `first` inteiro positivo, default 20 e máximo 100. `total` conta apenas autorizados antes de paginar. Relações têm `after` e `next`, permitindo continuar sem aumentar limite.

Listas sem paginação (`symbol`, `outline`, `imports`) são completas até `limits.unpaginated_items` (default 1.000); acima disso retornam `limit`, sem omitir itens como se a lista estivesse completa. Outline ordena por linha e depois ID; imports ordena lexicalmente. Isso é limite de trabalho, separado de cortes explicitamente marcados por orçamento.

Cursor vinculado ao snapshot permitido, política e consulta/variáveis/seleção normalizadas, excluindo somente `after`. Consistência exige repetir a consulta original com `after` novo. Budget pode diminuir quantidade efetiva da página sem alterar a identidade solicitada. Cursor é registrado na conexão, limitado/expirável e desconhecido/incompatível retorna `invalid_cursor`. Nenhum cursor evita revalidação da política ou snapshot.

Sem cursores aleatórios no payload: derivar token determinístico dos dados de paginação e registrar no namespace da conexão. Colisão/registro desconhecido é erro, nunca autorização. Hash sozinho não autentica cursor.

## 6. Erros e serialização

Erros de argumentos MCP (objeto inválido, campo extra, budget fora de faixa) são erros de protocolo; não passam pelo envelope e não alegam respeitar um budget rejeitado. Sintaxe GraphQL inválida ou erro de domínio com argumentos aceitos retorna envelope, também dentro do orçamento.

Códigos estáveis: `invalid_query`, `over_budget`, `not_found`, `denied`, `limit`, `source_changed`, `index_unavailable`, `invalid_cursor`, `internal`. Mensagem pública curta, sem stack, conteúdo de arquivo ou caminho absoluto. `errors.at` é JSON Pointer quando houver campo; localização sintática usa `location:{line,column}`. Sugestões/breakdown são opcionais, limitados. Cancelamento segue protocolo do SDK; nunca confirmar entrega cancelada.

MCP `isError:true` quando há erro sem dados úteis; sucesso parcial mantém false com errors/truncated. Um bloco textual, sem prefixos explicativos. SDL descoberto é resumo textual, não envelope.

Ordem de envelope: `data`, `cost`, `crumbs`, `truncated`, `errors`, presentes quando aplicável. Cost: `est`, `act`, `budget`, `meter`. Data segue ordem de seleção após merge de fragments; objetos de argumentos têm chaves lexicais. Marcadores e erros ordenados por path e code/reason, desempate lexical. JSON compacto, UTF-8, escaping definido por golden files. Nulls selecionados são preservados.

Determinismo exige mesmo estado completo: fontes, política, configuração, versões, consumidor, entregas e instante lógico de expiração. Primeira e segunda consulta naturalmente podem produzir bytes distintos. Horários, métricas de duração e IDs aleatórios ficam fora do envelope.
