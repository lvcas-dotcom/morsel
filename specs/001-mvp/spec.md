# Feature Spec 001: MVP "first bite" (v0.1)

**Status:** Especificado; implementação pendente · **Criada em:** 2026-11-23 · **Constituição:** v2.0.0

> Esta spec descreve **o quê** e **por quê**, incluindo os limites do contrato público. As decisões técnicas e algoritmos ficam em `research.md` e `plan.md`.

## Resumo

Permitir que um agente de IA consulte **arquivos e símbolos de código Go** de um repositório local pedindo **apenas os campos de que precisa**, com **custo em tokens visível e orçamento respeitado**, e **sem receber de novo conteúdo confirmado para o mesmo consumidor explícito**. Inclui também a medição para validar a hipótese H1 ([VISION.md §7](../../docs/VISION.md)).

## Escopo

**Dentro:** fonte de arquivos locais; símbolos Go (funções, métodos, tipos, constantes, variáveis); consultas com seleção de campos; orçamento de tokens; crumbs e expansão; descoberta do schema; estatísticas da sessão; comando de inicialização; benchmark A/B mínimo.

**Fora (specs futuras):** servidores MCP upstream (002), cache persistente (003), Postgres (004), outras linguagens (005), recipes (006), daemon compartilhado (007), qualquer escrita em fontes.

---

## Histórias de usuário

### US1: Consultar só o necessário (P1) 🎯 MVP

**Como** agente trabalhando num repositório, **quero** pedir partes específicas de arquivos e símbolos (assinatura, doc, corpo, chamadores, intervalo de linhas) **para** não carregar arquivos inteiros quando preciso de um trecho.

**Teste independente:** com o Morsel configurado num repositório Go, uma consulta pela assinatura de uma função devolve só a assinatura, com custo menor que o do arquivo inteiro.

**Cenários de aceitação**

1. **Dado** um repositório com `internal/orders/service.go` contendo `func CreateOrder(...)`, **quando** o agente consulta `symbol(name:"CreateOrder"){ signature }`, **então** a resposta contém apenas a assinatura e o custo reportado é menor que o custo do arquivo completo.
2. **Dado** um arquivo de 2.000 linhas, **quando** o agente consulta `file(path:...){ lines(from:100, to:140) }`, **então** recebe exatamente essas 41 linhas.
3. **Dado** um nome de símbolo que existe em dois pacotes, **quando** o agente consulta sem filtro de pacote, **então** recebe ambos, apenas com os campos selecionados; pacote e arquivo só aparecem se pedidos.
4. **Dado** um padrão `files(glob:"internal/**/*_test.go", first:10){ items { path tokens } next }`, **quando** é executado, **então** recebe até 10 caminhos com o custo em tokens de cada um, em ordem estável.

### US2: Orçamento de tokens (plate) (P1) 🎯 MVP

**Como** agente (ou como dev configurando o agente), **quero** saber quanto uma resposta vai custar e ter um teto **para** nunca estourar o contexto por acidente.

**Teste independente:** uma consulta que pediria 20 mil tokens, com orçamento de 4 mil, volta dentro de 4 mil, indicando o que foi cortado e como continuar.

**Cenários de aceitação**

1. **Dado** qualquer consulta, **quando** ela é respondida, **então** o envelope contém `cost.est`, `cost.act`, `cost.budget` e `cost.meter`; o custo é local, conforme o medidor declarado.
2. **Dado** uma consulta cuja estimativa excede o orçamento, **quando** é executada, **então** a resposta respeita o orçamento, lista os campos cortados em `truncated` (com um cursor ou instrução para continuar) e nunca excede `cost.budget`.
3. **Dado** uma consulta que não cabe no orçamento nem com cortes (por exemplo, a seleção mínima indivisível excede), **quando** é executada, **então** o agente recebe um erro `over_budget` e, quando couber, breakdown limitado por campo; o erro mínimo também respeita o orçamento.
4. **Dado** `@budget(tokens: N)` na consulta, **quando** é executada, **então** N substitui o orçamento padrão, respeitando o teto máximo configurado.

### US3: Não repetir o que já foi servido (crumbs) (P2)

**Como** agente em uma sessão longa, **quero** que conteúdo idêntico que já recebi venha como referência curta **para** reduzir repetição no contexto; economia faturada depende do provedor e é medida separadamente.

**Teste independente:** a mesma consulta com consumidor explícito executada duas vezes na mesma conexão tem a segunda resposta substancialmente menor, com crumbs no lugar do conteúdo.

**Cenários de aceitação**

1. **Dado** que o agente já recebeu o `body` de `CreateOrder` (versão v1) nesta conexão com consumer explícito, **quando** o mesmo consumer consulta o mesmo `body` de novo e o arquivo não mudou, **então** recebe um crumb (ID, versão e descritor de uma linha) em vez do corpo.
2. **Dado** que o arquivo mudou desde a última entrega, **quando** o agente consulta de novo, **então** recebe o conteúdo novo (a versão mudou, então não há crumb).
3. **Dado** um crumb, **quando** o agente chama `morsel_expand` com o ID dele, **então** recebe o conteúdo integral, com seleção de campos opcional.
4. **Dado** `fresh: true` numa consulta, **quando** ela é executada, **então** nenhum crumb é usado.
5. **Dado** dois consumidores distintos (por exemplo, dois subagentes identificados), **quando** cada um pede a mesma entidade pela primeira vez, **então** cada um recebe o conteúdo integral (crumbs são **por consumidor**), mas a leitura na fonte acontece uma vez só.

### US4: Descobrir o grafo sem pagar caro (P2)

**Como** agente, **quero** descobrir quais tipos, campos e argumentos existem **para** montar bites corretas sem carregar um schema enorme.

**Cenários de aceitação**

1. **Dado** `morsel_schema` sem argumentos, **quando** é chamado, **então** retorna um resumo compacto das raízes de consulta e dos tipos (em até 600 tokens no MVP).
2. **Dado** `morsel_schema(search: "callers")`, **quando** é chamado, **então** retorna apenas os tipos e campos relevantes, com o caminho a partir da raiz.
3. **Dado** uma bite inválida (campo inexistente), **quando** é executada, **então** o erro aponta o campo e sugere os nomes válidos mais próximos.

### US5: Ver a economia e provar a tese (P3)

**Como** dev, **quero** ver quanto a sessão economizou e rodar um benchmark A/B **para** confiar (ou desconfiar) do Morsel com números.

**Cenários de aceitação**

1. **Dado** uma sessão ativa ou encerrada, **quando** executo `morsel stats`, **então** vejo os tokens servidos, os tokens que leituras ingênuas teriam custado, a economia estimada e o detalhamento por tipo de entidade, com o rótulo explícito de "estimativa".
2. **Dado** o diretório `bench/` com tarefas definidas, **quando** executo `bench/run` (runner externo opt-in), **então** cada tarefa roda N vezes com e sem Morsel, e o relatório mostra os tokens de entrada, o custo, a taxa de sucesso e o intervalo de variação.

### US6: Começar em 5 minutos (P3)

**Como** dev, **quero** `morsel init` **para** configurar o projeto e ensinar o agente a usar o Morsel.

**Cenários de aceitação**

1. **Dado** um repositório sem configuração, **quando** executo `morsel init`, **então** é criado um `morsel.toml` com padrões seguros e é impresso um snippet de instruções; gravação em `AGENTS.md`/`CLAUDE.md` exige destino explícito, preserva conteúdo e é idempotente.
2. **Dado** o snippet aplicado explicitamente pelo usuário, **quando** o agente recebe uma tarefa no repositório, **então** ele tem as instruções para preferir `morsel_query` à leitura de arquivos inteiros.

---

## Requisitos funcionais

### Consulta (bites)
- **FR-001** O sistema DEVE aceitar consultas com seleção de campos sobre um grafo tipado, contendo apenas leitura.
- **FR-002** O sistema DEVE expor as raízes `file`, `files`, `symbol`, `symbols` e `ref` (ver `contracts/schema.graphql`).
- **FR-003** O sistema DEVE validar cada consulta contra o schema antes de executar e, em caso de erro, retornar a localização e sugestões.
- **FR-004** O sistema DEVE retornar somente campos selecionados, sem extras em data. Cortes/crumbs seguem o perfil explícito do protocolo; null selecionado não é omitido.
- **FR-005** Listas pagináveis DEVEM ter limite padrão (`first`) e teto configurável. Listas sem paginação DEVEM ter teto de trabalho explícito e erro ao excedê-lo, sem truncamento silencioso. Toda lista possui ordenação estável documentada.
- **FR-006** O sistema DEVE suportar intervalos de linhas em arquivos e o campo `outline` (lista de símbolos de um arquivo, sem corpos).

### Símbolos Go
- **FR-007** O sistema DEVE indexar funções, métodos (com receptor), tipos, constantes e variáveis de pacote dos arquivos `.go` dentro da raiz.
- **FR-008** Para cada símbolo, DEVEM estar disponíveis `name`, `kind`, `package`, `file`, `line`, `signature`, `doc` e `body`.
- **FR-009** `callers` e `callees` DEVEM estar disponíveis. Quando o resultado for aproximado (resolução por nome), a resposta DEVE marcar `approx: true`.
- **FR-010** O índice DEVE refletir mudanças em arquivos na próxima consulta, sem reiniciar o servidor.

### Custo e orçamento
- **FR-011** Toda resposta de consulta/expansão DEVE conter `cost.est`, `cost.act`, `cost.budget` e `cost.meter`. O teto vale para o JSON textual final no medidor local declarado; não garante tokens ou preço do provedor.
- **FR-012** A estimativa DEVE preceder a projeção da resposta e usar metadados disponíveis. A captura/versionamento e a indexação fria podem exigir leitura prévia, contabilizada como trabalho da consulta.
- **FR-013** O sistema NUNCA DEVE retornar um payload com `cost.act > cost.budget`.
- **FR-014** Quando houver cortes, a resposta DEVE listar em `truncated` cada campo cortado, o motivo e como continuar (cursor ou bite sugerida).
- **FR-015** O orçamento DEVE ser configurável por padrão, por consulta (`@budget`) e com teto máximo.
- **FR-016** A contagem de tokens DEVE usar um estimador plugável, com um padrão que não depende de rede.

### Crumbs e expansão
- **FR-017** O sistema DEVE manter por conexão e consumidor explícito o registro de valores completos entregues: ID, versão, campo e argumentos normalizados. Campo cortado ou ausente nunca conta como entregue.
- **FR-018** Uma repetição elegível DEVE virar crumb somente se custar menos que o valor completo, não tiver expirado e `fresh` for falso; sem consumidor explícito o sistema não suprime valores.
- **FR-019** Um crumb DEVE conter token de fragmento com identidade da entidade/campo/argumentos, versão e descritor de no máximo uma linha, conforme protocolo.
- **FR-020** `morsel_expand` DEVE recuperar o campo de um token de fragmento ou a projeção explicitamente selecionada de uma entidade, com fresh e autorização atual. ID de entidade exige select; registrar somente entrega completa confirmada.
- **FR-021** Crumbs DEVEM exigir identificador explícito de consumidor, isolado pelo namespace da conexão. Sem identificador, leituras e cache funcionam normalmente, mas não há supressão por histórico. Clientes DEVEM separar consumidores que não compartilham contexto.
- **FR-022** O registro de entregas DEVE expirar conforme a configuração (por número de consultas e por tempo), para tolerar a compactação de contexto do agente.

### Leitura deduplicada
- **FR-023** Materializações concorrentes da mesma entidade e versão DEVEM compartilhar uma leitura após autorização. Captura/revalidação para descobrir a versão não integra essa contagem; isso deve aparecer nas métricas.
- **FR-024** Entidades lidas DEVEM ser mantidas num cache normalizado em memória, com chave que inclui raiz, política, ID e versão, limitado por capacidade; eviction permite releitura.

### Segurança
- **FR-025** O sistema DEVE recusar caminhos fora da raiz configurada, inclusive via symlink.
- **FR-026** O sistema DEVE negar por padrão arquivos sensíveis (lista na configuração padrão) e respeitar `.gitignore`.
- **FR-027** Arquivos binários DEVEM ser identificados e nunca ter o conteúdo servido. Apenas metadados.

### Ferramentas MCP
- **FR-028** O servidor DEVE expor exatamente três ferramentas: `morsel_query`, `morsel_schema` e `morsel_expand` (ver `contracts/mcp-tools.md`).
- **FR-029** Respostas DEVEM ser determinísticas para entrada e estado completo iguais, incluindo entregas, medidor e expiração; não significa igualdade entre primeira e segunda consulta.

### Observabilidade e CLI
- **FR-030** O sistema DEVE registrar, por sessão, os tokens servidos e os tokens do baseline ingênuo, conforme a definição na spec M07.
- **FR-031** `morsel stats` DEVE exibir resumo de sessão por ID ou da mais recente, com acesso a sessões recentes e sem presumir sessão MCP compartilhada com a CLI.
- **FR-032** `morsel init` DEVE criar configuração sem sobrescrever, imprimir snippet e só gravar instruções com destino explícito, com bloco idempotente e preservação de conteúdo.
- **FR-033** `bench/run` (runner externo opt-in) DEVE executar tarefas A/B e gerar um relatório em Markdown e JSON.
- **FR-034** `morsel query '<bite>'` DEVE executar uma bite pela linha de comando, para depuração.

### Invariantes de implementação
- **FR-035** Toda execução DEVE ter limites independentes de entrada, profundidade, campos expandidos, trabalho, memória e tempo; deve aceitar cancelamento.
- **FR-036** IDs DEVEM distinguir declarações em arquivos distintos; versões DEVEM derivar integralmente dos bytes capturados, sem depender apenas de timestamp e tamanho.
- **FR-037** Paginação DEVE usar cursor validado, vinculado à seleção, snapshot e política; cursor incompatível não pode continuar silenciosamente.
- **FR-038** O histórico de entregas DEVE ser efetivado somente depois de escrita bem-sucedida do resultado final; falhas não podem suprimir futuras leituras.
- **FR-039** As definições das ferramentas e exemplos DEVEM ter fonte canônica verificável e compatibilidade explícita com o perfil de projeção.
- **FR-040** O projeto DEVE fornecer licença, contribuição, política de segurança, checks reproduzíveis e critérios explícitos de release.
- **FR-041** Cache, entregas, cursores e métricas DEVEM ter limites e retenção definidos; métricas persistidas não podem conter fontes, caminhos, queries ou segredos.
- **FR-042** O benchmark DEVE fixar entradas, versões e verificadores independentes; falhas, uso ausente e incerteza devem constar do resultado sem fabricar economia.

---

## Entidades-chave

- **Entity:** qualquer coisa endereçável no grafo (arquivo, símbolo). Tem `id` estável, `version` (derivada do conteúdo) e `kind`.
- **Bite:** consulta com seleção de campos e orçamento opcional.
- **Plate:** orçamento de tokens efetivo de uma bite.
- **Crumb:** referência a uma entrega anterior (`id@version` + descritor).
- **Consumer:** contexto explicitamente identificado pelo cliente e isolado por conexão. Sem identificador não há supressão por crumbs.
- **Ledger:** registro, por sessão, de tokens servidos e do baseline.

## Casos de borda

- Arquivo >1 MiB e dentro de `max_file_bytes`: projeção e leitura em linhas continuam disponíveis; resposta obedece ao orçamento. Acima do limite retorna `limit` sem ler todo o arquivo.
- Gerado: `generated: true`; não se remove corpo por ser gerado. Somente seleção explícita, `@brief`, limites e orçamento reduzem conteúdo.
- Erro de sintaxe Go: arquivo ainda pode ser lido como texto, mas seus símbolos não são servidos a partir de índice anterior. Retorna `index_unavailable` na resolução afetada.
- Arquivo removido: `not_found`; crumb não concede acesso. Mudança durante snapshot: `source_changed` recuperável.
- `{}` é inválido na gramática. `{ __typename }` é válido. Documento vazio é `invalid_query`.
- Não UTF-8, arquivo binário ou especial: não servir conteúdo. Binários regulares podem expor metadados autorizados; arquivos especiais são negados.
- Mesmo tamanho e timestamp com bytes diferentes: versão nova na próxima captura. Renomear invalida ID/cursor anterior.
- Mesmo nome sob build tags: entidades distintas por arquivo. Análise sintática abrange todos os `.go` permitidos; não promete respeitar o build ativo.

## Critérios de sucesso

- **SC-001** Meta, ainda não validada: p95 <50 ms em corpus de 5 mil arquivos, máquina, tamanho e tipos de query fixados. Medir captura/revalidação no total, separar caminhos frio/aquecido e não excluir trabalho para atingir a meta.
- **SC-002** Meta: erro da heurística em ±15% (p90) em corpus público fixado, contra tokenizer de referência identificado com versão. Até existir corpus/calibração, não anunciar essa precisão.
- **SC-003** Instalação até primeira bite em <5 minutos, observada em máquina limpa com release real.
- **SC-004** Binário sem cgo, <25 MB por alvo publicado; estático onde aplicável, sem prometer formato ELF estático em todos os sistemas.
- **SC-005** H1: ≥30% menos tokens de entrada, com sucesso não inferior dentro de margem predefinida. Abaixo de 20% ou perda >5 p.p. exige rever tese. Intervalo inconclusivo não autoriza anunciar H1 como comprovada.

## Divisão e decisões

As sete specs do [catálogo](README.md) detalham requisitos, aceitação, plano e tarefas. Contratos em [protocol.md](contracts/protocol.md) resolvem precedência de orçamento, identidade, cursores e perfil GraphQL.

Não há `[NEEDS CLARIFICATION]` bloqueando implementação: consumidor explícito é decisão conservadora e independente do cliente. Compatibilidade real com cada agente é um gate experimental da M06, não suposição de arquitetura.
