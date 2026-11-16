# SIRA-TB

Sistema de Identificação de Risco de Abandono do Tratamento de Tuberculose. A partir dos dados da notificação, estima a probabilidade de o paciente abandonar o tratamento, mostra os fatores que mais pesaram nessa estimativa e ordena os pacientes por risco, para ajudar a equipe de saúde a decidir quem recebe o Tratamento Diretamente Observado.

Trabalho final de Padrões e Arquitetura de Software, PUC-Campinas, 2026-2, grupo 1. O ponto de partida é o nosso Projeto Integrador VI: a pasta `legado/` traz o preditor como foi entregue no PI, e `modelo/` traz o modelo treinado com os microdados do SINAN.

## Integrantes

| Nome | RA | GitHub |
|---|---|---|
| Lucas Silva Brites | 24009893 | [Lucas-Brites1](https://github.com/Lucas-Brites1) |
| Mateo Shimizu Arbulu | 24013271 | [MateoZk](https://github.com/MateoZk) |
| Murilo de Santana Mendes | 24012855 | [Mendes2719](https://github.com/Mendes2719) |
| Pedro Henrique Lange Souza | 24008468 | [Pedro-lange](https://github.com/Pedro-lange) |

## Como rodar

Precisa do Python 3.12. Os comandos rodam na raiz do repositório.

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m sira.acesso.criar_usuario enfermeira
python -m uvicorn sira.app:app
```

No Linux ou no macOS, a ativação do ambiente é `source .venv/bin/activate`.

Com o sistema no ar, abra http://localhost:8000/docs e:

1. em `POST /login`, entre com o usuário criado e copie o token devolvido;
2. clique em **Authorize** e cole o token;
3. em `POST /casos`, o exemplo de notificação já vem preenchido, é só executar;
4. em `GET /casos/{id_caso}`, consulte o caso pelo `id` devolvido no cadastro.
