# Research 001: decisões técnicas

> Registro histórico: R1–R10 refletem o desenho inicial. R11–R15 abaixo substituem explicitamente escolhas conflitantes; contratos atuais prevalecem. Nada aqui comprova benchmark ou compatibilidade de runtime.

Cada decisão registra **o que** foi escolhido, **por quê** e **o que foi descartado**. Mudanças futuras devem adicionar uma nova entrada que referencia a anterior, sem apagar o histórico.

---

## R1. Linguagem de consulta

- **Decisão:** um **subconjunto de GraphQL**, só com queries: seleção de campos, argumentos, aliases, fragments e as diretivas `@budget`, `@brief` e `@include`/`@skip`. Sem mutations e sem subscriptions.
- **Por quê:** os modelos já foram treinados com muito GraphQL e escrevem bem nessa sintaxe. A seleção de campos é a essência do produto. O schema é autodescritivo (alimenta `morsel_schema`), e a sintaxe tem gramática formal, ferramentas e validação maduras.
- **Alternativas descartadas:**
  - *JSONPath/JMESPath:* bom para projeção, ruim para atravessar relações (`symbol → callers → file`) e sem schema.
  - *DSL própria:* custo de aprendizado para modelos e humanos, sem ferramentas.
  - *SQL:* expressivo demais e convida a consultas caras e difíceis de orçar.

## R2. Parser e validação

- **Decisão:** `github.com/vektah/gqlparser/v2` para parse e validação contra o SDL, com **executor próprio**.
- **Por quê:** precisamos de uma passagem de **análise de custo antes da execução** e de um envelope customizado. Executores prontos (graphql-go, gqlgen) assumem servidor HTTP e resolvers convencionais, e dificultam podar a árvore pelo orçamento.
- **Alternativas descartadas:** `graphql-go/graphql` (executor acoplado), `gqlgen` (gera código para servidor de API, que não é o nosso caso).

## R3. SDK MCP

- **Decisão:** SDK oficial em Go, `github.com/modelcontextprotocol/go-sdk`, com transporte **stdio** no MVP (HTTP fica para a spec 007).
- **Por quê:** é mantido junto da especificação e reduz o risco de divergência de protocolo.
- **Alternativa:** `mark3labs/mcp-go` (popular e maduro). Fica como plano B caso falte alguma funcionalidade no SDK oficial.
- **Ação:** fixar a versão no `go.mod` e cobrir com testes de contrato (T012).

## R4. Extração de símbolos Go

- **Decisão:** usar **`go/parser` + `go/ast` + `go/token`** da biblioteca padrão. `callers` e `callees` são resolvidos **por nome** dentro do módulo e marcados com `approx: true`.
- **Por quê:** não exige cgo, não exige o toolchain Go instalado na máquina do usuário e é rápido. Atende ao princípio V da constituição.
- **Alternativas descartadas no MVP:**
  - *`golang.org/x/tools/go/packages` + type-checking:* resolução exata, mas exige o toolchain e o build do módulo, e é lento em repositórios grandes. **Candidato a modo opcional** (`--precise`) numa spec futura.
  - *tree-sitter:* multilinguagem, mas exige cgo. Fica para a spec 005, isolado atrás de uma build tag.
  - *gopls via LSP:* processo externo e mais pesado. Pode ser útil no futuro para outras linguagens.

## R5. Estimativa de tokens

- **Decisão:** a interface `Tokenizer` é plugável. O padrão é **heurístico e calibrado**: `tokens = ceil(len(bytes) / ratio[kind])`, com `ratio` por tipo de conteúdo (código Go, Markdown, JSON e texto), calibrado offline contra a referência.
- **Referência para calibração e para o SC-002:** a **API de contagem de tokens do provedor** (por exemplo, o endpoint de contagem da Anthropic), usada **somente** pelo comando `morsel calibrate`, de forma opcional e com a chave do próprio usuário. Os coeficientes padrão, já calibrados, vêm embutidos no binário.
- **Por quê:** os tokenizers variam entre modelos, e uma estimativa de ±15% basta para fazer orçamento. Assim não há dependência de rede no caminho quente (princípio III).
- **Alternativas descartadas:** `tiktoken-go` como padrão. É preciso para modelos da OpenAI, mas não para os demais, e aumenta o binário com as tabelas BPE. Pode ser oferecido como tokenizer opcional.

## R6. Cache normalizado (pantry)

- **Decisão:** cache **em memória** com chave `EntityID@Version` e despejo LRU por tamanho em bytes. A deduplicação de leituras concorrentes usa `golang.org/x/sync/singleflight`.
- **Por quê:** o MVP é um processo por sessão, e persistência fica para a spec 003.
- **Alternativas para a spec 003:** `go.etcd.io/bbolt` (KV embutido, sem cgo) ou `modernc.org/sqlite` (SQLite sem cgo).

## R7. Formato de saída

- **Decisão:** **JSON compacto** (sem espaços), com chaves curtas e em ordem estável, e campos nulos omitidos.
- **Por quê:** é universal, todos os modelos leem bem, e com ordem estável a resposta fica determinística (princípio VI).
- **Alternativas:** TOON ou YAML enxuto. Podem economizar 10–30% em payloads tabulares, mas é preciso medir antes. Ficam como opção futura (`format: "toon"`) **depois** do benchmark.

## R8. Identidade e versão de entidades

- **Decisão:**
  - `EntityID` é textual e legível: `file:internal/orders/service.go`, `sym:go:internal/orders.CreateOrder` e `sym:go:internal/orders.(*Service).Create`.
  - `Version` são os **8 primeiros caracteres hex do xxhash64** do conteúdo do arquivo. Símbolos herdam a versão do arquivo que os contém.
- **Por quê:** IDs legíveis ajudam o agente a raciocinar e a citar. Versões por conteúdo (e não por mtime) são estáveis entre clones e máquinas.
- **Dependência:** `github.com/cespare/xxhash/v2` (pura Go e pequena).

## R9. Harness de benchmark

- **Decisão:** usar tarefas declarativas em YAML (`bench/tasks/*.yaml`) sobre um **repositório fixture fixado por commit**. A execução usa o agente em modo não interativo (inicialmente Claude Code em modo print, com saída JSON contendo uso e custo), em duas configurações: **A** com ferramentas nativas e **B** com o Morsel. O sucesso é medido por um **comando verificador** (por exemplo, `go test ./...` ou um script) e não por julgamento de LLM.
- **Por quê:** a medição é reproduzível, barata de rodar e o critério de sucesso é objetivo.
- **Cuidados:** N ≥ 5 execuções por braço, ordem alternada, mesmo modelo e mesma versão do agente. O relatório traz a mediana e o intervalo.
- **Alternativas:** SWE-bench completo. Tem mais credibilidade, mas é caro e lento. Fica como meta para a v0.4.

## R10. Configuração

- **Decisão:** `morsel.toml`, com expansão de variáveis de ambiente (`${VAR}`), via `github.com/BurntSushi/toml`.
- **Por quê:** TOML é legível, comum no ecossistema e não tem as ambiguidades do YAML.


## R11. Revisão de consistência e custo (substitui R5 e parte de R7)

- Decisão: `cost.est/act/budget/meter`; o medidor padrão é heurístico e offline. `act` mede o texto final segundo esse medidor, sem alegar contagem ou custo do provedor.
- Motivo: heurística não pode garantir teto de tokens para modelos desconhecidos. Wrapper MCP, discovery e histórico têm custos separados.
- Calibração remota foi retirada da v0.1. Corpus versionado com contagem de referência conhecida é gate para anunciar SC-002. Nenhum coeficiente é chamado de calibrado antes disso.
- `cost.saved` sai do envelope v1 e permanece nas estatísticas, evitando uma segunda autorreferência numérica. Finalização e limites estão em `contracts/protocol.md` e M04. A ordem de JSON Schema não determina ordem de JSON; o protocolo a define.

## R12. Identidade, frescor e consumidores (substitui R8)

- SHA-256 completo da stdlib para versões; elimina dependência xxhash e prefixo de 32 bits. Identidade de símbolo inclui arquivo, kind e receptor/nome normalizados.
- Chave de fragmento inclui argumentos efetivos. Crumbs exigem consumidor explícito e conexão; sem consumidor não há supressão. Evita depender de comportamento específico de subagentes.
- Snapshot por conteúdo; `mtime+size` não prova igualdade. Índice com erro sintático não conserva símbolos antigos como atuais.
- Tradeoff: hashing e descoberta completos podem custar latência. Medir esse custo na M07 antes de otimizar a garantia.

## R13. Fronteiras e dependências (revisa R2, R3, R6 e R10)

- Manter parser GraphQL e SDK MCP como escolhas, fixando versões na M01. Testar API concreta antes de congelar mínimo Go e conjunto de protocolos.
- Um pacote de contratos no diretório canônico permite embed sem cópias. Planner/executor ficam em query; fontes locais ficam em workspace até haver motivo real de extração.
- TOML, doublestar, gitignore e singleflight podem justificar dependências pontuais; avaliar licenças, manutenção e semântica. Não implementar gitignore parcial silenciosamente. Não escolher biblioteca por lista aspiracional.
- Sem framework DI, registry de plugins ou camadas genéricas. CLI simples primeiro. Persistência de contadores é distinta de cache de conteúdo.

## R14. Benchmark e escopo de rede (substitui a aceitação fraca de R9)

- Runner externo opt-in, fixtures sem segredos e verifier independente. Fixar agente, modelo, tokens de referência, prompt e versão Morsel.
- Teste que apenas detecta uma palavra não comprova entendimento. Tarefas de explicação exigem rubrica previamente fixada e revisão cega; correção exige teste de regressão não exposto ao agente.
- Metadados locais de stats não são economia faturada. Estimativa de baseline e experimento com uso de provedor são métricas separadas.
- N pequeno é piloto. Incerteza inconclusiva bloqueia alegação H1 e avanço de escopo; não se excluem fracassos do cálculo.

## R15. Fontes primárias verificadas em 2026-11-23

- [Go module layout](https://go.dev/doc/modules/layout): `cmd` e `internal` para comandos e implementação privada.
- [os.Root](https://go.dev/blog/osroot), [API e limites](https://pkg.go.dev/os#Root): confinamento resistente a traversal; não cobre todos os riscos de filesystem.
- [SDK MCP Go](https://github.com/modelcontextprotocol/go-sdk), [stdio 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25/basic/transports): stdout é exclusivamente protocolo; pin e testes reais serão feitos na implementação.
- [GraphQL September 2025](https://spec.graphql.org/September2025/): seleção não vazia, variáveis, validação, fragments e interfaces. O Morsel usa essa linguagem com perfil próprio de projeção; não promete executor GraphQL completo.

Essas fontes fundamentam decisões, não substituem validação das bibliotecas fixadas ou do produto.
