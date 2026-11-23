# Plano M01

Usar [arquitetura](../../../docs/ARCHITECTURE.md) e [contratos](../contracts/protocol.md). Acrescentar `embed.go` no pacote de contratos ao criar `go.mod`; `//go:embed` aponta apenas para arquivos locais desse pacote.

Escolher Go suportado e parser/SDK a partir de releases reais. Registrar versões, licenças e motivo em research. Começar com `testing`, `go vet` e um analisador estático; não duplicar staticcheck standalone e dentro de um agregador sem necessidade.

CI em duas etapas: documentos/contratos sempre; checks Go quando o módulo for criado na mesma entrega. Check de dependências usa imports de `go list -json` e a matriz permitida. Não contar linhas ou cobertura percentual como qualidade de arquitetura.

Verificação: fixtures inválidas para checker, schema JSON/SDL com parser real, import/embedding em módulo, teste de fronteira de imports, build sem cgo. Não criar testes que apenas repetem structs sem exercitar contrato.

Licença já declarada pelo README é materializada nesta revisão. Canal privado de segurança, responsáveis por conduta e configuração de publicação continuam gates explícitos, não fatos presumidos.
