# Plano de integração 001

Estado: desenho, implementação pendente. Substitui o plano monolítico anterior. A [arquitetura](../../docs/ARCHITECTURE.md) é a referência de dependências; o [catálogo](README.md) define as sete entregas e os planos locais.

## Decisões de integração

- Módulo pretendido: `github.com/lvcas-dotcom/morsel`, coerente com `origin` examinado. Confirmar novamente ao criar `go.mod`.
- Selecionar versão Go ainda suportada ao implementar M01; registrar mínimo exato em `go.mod` e CI. `os.Root` é requisito de implementação. Não presumir que uma versão antiga seguirá suportada.
- `CGO_ENABLED=0`; validar build e execução por plataforma separadamente. Cross-build não demonstra segurança ou funcionamento no alvo.
- SDL, schemas e descrições ficam em `specs/001-mvp/contracts`, com `embed.go` e tipos Go acrescentados na M01. Assim `go:embed` não depende de `../` nem cópias em `internal/`.
- Runtime usa biblioteca padrão, SDK MCP oficial e parser GraphQL fixados por versão. Cada dependência adicional exige motivo e licença em research. CLI pode começar com `flag`; cobra só com benefício concreto. SHA-256 da stdlib substitui xxhash truncado.
- Um processo stdio por conexão. Sem daemon, persistência de conteúdo, rede no runtime, calibração remota ou Homebrew tap no MVP.

## Contratos

As três ferramentas são definidas em [tools.json](contracts/tools.json). O [protocolo](contracts/protocol.md) estabelece precedência de orçamento, identidade de fragmentos, erros, recuperação e o perfil de resposta com crumbs. Não se anuncia conformidade de execução GraphQL completa.

Antes de entrar código de resolução, a M01 incorpora os contratos e a M03 testa parse/coerção com o parser real. A M04 valida JSON e invariantes de orçamento com o medidor real. O schema documental sozinho não prova nenhuma delas.

## Constitution Check (v2.0.0)

| Princípio | Aplicação | Exceção |
|---|---|---|
| I — Contexto | Campos selecionados, referências só quando menores | Não |
| II — Custo | Medidor declarado; orçamento inclui texto final | Não |
| III — Segurança | Root, política antes de cache; runtime sem rede; bench externo opt-in | Não |
| IV — Neutralidade | MCP fino; adaptador de agente restrito ao benchmark | Não |
| V — Binário | Sem cgo, dependências justificadas, init seguro | Não |
| VI — Determinismo | Estado completo e ordem definidos no protocolo | Não |
| VII — Evidência | M07 e H1 permanecem pendentes | Não |
| VIII — Spec/teste | Aceitação e tarefas por entrega, testes antes de implementação | Não |
| IX — Simplicidade | Três tools e monólito modular | Não |

## Integração e falhas

Um teste de subprocesso deve cobrir a mesma sequência da pessoa usuária: criar fixture, init, iniciar serve, listar tools, consultar arquivo/símbolo, repetir com consumidor, expandir, editar fonte, consultar nova versão e encerrar. Também exercita sessão nova, entrada inválida, timeout e stdout exclusivamente MCP.

Usar golden files para bytes determinísticos, testes de propriedade para orçamento e chaves, fuzz para parser/cursor e filesystem real para segurança. Não criar lint que proíbe qualquer iteração de map: verificar o comportamento serializado e imports permitidos.

Latência, uso de memória, precisão heurística, sucesso e economia são medições futuras. Os relatórios devem incluir captura fria e revalidação, não apenas resolver com índice previamente montado.
