# M07 — Evidência, stats e release

Estado: especificado; implementação pendente. Depende de M06. Requisitos: FR-030, FR-031, FR-033, FR-042; gates de FR-040, FR-041.

## Objetivo

Separar contabilidade local de evidência experimental e decidir o futuro do produto com resultados auditáveis.

## Requisitos locais

- **EVD-01** Baseline por bite = custo no medidor efetivo dos arquivos permitidos distintos cujo conteúdo/fragmento foi usado na resolução, lidos integralmente uma vez por bite. Scans de índice e arquivos usados só para autorização não aumentam artificialmente o baseline. `saved=max(0,naive-act)` é estimativa.
- **EVD-02** Por sessão persistir apenas versão do formato, ID local, início/fim, medidor e contadores por categoria. Nunca persistir path, query, fragmento, conteúdo, env ou consumer explícito. Atomic rename e permissões restritas; persistência é best effort, falha reportada em stderr.
- **EVD-03** Stats seleciona `--session <id>` ou a mais recente no diretório de estado; não presume sessão ativa compartilhada com outro processo. Retenção por prazo e capacidade; contador de processo ativo é snapshot eventual identificado como tal.
- **EVD-04** Runner externo `bench/run` é opt-in e isolado do binário. FR-033 é atendido por essa substituição explícita do comando inicialmente proposto `morsel bench`. Nada de chamadas de provedor em serve/query/init/stats.
- **EVD-05** Fixar commit fixture, versão Morsel/agente/modelo, instruções, políticas de ferramentas e verificadores. Braços diferem apenas na disponibilidade do Morsel e snippet. Ordem randomizada com seed registrada, worktrees limpas e caches independentes.
- **EVD-06** Coletar input/output, cached input quando disponível, custo segundo tabela/versionamento documentado, sucesso e falhas. Ausência de uso gera `unknown`, não zero. Uso faturado, texto das ferramentas e baseline estimado são métricas distintas.
- **EVD-07** Tarefas de bug/extensão usam testes independentes não fornecidos ao agente; entendimento usa rubrica fixada antes e julgamento humano cego. Teste de palavra isolada não mede sucesso. Piloto com N≥5/ braço/tarefa não prova H1 por si só.
- **EVD-08** Predefinir margem de não inferioridade de sucesso em 5 p.p., tamanho de amostra/poder e intervalos de 95%, respeitando agrupamento por tarefa. Intervalo que cruza o limite é inconclusivo, mesmo com mediana favorável. H1 demanda redução ≥30% e sucesso não inferior; aplicar critério de parada da visão.
- **EVD-09** Publicar artefatos só com revisão de segredos/licenças. Lançamento exige testes, checksums, notas de limitações, canal privado de segurança real e documentação reproduzida. Não inventar selo de produção ou compatibilidade sem execução no alvo.

## Aceitação

1. Duas leituras do mesmo arquivo dentro de uma bite contam um baseline; erro sem conteúdo não produz economia fictícia. Heurística aparece como estimativa em stats e relatório.
2. Crash/interrupção e duas sessões concorrentes não criam JSON parcial ou misturam contadores. Arquivo malformado é ignorado com aviso seguro; retenção não toca arquivos fora do diretório de estado.
3. Verifier falha quando agente só cria ANSWER.md contendo palavra-chave; correção precisa resolver teste independente, sem poder editar o verifier.
4. Runner com fixtures sintéticas de sucesso/erro/uso ausente gera relatório correto; todas as falhas permanecem no denominador.
5. Relatório de piloto diz positivo, negativo ou inconclusivo e lista manifest, seed, exclusões previamente justificadas e intervalos. Não promove roadmap 002+ sem evidência suficiente.
6. Release candidata passa build e testes por alvo, instalação em máquina limpa, help, licença/atribuições e teste real de primeira bite.
