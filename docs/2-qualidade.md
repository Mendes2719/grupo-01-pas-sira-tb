# 2. Atributos de qualidade

Os três atributos que mais pesam no SIRA-TB, com os nomes e as métricas da tabela 2.1 do livro (seção 2.3, que segue a ISO/IEC 25010:2023).

## Modificabilidade

**Por que ele, e não outro.** O modelo é retreinado a cada ano fechado no SINAN, a interface web ainda vai ser construída e o TCC vai acrescentar os módulos de carteira de pacientes e de análise territorial. O sistema vai mudar muito mais do que vai crescer em carga, já que um município tem algumas centenas de notificações por mês, e por isso escalabilidade e disponibilidade ficaram abaixo.

**Decisão.** Monolito modular com fronteira verificada no CI (ADR 0001), portas e adaptadores dentro de cada módulo (ADR 0002) e o preditor do PI atrás de um adaptador (ADR 0003).

**Medida.** Número de módulos tocados por uma mudança típica. A troca do JWT pela sessão no banco ([PR #9](https://github.com/Mendes2719/grupo-01-pas-sira-tb/pull/9)) mexeu em um módulo, `acesso`, e na montagem em `sira/app.py`. Um retreino troca os arquivos de `modelo/` e não toca em nenhum arquivo de `sira/`, porque o formulário e as faixas vêm dos metadados do modelo.

## Segurança

**Por que ele, e não outro.** Os casos são dados de saúde, classificados como sensíveis pela LGPD (RNF02), e as rotas de casos só podem ser usadas por quem está autenticado (RNF01). Um acesso indevido ou um vazamento custa muito mais aqui do que alguns milissegundos a mais de resposta.

**Decisão.** Sessão guardada no banco, que o logout encerra na hora (ADR 0006), senha guardada só como hash PBKDF2 com sal e log com campos fixos, sem o corpo nem os parâmetros das requisições.

**Medida.** Superfícies expostas sem login: `/login`, `/campos`, `/saude` e a documentação em `/docs`, nenhuma com dado de paciente. O teste `test_logout_encerra_a_sessao_na_hora` confere que o token deixa de valer logo depois do logout, e `test_requisicao_vira_uma_linha_json_sem_o_corpo` confere que o corpo enviado não aparece no log.

## Desempenho

**Por que ele, e não outro.** A estimativa aparece enquanto o profissional registra a notificação, e o RNF03 fixa os limites: até 1 segundo para a estimativa com a explicação e até 3 segundos para a lista com até 1.000 casos.

**Decisão.** O modelo fica carregado na memória do mesmo processo da API, sem chamada de rede (ADR 0007), e a estimativa é gravada no cadastro, então a lista só lê e ordena pelo índice de probabilidade (ADR 0004).

**Medida.** Latência da estimativa e da lista. O `EstimadorCronometrado` registra `duracao_ms` em cada estimativa e o middleware registra a duração de cada requisição. Rodando localmente, 30 cadastros seguidos tiveram a estimativa com mediana de 18 ms e máximo de 46 ms, o cadastro completo pela API ficou com mediana de 26 ms e a lista com 1.030 casos respondeu em 52 ms.

## Trade-off assumido

Pioramos a escalabilidade de propósito. Com um único processo e o banco em um arquivo SQLite (ADRs 0004 e 0007), o sistema não sobe uma segunda instância atrás de um balanceador e aceita uma escrita por vez. Em troca, a estimativa roda em memória, sem rede no meio, e o sistema inteiro sobe com um comando, o que ganha desempenho e mantém a operação simples para uma secretaria municipal, que é quem vai rodar o sistema. É o caso que a seção 2.4 descreve: nenhum estilo é bom em todos os atributos ao mesmo tempo, e o que escolhemos priorizar está registrado nos ADRs.
