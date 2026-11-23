# Constituição do Morsel

**Versão:** 1.0.0 · **Ratificada em:** 2026-11-23

Estes princípios valem para **todas** as features. Um plano que viole algum deles precisa registrar a exceção, com justificativa, na seção *Constitution Check* do `plan.md`. Exceções sem justificativa bloqueiam o merge.

---

## I. Contexto é um recurso escasso

Cada token que o Morsel coloca na janela do agente precisa justificar sua presença.

- O padrão é **o mínimo útil**. Mais conteúdo vem só quando o agente pede explicitamente.
- Nenhuma resposta inclui metadados que o agente não pediu, exceto o envelope mínimo (`cost`, `crumbs`, `truncated`).
- Formatos de saída são compactos (JSON sem indentação, chaves curtas e estáveis).

## II. Custo visível antes de servir

- Toda resposta informa o custo estimado (`cost.estimated`) e o custo medido (`cost.actual`) em tokens.
- Toda consulta tem um orçamento (`plate`). Se não houver um explícito, aplica-se o padrão da configuração.
- **Nunca se excede o orçamento em silêncio.** Quando algo não cabe, a resposta diz o que foi cortado e como pedir o restante.

## III. Somente leitura e seguro por padrão

- O Morsel **não escreve** em nenhuma fonte na linha principal do produto. Escrita, se um dia existir, exige spec própria e opt-in explícito.
- O acesso fica confinado à raiz configurada. Caminhos fora dela, incluindo via symlink, são recusados.
- Arquivos sensíveis são negados por padrão (`.env*`, chaves privadas, `*.pem`, credenciais conhecidas) e não podem ser liberados sem configuração explícita.
- O Morsel respeita `.gitignore` por padrão.
- Nenhum dado sai da máquina. O Morsel não faz telemetria.

## IV. Neutro em relação a agente e modelo

- A interface primária é o **MCP**. Nenhuma feature pode depender de um agente ou provedor específico.
- Integrações específicas (por exemplo, hooks do Claude Code) são opcionais e ficam fora do núcleo.

## V. Binário único, zero atrito

- O núcleo é distribuído como **um binário Go estático, sem cgo**.
- `morsel init` + `morsel serve` precisam resultar em algo útil sem editar configuração.
- Dependências novas no núcleo exigem justificativa no `research.md`.

## VI. Determinismo

- A mesma consulta sobre o mesmo estado das fontes produz **exatamente os mesmos bytes**: ordenação estável de chaves e listas, e nada de timestamps ou IDs aleatórios no payload.
- Motivo: respostas estáveis maximizam o acerto de *prompt cache* dos provedores e tornam os testes de golden file possíveis.

## VII. Medir antes de prometer

- Nenhum número de economia aparece em README, post ou release sem um benchmark **reproduzível** no repositório (`bench/`).
- Os benchmarks sempre reportam **tokens e taxa de sucesso juntos**.
- O `morsel stats` deixa claro que a economia exibida é uma **estimativa contra leituras ingênuas**, não uma medição do provedor.

## VIII. Spec primeiro, teste primeiro

- Comportamento novo começa com mudança de spec.
- Toda tarefa de implementação começa com um teste que falha.
- Os contratos em `contracts/` são verificados por testes de contrato no CI.

## IX. Simplicidade

- A superfície exposta ao agente é de **três ferramentas MCP**. Adicionar uma quarta exige emenda a esta constituição.
- Não existe feature "por via das dúvidas": o que não tem história de usuário não entra.
- É melhor um comportamento previsível do que um comportamento esperto.

---

## Governança

- Emendas são feitas por PR que altera este arquivo, com incremento de versão (SemVer: MAJOR para remover ou redefinir princípios, MINOR para adicionar, PATCH para redação).
- Toda emenda registra a motivação no histórico abaixo.

### Histórico

| Versão | Data | Mudança |
|---|---|---|
| 1.0.0 | 2026-11-23 | Ratificação inicial |
