# M06 — MCP e CLI

Estado: especificado; implementação pendente. Depende de M05; spike de transporte pertence à M01. Requisitos: FR-028, FR-032, FR-034.

## Objetivo

Executar o mesmo caso de uso pelo agente e terminal, com descoberta estável e inicialização segura.

## Requisitos locais

- **INT-01** Expor exatamente as três tools de tools.json. Fixar versão SDK e conjunto explícito de versões MCP testadas; não anunciar suporte automático a cada revisão nova do protocolo.
- **INT-02** Um bloco textual compacto por query/expand; sem cópia duplicada em structuredContent no perfil v1. Não declarar outputSchema MCP que descreva um objeto ausente de structuredContent. O JSON Schema de envelope é contrato local de conteúdo textual.
- **INT-03** stdout do serve contém exclusivamente MCP, logs seguros em stderr. Sem conteúdo de fonte/query/segredo em logs padrão. Sinais, deadline e cancelamento encerram trabalho.
- **INT-04** `query` CLI usa mesmo pipeline e limites; cada invocação é nova conexão lógica, portanto não promete crumbs entre processos. `serve`, `init`, `query`, `stats` e `version` formam CLI v0.1; runner A/B é ferramenta externa.
- **INT-05** `init` cria morsel.toml sem sobrescrever e, por padrão, imprime snippet para aplicação manual. Escrita em instruções só com `--instructions <path>` explícito, caminho local autorizado, bloco delimitado, idempotente e atualizado atomicamente sem substituir conteúdo alheio.
- **INT-06** Config existente inválida causa erro útil, não reset. Falha parcial de init é reportada com arquivos escritos e retomada segura; não alegar transação atômica entre dois arquivos.

## Aceitação

1. Cliente SDK inicia subprocesso, descobre exatamente três tools, chama query/schema/expand e interpreta envelopes reais.
2. JSON de argumentos inválido recebe erro de protocolo; erros de domínio usam envelope e `isError:true` sem adicionar texto extra fora dele. Resposta parcial com dados usa `isError:false` e errors no envelope.
3. Cliente cancela leitura cara, encerra stdin ou recebe sinal: servidor encerra sem goroutines/descritores pendentes; stdout continua parseável.
4. Init duas vezes preserva bytes de instruções existentes e não duplica bloco; symlink, caminho externo, interrupção e arquivo conflitante são recusados/recuperáveis.
5. Query CLI e MCP produzem mesmos bytes com mesmo estado lógico/configuração; flags só traduzem entrada, não implementam regras duplicadas.
6. Teste com cliente agente real documenta versão e consumer. Se subagentes compartilham contexto sem IDs distinguíveis, crumbs ficam desativados; cache e projeção continuam úteis.
