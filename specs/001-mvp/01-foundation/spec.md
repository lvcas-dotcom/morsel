# M01 — Fundação open source

Estado: especificado; implementação pendente. Dependências: nenhuma. Requisitos: FR-039, FR-040.

## Objetivo e escopo

Permitir que uma pessoa clone, entenda, valide e contribua sem conhecimento privado. Criar módulo, pacote de contratos, checks e documentação mínima; não criar pastas vazias ou handlers fictícios para parecer funcional.

## Requisitos locais

- **FND-01** Módulo Go usa caminho do repositório confirmado, versão suportada e dependências fixadas com `go.sum`. Atualizações de dependência são PRs separados quando não necessárias à feature.
- **FND-02** SDL, schemas e tools são incorporados da pasta canônica; não existem cópias manuais. Alterar contrato exige revisar compatibilidade e exemplos.
- **FND-03** Contribuição, licença, segurança e revisão têm instruções públicas. Não inventar contato, mantenedor, SLA ou suporte a versão inexistente.
- **FND-04** Checks locais reproduzem CI; ações de terceiros são fixadas por SHA, permissões mínimas e workflows de PR não recebem secrets nem executam código não confiável com credenciais de escrita.
- **FND-05** Erros do checker documental falham com mensagem e caminho útil; relações de dependência e cobertura de FR não podem divergir silenciosamente.

## Aceitação

1. Clone limpo: verificação documental passa offline; links locais e catálogo são consistentes.
2. Mudança inválida em JSON, link ou ID: checker falha e aponta o artefato. A M01 acrescenta validação completa JSON Schema e SDL com bibliotecas reais.
3. Após bootstrap Go: `go test ./...`, vet, análise estática e race passam; contratos podem ser importados e embutidos sem `../`.
4. Dependência ou import que viola a arquitetura: check falha. Build sem cgo funciona para os alvos definidos; execução por SO será gate posterior.
5. Guia distingue design, funções implementadas e comandos planejados. Não publicar binário de scaffold como produto.

## Fora de escopo

Release pública, automação que publica sem autorização, tap Homebrew, SDK público e governança com pessoas/canais fictícios.
