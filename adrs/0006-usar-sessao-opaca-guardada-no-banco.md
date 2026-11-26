# ADR 0006: usar sessão opaca guardada no banco

**Status:** aceito, substitui o ADR 0005

**Contexto:** Substitui o ADR 0005. Ao implementar o logout do RF09, que pede que o logout encerre a sessão e bloqueie o acesso às rotas protegidas, o JWT continuou aceito até expirar, porque o servidor não guarda nada sobre o token emitido. Com dados de saúde, um token esquecido no computador compartilhado de uma unidade continuaria valendo por até 8 horas depois do logout.

**Decisão:** Gerar no login um token aleatório, guardar no banco só o resumo SHA-256 dele com o login e a validade, consultar essa tabela em cada rota protegida e apagar a linha no logout.

**Alternativas consideradas:**
- Manter o JWT com uma lista de tokens revogados: descartada porque também consulta o banco em toda requisição e ainda deixa a chave de assinatura para configurar.
- JWT de validade curta com token de renovação: descartada porque continua existindo uma janela em que o token vale depois do logout, e o fluxo de login fica com o dobro de passos.

**Consequências:**
- Positivas: o logout vale na hora; não há chave de assinatura para configurar; a troca do tipo de token mexeu só no adaptador de sessões e em `sira/app.py`, sem mudar `entrar` nem `usuario_da_sessao` no serviço.
- Negativas: uma consulta ao banco a mais em cada requisição protegida; sessões vencidas continuam na tabela até alguém apagá-las.

**Implementado em:** [PR #9](https://github.com/Mendes2719/grupo-01-pas-sira-tb/pull/9)
