# M05 — Crumbs e histórico de entrega

Estado: especificado; implementação pendente. Depende de M04. Requisitos: FR-017, FR-018, FR-019, FR-020, FR-021, FR-022, FR-038.

## Objetivo

Evitar repetir conteúdo que um consumidor identificou como pertencente ao mesmo contexto, com recuperação explícita e sem suprimir conteúdo não entregue.

## Requisitos locais

- **DLV-01** Namespace = conexão + consumidor explícito. Ausência de consumer não gera nem consulta histórico de entrega. Dois subagentes que não compartilham contexto devem usar IDs diferentes.
- **DLV-02** Identidade de valor inclui entidade, versão, campo e argumentos efetivos normalizados, inclusive intervalos. Alias muda caminho da resposta, não identidade semântica. Somente folhas textuais completas elegíveis são referenciáveis.
- **DLV-03** Crumb só substitui valor acima do mínimo configurado e se for menor no medidor efetivo. Descriptor é uma linha, até 120 caracteres Unicode e limitado também por custo.
- **DLV-04** `fresh` desativa supressão nesta consulta. Expand resolve entidade ou fragmento, reautoriza fonte e retorna versão atual com fresh; se a versão mudou, não oferece conteúdo histórico como atual.
- **DLV-05** Resultado produz plano de entregas provisório. Confirmar apenas após escrita completa bem-sucedida; falha, corte ou cancelamento não cria entrega. Expiração usa relógio injetado e contador por consumidor.
- **DLV-06** Expira ao atingir TTL OU distância de consultas definida; evicção por capacidade permite repetir conteúdo. Consultas inválidas não avançam contador; operações query/expand válidas avançam mesmo em erro de domínio, após escrita.

## Aceitação

1. Duas consultas do mesmo body com consumer: segunda pode ter crumb; sem consumer ambas têm conteúdo. Consumidores e conexões diferentes recebem conteúdo na primeira leitura.
2. `lines(1,10)` e `lines(50,60)` nunca compartilham crumb. Mesmos argumentos com defaults/ordem diferente compartilham identidade.
3. Entrega cortada por budget, falha de transporte e cancelamento não suprimem uma consulta seguinte.
4. Mudança de fonte/política revalida acesso; expiração, eviction e reconexão voltam a servir conteúdo.
5. Expand do `$crumb` é utilizável sem interpretar ID manualmente; erro de versão, arquivo removido ou acesso negado é explícito.
6. Consultas concorrentes podem ambas devolver conteúdo completo; não podem devolver crumb antes de uma entrega confirmada.
