# Constituição do Morsel

**Versão:** 2.0.0 · **Ratificada em:** 2026-11-23

Estes princípios valem para **todas** as features. Um plano que viole algum deles precisa registrar a exceção, com justificativa, na seção *Constitution Check* do `plan.md`. Exceções sem justificativa bloqueiam o merge.

---

## I. Contexto é um recurso escasso

Cada token que o Morsel coloca na janela do agente precisa justificar sua presença.

- O padrão é **o mínimo útil**. Mais conteúdo vem só quando o agente pede explicitamente.
- Nenhuma resposta inclui metadados que o agente não pediu, exceto o envelope mínimo (`cost`, `crumbs`, `truncated`).
- Formatos de saída são compactos (JSON sem indentação, chaves curtas e estáveis).

## II. Custo visível antes de servir

- Toda resposta de consulta/expansão informa a previsão (`cost.est`), a medição local (`cost.act`) e o medidor (`cost.meter`). Com medidor heurístico, ambos são estimativas, não contagem ou cobrança do provedor. Discovery tem teto próprio.
- Toda consulta tem um orçamento (`plate`). Se não houver um explícito, aplica-se o padrão da configuração.
- O texto final de consulta/expansão respeita o orçamento no medidor declarado, incluindo envelope e marcadores. Entradas abaixo do mínimo são rejeitadas antes da execução. Quando algo não cabe, a resposta diz o que foi cortado e como continuar. O limite não cobre wrappers MCP nem histórico enviado pelo cliente ao provedor.

## III. Somente leitura e seguro por padrão

- O Morsel **não escreve** em nenhuma fonte na linha principal do produto. Escrita, se um dia existir, exige spec própria e opt-in explícito.
- O acesso fica confinado à raiz configurada. Caminhos fora dela, incluindo via symlink, são recusados.
- Arquivos sensíveis são negados por padrão (`.env*`, chaves privadas, `*.pem`, credenciais conhecidas) e não podem ser liberados sem configuração explícita.
- O Morsel respeita `.gitignore` por padrão.
- O runtime não faz rede nem telemetria. Benchmarks externos são opt-in e podem enviar dados ao provedor escolhido; ficam fora do runtime e usam fixtures sem segredos. Nenhuma calibração remota integra a v0.1.

## IV. Neutro em relação a agente e modelo

- A interface primária é o **MCP**. Nenhuma feature pode depender de um agente ou provedor específico.
- Integrações específicas (por exemplo, hooks do Claude Code) são opcionais e ficam fora do núcleo.

## V. Binário único, zero atrito

- O núcleo é distribuído como **um binário Go sem cgo**, estático onde aplicável.
- `morsel init` + `morsel serve` precisam resultar em algo útil sem editar configuração.
- Dependências novas no núcleo exigem justificativa no `research.md`.

## VI. Determinismo

- A mesma entrada com o mesmo estado completo (fontes, política, configuração, medidor, consumidor, entregas e relógio lógico de expiração) produz os mesmos bytes. Primeira e segunda entrega podem diferir por crumbs. Não há timestamps ou IDs aleatórios no payload de consulta.
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
| 2.0.0 | 2026-11-23 | Redefine custo como medição local declarada, escopo do orçamento e determinismo com estado de entrega. Distingue runtime offline do benchmark opt-in; remove calibração remota do MVP e qualifica build estático por plataforma. Motivação: evitar garantias impossíveis ou contraditórias. |
