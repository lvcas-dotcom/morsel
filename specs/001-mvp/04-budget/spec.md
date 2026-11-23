# M04 — Orçamento e serialização

Estado: especificado; implementação pendente. Depende de M03. Requisitos: FR-011, FR-012, FR-013, FR-014, FR-015, FR-016, FR-029.

## Objetivo

Finalizar respostas compactas e recuperáveis dentro de um orçamento local verificável, informando exatamente o que foi medido.

## Requisitos locais

- **BGT-01** Padrão 4.000, mínimo 256 e teto 16.000 unidades. Precedência: argumento `budget` > diretiva `@budget` > configuração. Valores fora do intervalo são rejeitados, nunca ajustados silenciosamente.
- **BGT-02** `est` prevê antes de projetar a resposta; `act` é a contagem do JSON textual final no medidor identificado. O padrão `heuristic-v1` usa `ceil(bytes_UTF8/4)` para contagem final; previsão por tamanho pode superestimar. Sem alegação de calibração até SC-002 medido.
- **BGT-03** Wrapper MCP e uso de provedor ficam fora da medição. Medidores alternativos são determinísticos, offline e identificados por algoritmo/versão; máximo sobre bytes de saída também é obrigatório.
- **BGT-04** Estratégia de redução é determinística, termina e contabiliza marcadores/erros. Nunca cortar JSON bruto, partir código UTF-8 ou fabricar valor parcial como completo.
- **BGT-05** `@brief(lines:N)` só em folha textual elegível, N positivo e limitado. Prefixo é marcado e recuperável por seleção/expansão explícita. Corte automático usa `reason:budget`, não finge solicitação brief.
- **BGT-06** Se o mínimo selecionado não couber, retorna envelope `over_budget` compacto, também dentro do orçamento. Breakdown/sugestões opcionais são limitados e removíveis. Entrada abaixo do mínimo é erro de argumento fora da garantia de payload de query.
- **BGT-07** Ordem do envelope e data, nulls e referências seguem protocolo. Chaves dinâmicas e desempates não dependem da iteração de map nem da conclusão de goroutines.

## Aceitação

1. Variar Unicode, escaping JSON, aliases longos, listas e budget: todo sucesso/erro de domínio aceito tem `act <= budget` e contagem correta do texto final.
2. Estimativa deliberadamente subestimada: guard converge sem devolver payload acima do teto; marcador também ocupa orçamento.
3. Todos os textos cortados têm caminho de resposta válido e recuperação executável. Campo removido não entra no histórico de entrega M05.
4. Mesmo estado completo e relógio controlado produz bytes idênticos em múltiplas execuções e ordem de resolução diferente.
5. Orçamentos conflitantes obedecem precedência; negativos/acima do máximo são rejeitados antes de executar.

## Limitação explícita

Heurística não limita tokens cobrados por um provedor. SC-002 é precisão experimental, não prova de teto universal. Um medidor exato só é exato para a codificação identificada.
