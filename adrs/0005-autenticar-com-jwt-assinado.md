# ADR 0005: autenticar com JWT assinado

**Status:** aceito

**Contexto:** O RF09 pede login, e as rotas de casos só podem ser usadas por quem está autenticado (RNF01). O documento do PI previa um token JWT emitido no login e verificado pela API a cada requisição, e a interface web ainda não foi construída.

**Decisão:** Emitir no login um JWT assinado com HS256, com o login no campo `sub` e validade de 8 horas, e validar a assinatura e a validade em toda rota protegida.

**Alternativas consideradas:**
- Sessão guardada no banco: descartada neste momento por acrescentar uma tabela e uma consulta ao banco em cada requisição.
- HTTP Basic com a senha em toda requisição: descartada porque a senha trafegaria e seria verificada com PBKDF2, que é lento de propósito, em cada chamada.

**Consequências:**
- Positivas: a validação não consulta o banco; o token já traz o login de quem está cadastrando o caso.
- Negativas: o token não pode ser revogado antes de expirar; a chave de assinatura precisa ser configurada em `SIRA_CHAVE` e protegida.
