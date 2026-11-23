# Morsel: Visão

> *Feed your agents morsels, not feasts.*
> Um motor de contexto para agentes de IA, inspirado no **lado cliente** do GraphQL.

> Documento exploratório do desenho inicial. Afirmações de mercado e comparações abaixo não foram auditadas nesta revisão e não são evidência de originalidade, custo ou superioridade. Para comportamento normativo, consulte os contratos e a constituição v2.

Este documento explica **por que** o Morsel existe, **qual tese** ele defende e **o que ele não é**. As decisões de *como* construir ficam em [`specs/`](../specs/).

---

## 1. O problema

Agentes de IA (Claude Code, Codex, Cursor, agentes próprios) gastam a maior parte dos tokens com **contexto**, não com raciocínio. O desperdício tem quatro formas:

| Desperdício | Exemplo | Por que é caro |
|---|---|---|
| **Excesso de dados** | A ferramenta devolve o objeto inteiro (80 KB) quando o agente queria 2 campos | Polui a janela e degrada a qualidade |
| **Repetição** | O mesmo arquivo é lido 4 vezes na mesma sessão | O histórico é recobrado a cada turno; o custo cresce de forma quadrática |
| **Multiplicação** | 3 subagentes leem os mesmos 5 arquivos | Paga-se 3 vezes por trabalho idêntico |
| **Cegueira de custo** | Ninguém sabe o que uma chamada vai custar antes de ela cair no contexto | Estouros de janela e contas imprevisíveis |

Isso não é teórico. O mercado mudou de "qual modelo escolher" para "como mover menos tokens". Relatos de 2026 mostram loops de agente cujo custo cresce mais de 10x acima da estimativa ingênua, e tarefas que custam ~50 mil tokens com um agente passando de centenas de milhares quando divididas entre vários agentes especializados.

## 2. O que já existe (e o que falta)

Usar GraphQL para o agente **pedir só os campos necessários** já é um nicho estabelecido:

- **Apollo MCP Server**: transforma operações GraphQL em ferramentas MCP e oferece busca semântica no schema e minificação.
- **WunderGraph e Grafbase**: defendem GraphQL como camada de API para agentes e podam o schema para caber no contexto.
- **Servidores MCP GraphQL menores** (Anansi e outros): com poucas ferramentas fixas, o agente monta a query.
- **Projeção e compressão**: mcp-distill, mcp-trim, json-mask, e o **mcp-compressor** da Atlassian, que comprime as descrições das ferramentas.
- **PromptQL (Hasura)**: o agente gera um plano de consulta e o executa fora do LLM.

**Todos atacam o lado *servidor*: uma fonte de dados de cada vez.**

O que ninguém trouxe para agentes é o lado **cliente** do ecossistema GraphQL, justamente o que resolveu para front-ends os mesmos problemas que os agentes têm hoje:

| Peça do ecossistema GraphQL | Problema que resolveu no front-end | Problema equivalente no agente |
|---|---|---|
| Seleção de campos | Excesso de dados | Excesso de dados |
| **Cache normalizado** (Apollo Client) | Componentes buscando a mesma entidade várias vezes | O mesmo arquivo ou símbolo reinjetado no contexto |
| **DataLoader** | N+1 e requisições duplicadas | Subagentes lendo a mesma coisa em paralelo |
| **Análise de custo** | Queries abusivas derrubando o servidor | Respostas estourando a janela de contexto |
| **@defer** | Pagar por dado que talvez não seja exibido | Leitura especulativa |
| **Persisted queries** | Payload e segurança | Prefixos estáveis que aproveitam melhor o *prompt cache* |

**A tese do Morsel é ser o "Apollo Client do contexto do agente".**

## 3. O que o Morsel é

Um **binário único em Go** que roda como **servidor MCP**. Ele fica entre o agente e tudo o que o agente acessa: arquivos, símbolos de código, banco de dados e outros servidores MCP. O agente passa a enxergar:

1. **Um grafo único**, consultado com seleção de campos estilo GraphQL. Cada consulta é chamada de **bite**.
2. **Um preço antes da compra**: cada resposta traz o custo estimado e o custo real em tokens, e respeita um orçamento (**plate**).
3. **Uma memória do que já foi servido**: uma entidade que o agente já recebeu volta como **crumb** (referência curta), não como conteúdo repetido.
4. **Três ferramentas**, não centenas: `morsel_query`, `morsel_schema`, `morsel_expand`.

### O que o Morsel **não** é

- **Não é um framework de agentes.** Não orquestra, não planeja, não chama LLMs. Ele é infraestrutura que qualquer agente usa.
- **Não é um servidor GraphQL de API.** Não substitui o Apollo nem o Hasura. Ele pode ficar **na frente** deles.
- **Não é RAG nem busca vetorial.** Busca semântica pode virar uma fonte no futuro, mas o núcleo é **endereçamento exato** de entidades.
- **Não é um compressor com perdas.** O Morsel não resume nem reescreve conteúdo por conta própria. Ele **seleciona, deduplica e mede**. O agente sempre pode pedir o conteúdo integral.

## 4. Por que agora

- **MCP virou o padrão de integração** entre agentes e ferramentas, então um proxy MCP alcança qualquer agente sem integração específica.
- **O custo de tokens virou assunto de diretoria.** Times passaram a medir e cortar movimento de tokens.
- **O MCP passou a permitir que ferramentas declarem `outputSchema`**, o que torna possível tipar respostas de servidores upstream e projetar campos sem regras manuais.
- **Agentes usam cada vez mais subagentes**, e é nisso que a deduplicação compensa.

## 5. Princípios de produto

1. **Cada token precisa justificar sua presença.** Esse é o critério de toda feature.
2. **Custo visível antes de servir.** Sem surpresas.
3. **Determinismo.** A mesma consulta sobre o mesmo estado completo (incluindo entregas/expiração) devolve os mesmos bytes, o que ajuda o *prompt cache* do provedor.
4. **Neutro.** Funciona com qualquer agente e qualquer modelo. Sem lock-in.
5. **Medir antes de prometer.** Nenhum número de economia é publicado sem um benchmark reproduzível.

## 6. Métrica norte

> **Tokens de contexto por tarefa resolvida**, com taxa de sucesso igual ou maior que a do agente sem o Morsel.

Economizar tokens e piorar o resultado é fracasso. A métrica sempre vem acompanhada da taxa de sucesso.

## 7. Hipótese e critério de parada

**Hipótese H1:** em tarefas reais de código (entender, corrigir, estender) num repositório Go de tamanho médio, um agente com Morsel usa **pelo menos 30% menos tokens de entrada** do que o mesmo agente com as ferramentas nativas, **sem perder taxa de sucesso**.

**Critério de parada:** se o benchmark da v0.1 mostrar menos de 20% de redução, ou uma queda de sucesso maior que 5 pontos percentuais, a tese é revista **antes** de investir nas fontes da v0.2. Esse número decide o futuro do projeto, não a opinião de ninguém.

## 8. Estratégia de lançamento

1. **Construir em público**, com specs abertas desde o dia 1. O próprio processo SDD vira conteúdo.
2. **A demo é um número.** Tela dividida com a mesma tarefa, com e sem Morsel, e um contador de tokens ao vivo. Só é publicada depois do benchmark.
3. **Comando de "uau" imediato:** `morsel stats` mostra quanto a sessão economizou em relação a leituras ingênuas.
4. **Canais:** Show HN, r/golang, r/LocalLLaMA, a comunidade Go Brasil, PRs para awesome-mcp-servers e awesome-go, e posts técnicos sobre "o lado cliente do GraphQL aplicado a agentes".
5. **Selo para projetos que adotam** (`fed by morsel`), como ciclo de divulgação orgânica.

## 9. Riscos

| Risco | Impacto | Mitigação |
|---|---|---|
| O agente escreve bites ruins (pede campos demais) | A economia some | Orçamento obrigatório, erro explicativo com custo por campo, `recipes` prontas e instruções geradas pelo `morsel init` |
| O agente ignora o Morsel e usa as ferramentas nativas | Sem efeito | Snippet para `CLAUDE.md`/`AGENTS.md` e, no futuro, hooks de redirecionamento |
| O agente perde um crumb após compactar o contexto | Resposta incompleta | O crumb carrega um descritor e há `morsel_expand` e `fresh: true` |
| Grandes players (Cursor, Anthropic) fazem otimizações internas | Diferencial menor | Ser neutro, ficar na frente de **qualquer** agente e cobrir também fontes de dados |
| A estimativa de tokens erra | Orçamentos falham | Tokenizer plugável, calibração e meta de erro de ±15% |

## 10. Fontes da pesquisa (novembro de 2026)

- Apollo, "Every Token Counts: Building Efficient AI Agents with GraphQL and Apollo MCP Server": https://www.apollographql.com/blog/building-efficient-ai-agents-with-graphql-and-apollo-mcp-server
- Apollo, "Smart Schema Discovery": https://www.apollographql.com/blog/smart-schema-discovery-how-apollo-mcp-server-maximizes-ai-context-efficiency
- WunderGraph, "GraphQL Is the API Layer AI Agents Actually Need": https://wundergraph.com/blog/graphql-api-layer-for-ai-agents
- Grafbase, "Solving context explosion in GraphQL MCP servers": https://grafbase.com/blog/managing-mcp-context-graphql
- Atlassian, "MCP Compression: Preventing tool bloat in AI agents": https://www.atlassian.com/blog/developer/mcp-compression-preventing-tool-bloat-in-ai-agents
- mcp-distill: https://shoegazerstella.github.io/mcp-distill/
- mcp-trim: https://github.com/pask00/mcp-trim
- Hasura PromptQL: https://hasura.io/promptql
- Augment Code, "AI Agent Loop Token Costs": https://augmentcode.com/guides/ai-agent-loop-token-cost-context-constraints
- The New Stack, "Why cheaper models alone won't save your AI budget": https://thenewstack.io/agentic-ai-token-costs/
- The New Stack, "Stop the token bleed": https://thenewstack.io/?p=22833961
