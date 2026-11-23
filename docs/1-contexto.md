# 1. Contexto

## O problema e para quem

O tratamento da tuberculose dura no mínimo seis meses e depende da adesão do paciente. Entre os casos notificados no Brasil de 2015 a 2023 que terminaram em cura ou abandono, 17,7% foram abandono, e a taxa subiu de 14,8% em 2015 para 21,7% em 2023. A medida mais indicada contra o abandono é o Tratamento Diretamente Observado (TDO), só que não há equipe para acompanhar todos os pacientes, e hoje a escolha de quem recebe o TDO depende da percepção de cada equipe.

O SIRA-TB estima, no momento da notificação, a probabilidade de o paciente abandonar o tratamento, mostra os fatores que mais pesaram nessa estimativa e ordena os pacientes por risco. Ele é feito para as equipes das unidades básicas de saúde que notificam e acompanham os casos, para os Programas de Controle da Tuberculose e para as secretarias municipais e estaduais de saúde.

## Escopo

Entra neste repositório a API que a aplicação web vai consumir:

- login e logout de quem usa o sistema;
- cadastro do caso com a estimativa, a faixa de risco e os fatores, guardados junto com a versão do modelo;
- lista priorizada com filtros por faixa, período e município, detalhe do caso e indicadores da lista;
- a ficha de notificação com os campos obrigatórios, montada a partir do modelo;
- logs estruturados e um ponto de saúde para quem opera o sistema.

Fica de fora a interface web em React prevista no PI, o pipeline de dados e o treino do modelo, que continuam no repositório do PI e entregam aqui só a pasta `modelo/`, a integração com o SINAN, qualquer diagnóstico ou recomendação clínica e os módulos de carteira de pacientes e de análise territorial, que ficam para o TCC.

## O que já existia no PI e o que este trabalho mudou

O PI entregou o modelo treinado e uma API em dois arquivos, que estão no [commit inicial](https://github.com/Mendes2719/grupo-01-pas-sira-tb/tree/861f231287aa64f5da8e2f96cf0e885aa0c5bea9/legado): `prever.py`, com a classe `Preditor` que valida a ficha, monta as variáveis, roda o XGBoost e explica a estimativa, e `api.py`, com as rotas `/saude`, `/campos`, `/prever` e `/priorizar`. Não havia banco, login nem lista guardada, e a API carregava o modelo já no import.

Neste trabalho o código virou um monolito modular, com os módulos acesso, casos e risco organizados em portas e adaptadores e uma função de aptidão no CI ([PR #2](https://github.com/Mendes2719/grupo-01-pas-sira-tb/pull/2)). O preditor do PI ficou em `legado/` sem alteração, atrás de um adaptador ([PR #5](https://github.com/Mendes2719/grupo-01-pas-sira-tb/pull/5)), e o resto do sistema foi construído em volta dele: persistência em SQLite com a estimativa congelada ([PR #6](https://github.com/Mendes2719/grupo-01-pas-sira-tb/pull/6)), login ([PR #7](https://github.com/Mendes2719/grupo-01-pas-sira-tb/pull/7)), depois trocado por uma sessão que o logout encerra ([PR #9](https://github.com/Mendes2719/grupo-01-pas-sira-tb/pull/9)), cadastro e consulta de casos ([PR #8](https://github.com/Mendes2719/grupo-01-pas-sira-tb/pull/8)), lista priorizada ([PR #10](https://github.com/Mendes2719/grupo-01-pas-sira-tb/pull/10)) e indicadores ([PR #13](https://github.com/Mendes2719/grupo-01-pas-sira-tb/pull/13)).

No caminho, a lista foi refatorada com o `FiltroDeCasos` e um Builder ([PR #11](https://github.com/Mendes2719/grupo-01-pas-sira-tb/pull/11)), a estimativa ganhou um Decorator que mede o tempo ([PR #14](https://github.com/Mendes2719/grupo-01-pas-sira-tb/pull/14)) e entraram os logs estruturados com o `/saude` ([PR #12](https://github.com/Mendes2719/grupo-01-pas-sira-tb/pull/12)), além do ruff, do pytest e do CI desde o primeiro PR ([PR #1](https://github.com/Mendes2719/grupo-01-pas-sira-tb/pull/1)). As rotas `/prever` e `/priorizar` saíram, porque agora o cadastro faz a estimativa e a lista ordena os casos guardados.
