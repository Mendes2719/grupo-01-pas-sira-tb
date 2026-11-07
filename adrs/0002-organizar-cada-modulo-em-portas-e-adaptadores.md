# ADR 0002: organizar cada módulo em portas e adaptadores

**Status:** aceito

**Contexto:** As regras do sistema, como o que é um caso, a ordem da lista e a validade de uma sessão, precisam continuar as mesmas quando a tecnologia em volta mudar, e algumas mudanças já estão previstas: o modelo é retreinado a cada ano fechado no SINAN, o banco da implantação real ainda não foi definido e a interface web ainda não existe. No código do PI as rotas chamam o preditor direto, e qualquer teste precisa carregar o XGBoost.

**Decisão:** Dentro de cada módulo, o domínio e o serviço declaram as portas como `Protocol` e não importam FastAPI, SQLite nem o modelo; os adaptadores de HTTP, banco e modelo implementam essas portas, e a montagem acontece em um único ponto, `sira/app.py`.

**Alternativas consideradas:**
- Camadas com dependência direta (rota, serviço e repositório concreto): descartada porque o serviço importaria o SQLite e o preditor, e o teste das regras continuaria preso à infraestrutura.
- Clean Architecture com os quatro círculos em pastas separadas: descartada pelo número de arquivos que criaria em três módulos pequenos, sem regra a mais para proteger.

**Consequências:**
- Positivas: os serviços são testados com SQLite temporário e estimador falso, sem XGBoost; trocar uma tecnologia é trocar um adaptador e uma linha em `sira/app.py`.
- Negativas: mais arquivos por módulo, e o mapeamento entre o domínio e as tabelas é escrito à mão em cada adaptador.
