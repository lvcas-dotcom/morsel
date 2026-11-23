# Feature Spec 001: MVP "first bite" (v0.1)

**Status:** Draft · **Criada em:** 2026-11-23 · **Constituição:** v1.0.0

> Esta spec descreve **o quê** e **por quê**. Nenhuma decisão de tecnologia aparece aqui; elas ficam em `research.md` e `plan.md`.

## Resumo

Permitir que um agente de IA consulte **arquivos e símbolos de código Go** de um repositório local pedindo **apenas os campos de que precisa**, com **custo em tokens visível e orçamento respeitado**, e **sem receber de novo o que já recebeu**. Inclui também a medição para validar a hipótese H1 ([VISION.md §7](../../docs/VISION.md)).

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
3. **Dado** um nome de símbolo que existe em dois pacotes, **quando** o agente consulta sem filtro de pacote, **então** recebe a lista dos dois com pacote e arquivo, sem os corpos.
4. **Dado** um padrão `files(glob:"internal/**/*_test.go", first:10){ items { path tokens } next }`, **quando** é executado, **então** recebe até 10 caminhos com o custo em tokens de cada um, em ordem estável.

### US2: Orçamento de tokens (plate) (P1) 🎯 MVP

**Como** agente (ou como dev configurando o agente), **quero** saber quanto uma resposta vai custar e ter um teto **para** nunca estourar o contexto por acidente.

**Teste independente:** uma consulta que pediria 20 mil tokens, com orçamento de 4 mil, volta dentro de 4 mil, indicando o que foi cortado e como continuar.

**Cenários de aceitação**

1. **Dado** qualquer consulta, **quando** ela é respondida, **então** o envelope contém `cost.estimated`, `cost.actual` e `cost.budget`.
2. **Dado** uma consulta cuja estimativa excede o orçamento, **quando** é executada, **então** a resposta respeita o orçamento, lista os campos cortados em `truncated` (com um cursor ou instrução para continuar) e nunca excede `cost.budget`.
3. **Dado** uma consulta que não cabe no orçamento nem com cortes (por exemplo, só o envelope mínimo já excede), **quando** é executada, **então** o agente recebe um erro `over_budget` com o custo estimado **por campo**, para poder reformular.
4. **Dado** `@budget(tokens: N)` na consulta, **quando** é executada, **então** N substitui o orçamento padrão, respeitando o teto máximo configurado.

### US3: Não repetir o que já foi servido (crumbs) (P2)

**Como** agente em uma sessão longa, **quero** que conteúdo idêntico que já recebi venha como referência curta **para** não pagar de novo por ele.

**Teste independente:** a mesma consulta executada duas vezes na mesma sessão tem a segunda resposta substancialmente menor, com crumbs no lugar do conteúdo.

**Cenários de aceitação**

1. **Dado** que o agente já recebeu o `body` de `CreateOrder` (versão v1) nesta sessão, **quando** consulta o mesmo `body` de novo e o arquivo não mudou, **então** recebe um crumb (ID, versão e descritor de uma linha) em vez do corpo.
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
2. **Dado** o diretório `bench/` com tarefas definidas, **quando** executo `morsel bench`, **então** cada tarefa roda N vezes com e sem Morsel, e o relatório mostra os tokens de entrada, o custo, a taxa de sucesso e o intervalo de variação.

### US6: Começar em 5 minutos (P3)

**Como** dev, **quero** `morsel init` **para** configurar o projeto e ensinar o agente a usar o Morsel.

**Cenários de aceitação**

1. **Dado** um repositório sem configuração, **quando** executo `morsel init`, **então** é criado um `morsel.toml` com padrões seguros e é gerado um snippet de instruções para o agente (`AGENTS.md` ou `CLAUDE.md`), sem sobrescrever conteúdo existente.
2. **Dado** o snippet aplicado, **quando** o agente recebe uma tarefa no repositório, **então** ele tem as instruções para preferir `morsel_query` à leitura de arquivos inteiros.

---

## Requisitos funcionais

### Consulta (bites)
- **FR-001** O sistema DEVE aceitar consultas com seleção de campos sobre um grafo tipado, contendo apenas leitura.
- **FR-002** O sistema DEVE expor as raízes `file`, `files`, `symbol`, `symbols` e `ref` (ver `contracts/schema.graphql`).
- **FR-003** O sistema DEVE validar cada consulta contra o schema antes de executar e, em caso de erro, retornar a localização e sugestões.
- **FR-004** O sistema DEVE retornar somente os campos selecionados, sem campos extras.
- **FR-005** Listas DEVEM ter um limite padrão (`first`), com o limite máximo configurável, e ordenação estável documentada.
- **FR-006** O sistema DEVE suportar intervalos de linhas em arquivos e o campo `outline` (lista de símbolos de um arquivo, sem corpos).

### Símbolos Go
- **FR-007** O sistema DEVE indexar funções, métodos (com receptor), tipos, constantes e variáveis de pacote dos arquivos `.go` dentro da raiz.
- **FR-008** Para cada símbolo, DEVEM estar disponíveis `name`, `kind`, `package`, `file`, `line`, `signature`, `doc` e `body`.
- **FR-009** `callers` e `callees` DEVEM estar disponíveis. Quando o resultado for aproximado (resolução por nome), a resposta DEVE marcar `approx: true`.
- **FR-010** O índice DEVE refletir mudanças em arquivos na próxima consulta, sem reiniciar o servidor.

### Custo e orçamento
- **FR-011** Toda resposta DEVE conter `cost.estimated`, `cost.actual` e `cost.budget`.
- **FR-012** A estimativa DEVE ser calculada **antes** da materialização do conteúdo, quando a fonte permitir (arquivos e símbolos permitem).
- **FR-013** O sistema NUNCA DEVE retornar um payload com `cost.actual > cost.budget`.
- **FR-014** Quando houver cortes, a resposta DEVE listar em `truncated` cada campo cortado, o motivo e como continuar (cursor ou bite sugerida).
- **FR-015** O orçamento DEVE ser configurável por padrão, por consulta (`@budget`) e com teto máximo.
- **FR-016** A contagem de tokens DEVE usar um estimador plugável, com um padrão que não depende de rede.

### Crumbs e expansão
- **FR-017** O sistema DEVE manter, por consumidor, o registro de quais entidades (ID + versão + campo) já foram entregues.
- **FR-018** Uma entrega repetida de entidade, campo e versão idênticos DEVE virar um crumb, exceto quando `fresh: true`.
- **FR-019** Um crumb DEVE conter o ID da entidade, a versão e um descritor de no máximo 1 linha.
- **FR-020** `morsel_expand(id, select?)` DEVE devolver o conteúdo integral (ou a projeção pedida) e registrar a entrega.
- **FR-021** O consumidor padrão DEVE ser a sessão MCP, e o agente PODE informar um identificador de consumidor explícito.
- **FR-022** O registro de entregas DEVE expirar conforme a configuração (por número de consultas e por tempo), para tolerar a compactação de contexto do agente.

### Leitura deduplicada
- **FR-023** Leituras concorrentes da mesma entidade e versão DEVEM resultar em uma única leitura na fonte.
- **FR-024** Entidades lidas DEVEM ser mantidas num cache normalizado em memória, com chave = ID + versão.

### Segurança
- **FR-025** O sistema DEVE recusar caminhos fora da raiz configurada, inclusive via symlink.
- **FR-026** O sistema DEVE negar por padrão arquivos sensíveis (lista na configuração padrão) e respeitar `.gitignore`.
- **FR-027** Arquivos binários DEVEM ser identificados e nunca ter o conteúdo servido. Apenas metadados.

### Ferramentas MCP
- **FR-028** O servidor DEVE expor exatamente três ferramentas: `morsel_query`, `morsel_schema` e `morsel_expand` (ver `contracts/mcp-tools.md`).
- **FR-029** Respostas DEVEM ser determinísticas: mesma entrada e mesmo estado produzem os mesmos bytes.

### Observabilidade e CLI
- **FR-030** O sistema DEVE registrar, por sessão, os tokens servidos e os tokens do baseline ingênuo, conforme a definição em `plan.md` §7.
- **FR-031** `morsel stats` DEVE exibir o resumo da sessão atual e das sessões recentes.
- **FR-032** `morsel init` DEVE criar a configuração e o snippet de instruções sem sobrescrever conteúdo existente.
- **FR-033** `morsel bench` DEVE executar tarefas A/B e gerar um relatório em Markdown e JSON.
- **FR-034** `morsel query '<bite>'` DEVE executar uma bite pela linha de comando, para depuração.

---

## Entidades-chave

- **Entity:** qualquer coisa endereçável no grafo (arquivo, símbolo). Tem `id` estável, `version` (derivada do conteúdo) e `kind`.
- **Bite:** consulta com seleção de campos e orçamento opcional.
- **Plate:** orçamento de tokens efetivo de uma bite.
- **Crumb:** referência a uma entrega anterior (`id@version` + descritor).
- **Consumer:** quem recebe as respostas (sessão MCP ou ID explícito). Os crumbs são por consumidor.
- **Ledger:** registro, por sessão, de tokens servidos e do baseline.

## Casos de borda

- Arquivo gigante (> 1 MB): o `content` é sempre cortado pelo orçamento, e `outline` e `lines` continuam funcionando.
- Arquivo gerado (`// Code generated ... DO NOT EDIT.`): é marcado com `generated: true`, e o `body` dos símbolos é cortado por padrão.
- Arquivo com erro de sintaxe Go: o índice daquele arquivo usa a última versão válida e marca `stale: true`, ou fica vazio se nunca foi válido.
- Arquivo apagado entre consultas: o crumb correspondente vira inválido e `ref` devolve `not_found`.
- Consulta vazia ou só com `__typename`: resposta válida com o custo do envelope.
- Encoding diferente de UTF-8: o arquivo é tratado como binário, a menos que seja configurado.

## Critérios de sucesso

- **SC-001** Consultas de arquivo ou símbolo com o cache aquecido respondem em **p95 < 50 ms** num repositório de 5 mil arquivos.
- **SC-002** O erro da estimativa de tokens fica dentro de **±15% (p90)** no corpus de calibração, comparado ao tokenizer de referência.
- **SC-003** Instalação até a primeira bite útil em **menos de 5 minutos**, seguindo o README.
- **SC-004** O binário é estático, sem cgo, com **menos de 25 MB**.
- **SC-005** (Hipótese H1, a validar) No benchmark A/B, há **≥ 30% menos tokens de entrada**, sem queda de taxa de sucesso maior que o intervalo de variação. Se o resultado for menor que 20% ou a queda de sucesso for maior que 5 p.p., aciona-se o critério de parada da VISION.

## Pontos em aberto

- **[NEEDS CLARIFICATION]** Subagentes do Claude Code compartilham a mesma sessão MCP do agente principal? Isso define se o FR-021 precisa de um ID de consumidor explícito para funcionar com subagentes. **Ação:** experimento na T005 antes da US3.
- ~~Qual tokenizer de referência usar para o SC-002?~~ **Resolvido em `research.md` R5:** a API de contagem do provedor, usada só na calibração offline.
