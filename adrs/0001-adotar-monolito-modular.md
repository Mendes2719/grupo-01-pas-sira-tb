# ADR 0001: adotar monolito modular com os módulos acesso, casos e risco

**Status:** aceito

**Contexto:** O PI entregou o preditor e uma API com quatro rotas em dois arquivos, sem banco e sem login. Neste semestre o sistema precisa de autenticação, cadastro de casos, lista priorizada e indicadores, e a continuação no TCC já prevê os módulos de carteira de pacientes e de análise territorial. A equipe tem quatro pessoas no mesmo repositório, nenhuma infraestrutura de operação além do próprio computador, e o volume esperado é o de um município, com algumas centenas de notificações por mês.

**Decisão:** Construir o sistema como uma única aplicação FastAPI dividida nos módulos `acesso`, `casos` e `risco`, cada um com a interface pública no próprio `__init__.py`, e verificar essa fronteira com um teste de arquitetura que roda no CI.

**Alternativas consideradas:**
- Microsserviços, com o modelo em um serviço próprio como no PI: descartada porque nenhuma parte precisa de implantação ou escala independente, e a predição viraria uma chamada de rede dentro de todo cadastro.
- Monolito em camadas: descartada porque o corte por camada técnica junta autenticação, casos e modelo na mesma camada de negócio, sem fronteira para os módulos que o TCC vai acrescentar.

**Consequências:**
- Positivas: um artefato e um comando para subir o sistema; um módulo novo entra sem mexer nos outros; o teste de arquitetura acusa a importação proibida antes do merge.
- Negativas: os três módulos dividem o mesmo processo, então um erro ao carregar o modelo também derruba o login; manter a fronteira exige revisão e cuidado com o teste.
