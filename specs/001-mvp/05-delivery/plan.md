# Plano M05

`internal/delivery` guarda valores de chave, versão e marcador, não conteúdo. Relógio e sequência são dependências explícitas; mutex cobre apenas mapa/LRU/commit. Operação de commit contém entradas idempotentes e não faz I/O de fonte.

Token de fragmento opaco com prefixo `frag:` é serialização canônica base64url de ID, campo e argumentos, sem autoridade embutida. Resolve via versão atual e política da fonte. Não usar o fragmento como autorização nem prometer segredo; validar tamanho/schema antes de parse.

TTL a partir da última entrega completa; crumb repetido não renova conhecimento indefinidamente. Distância de query usa contador confirmado e monotonamente crescente por consumidor. Clock de parede não aparece no envelope. Testes avançam relógio/contador sem sleeps.

Escrita e commit são coordenados por app/adaptador. Confirmar depois que SDK indicar escrita concluída; se SDK não expuser essa fronteira, o spike M01-T06 deve instrumentar transporte ou manter supressão desativada até haver evidência. Não chamar retorno do handler de confirmação de transporte sem verificar.

Rollback parcial não é necessário porque nada é registrado antes do resultado final. Métricas usam o mesmo receipt de sucesso e snapshots contadores, sem transação distribuída ou promessa de exatamente uma entrega.
