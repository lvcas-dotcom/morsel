# Plano M04

`internal/budget` recebe result tree e estimativas, não filesystem. Serialização tem ordem explícita do protocolo. Medidor é pequena interface no consumidor que prevê e mede; padrão usa bytes UTF-8, sem rede.

O MVP oferece apenas `heuristic-v1`. Para resolver a autorreferência de `act`, serializar primeiro com `act=0`, calcular `ceil(bytes/4)`, inserir a contagem e repetir até estabilizar. Com todos os outros campos fixos, o tamanho só muda com a quantidade de dígitos de `act`; essa função é monótona e limitada pelo máximo de bytes de resposta. Portanto a iteração crescente termina num ponto fixo, sem padding, espaços artificiais ou reserva aproximada. Recontar o texto final e exigir igualdade com `act`.

Não incluir `cost.saved` no envelope v1: sua dependência de `act` complicaria desnecessariamente a finalização. A economia é calculada no ledger depois de fixar o texto e exibida em stats. A interface pode permitir outros medidores internamente, mas habilitar um medidor novo exige provar finalização estável; não assumir que um tokenizer BPE é monótono com mudanças em números.

Redução sempre remove pelo menos uma unidade semântica: item de lista ou folha textual. Brief explícito vem primeiro; por orçamento, reduzir maior contribuição, desempate pelo JSON Pointer lexical. Não reduzir escalares obrigatórios inventando valores. Se não houver unidade redutível, cair para erro mínimo prevalidado com budget mínimo suportado. Reduzir também quantidade/comprimento de marcadores antes desse fallback.

Esse algoritmo só está pronto após property tests sobre JSON escapado e limites numéricos. Testar o erro mínimo, todos os metadados opcionais e mudanças no número de dígitos; nenhum contador de iterações pode autorizar enviar excesso. Preferir algoritmo mais simples que demonstre o mesmo contrato quando a implementação revelar oportunidade, alterando este plano antes.

Integração deve usar contador real configurado, não mock que devolve sempre 1. Fuzz cobre encode/decode, progressão e limite; exemplos JSON Schema não verificam desigualdade numérica entre campos, por isso a invariante precisa de teste Go.
