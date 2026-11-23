# Plano M06

Adaptadores finos em `mcpserver` e `cli` chamam app. Contratos são incorporados pelo pacote canônico. Evitar registro automático de tools por reflexão que altere schemas sem revisão.

Reusar o spike M01-T06 antes de finalizar M05: negociar protocolos, observar escrita/cancelamento e garantir que o handler não faça commit prematuro. Cliente de integração em subprocesso testa framing/stdout; cliente em memória não substitui esse teste.

Init usa temp file no mesmo diretório, sync/rename quando aplicável e modo preservado. Validação anti-symlink também vale no destino de instruções; raiz de escrita é o projeto escolhido pelo operador, sem caminho fornecido por tool. O princípio de leitura de fontes admite os arquivos de configuração/instruções explicitamente criados por init.

Exit codes CLI: 0 sucesso, 2 argumento/config inválido, 1 erro operacional/domínio sem dados. Sucesso parcial deve ser distinguível via errors/truncated do JSON, mantendo saída consumível. Help deixa claro o medidor heurístico e como escolher consumer/fresh.

Testes: subprocesso SDK, testscript ou exec com diretório temporário, instrução preexistente, falha de gravação e sinais. Medir tamanho de discovery completo; meta das descrições não substitui esse custo.
