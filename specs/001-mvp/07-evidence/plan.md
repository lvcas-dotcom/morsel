# Plano M07

`internal/stats` recebe recibos de resultados confirmados e métricas agregadas. Estado por usuário em diretório da plataforma (`os.UserConfigDir` ou estado equivalente documentado), restrito; testes usam diretório temporário. Arquivos não são nomeados a partir de consumer fornecido pela query. Formato versionado permite rejeitar versões desconhecidas.

Snapshot de sessão é gravado atomicamente no fim de cada resposta ou com frequência documentada; sincronização em shutdown. Se gravação falhar, atendimento continua e aviso não inclui dados privados. Baseline usa conjunto explícito de arquivos de evidência; não contar todos os arquivos varridos para resolver um nome.

Runner externo pode ter adaptador para um agente inicial sem contaminar core. Manifests declarativos locais são confiáveis, não recebidos de upstream/queries. Prover comandos de verifier como argv, prazo e workspace isolado; nunca rodar código de benchmark durante check documental normal.

Reprodutibilidade significa procedimento/entradas fixados, não determinismo do LLM. Guardar metadados e uso bruto redigido, commit, seed e verificações; relatórios de latência separam captura fria, hashing, cache, projeção e serialização.

Medir tokens no nível da tarefa inteira. Cache de prompt do provedor e custos não crescem simplesmente com tokens textuais; reportar componentes disponíveis sem extrapolar. Uma decisão humana revisa evidência antes de qualquer alegação README ou release.
