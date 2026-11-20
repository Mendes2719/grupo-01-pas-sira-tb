# ADR 0007: implantar o sistema como um único processo Uvicorn com o modelo carregado na subida

**Status:** aceito

**Contexto:** O sistema vai rodar no servidor da secretaria de saúde ou, durante a disciplina, no computador de quem avalia. O modelo tem 8,6 MB, a carga dele junto com o XGBoost leva alguns segundos e a predição de um paciente leva algumas dezenas de milissegundos. A equipe não tem pipeline de implantação nem orquestrador, e quem opera precisa saber se a instância está de pé e qual versão do modelo ela carregou.

**Decisão:** Implantar a aplicação como um único processo, iniciado com `python -m uvicorn sira.app:app`, que carrega o modelo uma vez ao subir, usa o banco no caminho dado por `SIRA_BANCO` e expõe `GET /saude` para o monitoramento.

**Alternativas consideradas:**
- Manter o modelo em uma API separada, como no PI: descartada porque dobraria as unidades a implantar e colocaria uma chamada de rede, com timeout e nova tentativa, dentro de cada cadastro.
- Função serverless para a predição: descartada porque cada partida a frio carregaria o XGBoost e o modelo, o que passa do limite de 1 segundo do RNF03.

**Consequências:**
- Positivas: um comando sobe o sistema inteiro; a predição acontece em memória, sem rede; `GET /saude` diz se o banco responde e qual versão do modelo está carregada.
- Negativas: retreinar o modelo exige reiniciar o processo; com SQLite em arquivo não dá para subir uma segunda instância atrás de um balanceador; uma queda do processo tira tudo do ar.
