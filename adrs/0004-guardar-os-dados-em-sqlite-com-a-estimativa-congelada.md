# ADR 0004: guardar os dados em SQLite, com a estimativa congelada no registro do caso

**Status:** aceito

**Contexto:** O sistema passa a guardar casos e usuários. O documento do PI previa PostgreSQL, mas nem a equipe nem quem avalia o trabalho tem um servidor de banco disponível, e o volume de um município é de centenas de casos por mês. O RNF09 pede que cada predição guardada mostre quando foi feita, por quem e com qual versão do modelo, mesmo depois de um retreino.

**Decisão:** Usar um único arquivo SQLite, com as tabelas de cada módulo separadas pelo nome, e gravar no caso, no momento do cadastro, a probabilidade, a faixa, os fatores, a versão do modelo, o usuário e a data.

**Alternativas consideradas:**
- PostgreSQL: descartada neste semestre porque exige um servidor instalado para rodar e avaliar o sistema; a porta `RepositorioDeCasos` deixa a troca para um adaptador novo.
- Guardar só a ficha e recalcular a estimativa a cada leitura: descartada porque um retreino mudaria o resultado de casos antigos sem deixar registro, o contrário do que pede o RNF09.

**Consequências:**
- Positivas: nada para instalar além do Python; a lista lê o risco já calculado e ordena pelo índice de probabilidade, sem rodar o modelo.
- Negativas: o SQLite aceita uma escrita por vez, o que limita o uso simultâneo; os fatores ficam em JSON e não podem ser filtrados por SQL; a migração para PostgreSQL vai exigir mover os dados.
