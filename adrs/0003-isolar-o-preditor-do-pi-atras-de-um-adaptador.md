# ADR 0003: isolar o preditor do PI atrás de um adaptador em vez de reescrevê-lo

**Status:** aceito

**Contexto:** O `legado/prever.py` reconstrói as variáveis do modelo com as mesmas regras do tratamento dos dados, e essa equivalência foi validada no PI: a API reproduz a probabilidade do pipeline de treino em pelo menos 99% dos casos de 2023 (RNF05). O código, porém, fala o vocabulário do PI, com dicionários, faixa como texto sem acento, erro como `ValueError` e campos técnicos como o peso SHAP em log-odds, e a classe `Preditor` concentra formulário, validação, montagem das variáveis, predição e explicação.

**Decisão:** Manter `legado/prever.py` sem alteração e fora do linter, e acessá-lo só pelo adaptador `PreditorDoPI` do módulo risco, que traduz a resposta para `Estimativa`, `Fator` e `FaixaDeRisco` e o erro para `DadosInvalidos`.

**Alternativas consideradas:**
- Reescrever o preditor dentro do novo domínio, em classes menores: descartada porque exigiria refazer a validação de consistência com o pipeline de treino, sem ganho para quem usa o sistema.
- Usar o dicionário do PI direto nos módulos novos: descartada porque o formato do legado se espalharia pelo sistema, e qualquer mudança nele quebraria casos e HTTP ao mesmo tempo.

**Consequências:**
- Positivas: a estimativa continua idêntica à validada no PI, o que o teste de caracterização confere; o resto do sistema não conhece XGBoost, pandas nem o formato do PI.
- Negativas: o legado continua com uma classe grande e métodos longos, só que isolado; toda mudança no formato de resposta do PI exige atualizar o adaptador.
