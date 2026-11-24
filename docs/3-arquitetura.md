# 3. Arquitetura

## Plano macro: monolito modular

O SIRA-TB é um monolito modular (livro, capítulo 6): uma única aplicação FastAPI, implantada como um processo, dividida nos módulos `acesso`, `casos` e `risco`, cada um com a interface pública no próprio `__init__.py` (ADR 0001).

**Quando adotar (seção 6.5).** O livro indica o estilo para sistema novo cujo domínio ainda está sendo descoberto, quando o time cabe em uma ou duas equipes e a organização não tem plataforma de operação madura. É o nosso caso, com quatro pessoas, nenhuma infraestrutura além do computador de cada um e um domínio que ainda vai ganhar os módulos de carteira e de análise territorial no TCC. A seção também cita a intenção real de extrair serviços no futuro, e o módulo `risco` é o candidato natural, porque o resto do sistema só fala com ele pela porta `EstimadorDeRisco`.

**Quando evitar (seção 6.6).** O estilo perde quando times diferentes precisam publicar em ritmos diferentes ou quando uma parte exige máquina diferente, e nada disso acontece aqui: o modelo roda em CPU comum em algumas dezenas de milissegundos. O erro de adoção que o livro aponta, pastas renomeadas sem nenhuma verificação, é coberto pela função de aptidão em [tests/test_arquitetura.py](https://github.com/Mendes2719/grupo-01-pas-sira-tb/blob/a8ccb5169aefabbaa21390a2744514864ffefa0b/tests/test_arquitetura.py#L21-L34), que roda no CI e falha quando um módulo importa o interno de outro:

```python
def interno_de_outro_modulo(nome: str, modulo: str) -> bool:
    partes = nome.split(".")
    return partes[0] == "sira" and len(partes) > 2 and partes[1] in MODULOS - {modulo}
```

**Custo real (seção 6.7).** A operação é a de um artefato só, igual à do monolito em camadas, e o teste de cada módulo roda rápido, sem ambiente distribuído. O custo que pagamos é de time e de governança: revisar a fronteira em cada PR, manter a interface pública pequena e manter o teste de arquitetura.

## Plano interno: portas e adaptadores em cada módulo

Dentro de cada módulo o código segue a arquitetura hexagonal (capítulo 7 e ADR 0002). O domínio e o serviço ficam no centro e declaram as portas como `Protocol`, os adaptadores de HTTP, SQLite e modelo ficam na borda e implementam essas portas, e `sira/app.py` é o único ponto que conhece as classes concretas e monta tudo ([app.py](https://github.com/Mendes2719/grupo-01-pas-sira-tb/blob/a8ccb5169aefabbaa21390a2744514864ffefa0b/sira/app.py#L32-L41)). O módulo `risco` não tem serviço próprio, porque a porta é atendida direto pelo adaptador do preditor do PI.

```mermaid
flowchart LR
    subgraph entrada["Adaptadores primários"]
        http["http.py de cada módulo (FastAPI)"]
        cli["acesso/criar_usuario.py (linha de comando)"]
    end
    subgraph nucleo["Núcleo do módulo"]
        servico["servico.py (casos de uso)"]
        dominio["dominio.py (entidades e regras)"]
        portas["portas.py (Protocol)"]
    end
    subgraph saida["Adaptadores secundários"]
        sqlite["sqlite.py (SQLite)"]
        preditor["risco/preditor_pi.py e risco/cronometro.py"]
    end
    montagem["sira/app.py (montagem)"]
    http -->|"chamada"| servico
    cli -->|"chamada"| servico
    servico -->|"chamada"| dominio
    servico -->|"depende de"| portas
    sqlite -.->|"implementa"| portas
    preditor -.->|"implementa"| portas
    montagem -.->|"cria e injeta"| http
    montagem -.->|"cria e injeta"| sqlite
    montagem -.->|"cria e injeta"| preditor
```

| Parte | Pasta ou arquivo |
|---|---|
| Domínio | `sira/acesso/dominio.py`, `sira/casos/dominio.py`, `sira/risco/dominio.py` |
| Portas | `sira/acesso/portas.py`, `sira/casos/portas.py`, `sira/risco/portas.py` |
| Serviços (casos de uso) | `sira/acesso/servico.py`, `sira/casos/servico.py` |
| Adaptadores primários | `sira/*/http.py` e `sira/acesso/criar_usuario.py` |
| Adaptadores secundários | `sira/acesso/sqlite.py`, `sira/casos/sqlite.py`, `sira/risco/preditor_pi.py`, `sira/risco/cronometro.py` |
| Montagem | `sira/app.py` |
| Apoio compartilhado | `sira/banco.py` e `sira/observabilidade.py` |
| Legado do PI | `legado/prever.py` |

## Estilos considerados e descartados

**Microsserviços (capítulo 9).** No PI o modelo já tinha uma API própria e a aplicação web estava prevista como outra unidade, então separar risco, casos e acesso em serviços era o caminho mais óbvio. Descartamos porque nenhuma parte precisa de implantação ou escala independente, e cada cadastro passaria a depender de uma chamada de rede ao serviço de risco, com timeout, nova tentativa e falha parcial para tratar, um custo de operação alto para uma equipe de quatro pessoas sem plataforma para isso.

**Monolito em camadas (capítulo 5).** É o arranjo padrão de uma API FastAPI, com rota, serviço e repositório. Descartamos porque o corte por camada técnica deixaria login, casos e modelo na mesma camada de negócio, sem fronteira para os módulos do TCC, e o serviço importaria o SQLite e o XGBoost direto, o que deixaria o teste das regras preso à infraestrutura.

## C4

Os níveis 1 e 2 usam a sintaxe C4 do Mermaid e o nível 3 usa diagrama de fluxo, como os modelos do apêndice B.4. Cada conector traz o tipo no rótulo. As fontes estão em [`diagrams/`](../diagrams).

### Nível 1, contexto

```mermaid
C4Context
    title Nível 1 (contexto) do SIRA-TB
    Person(profissional, "Profissional de saúde", "Notifica o caso e decide quem recebe TDO")
    System(sira, "SIRA-TB", "Estima o risco de abandono e ordena os pacientes por risco")
    System_Ext(pipeline, "Pipeline de dados do PI", "Trata os microdados do SINAN e treina o modelo")
    Rel(profissional, sira, "chamada: cadastra casos e consulta a lista", "HTTPS")
    Rel(pipeline, sira, "arquivo: entrega modelo.json e metadados.json", "JSON")
    UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1")
```

### Nível 2, contêineres

A aplicação web ainda não existe e está no diagrama porque é ela que vai consumir a API; enquanto isso, a API é usada pela documentação interativa em `/docs`.

```mermaid
C4Container
    title Nível 2 (contêineres) do SIRA-TB
    Person(profissional, "Profissional de saúde", "Notifica o caso e decide quem recebe TDO")
    System_Ext(pipeline, "Pipeline de dados do PI", "Trata os microdados do SINAN e treina o modelo")
    System_Boundary(sira, "SIRA-TB") {
        Container(web, "Aplicação web", "React e TypeScript, prevista no PI", "Telas de login, cadastro, lista e detalhe")
        Container(api, "API do SIRA-TB", "Python, FastAPI e Uvicorn", "Monolito modular com os módulos acesso, casos e risco")
        ContainerDb(banco, "Banco", "SQLite", "Usuários, sessões e casos com a estimativa congelada")
        ContainerDb(modelo, "Modelo", "XGBoost em JSON", "modelo.json e metadados.json")
    }
    Rel(profissional, web, "chamada: usa", "HTTPS")
    Rel(web, api, "chamada: login, cadastro, lista e indicadores", "HTTPS e JSON")
    Rel(api, banco, "arquivo: lê e grava", "sqlite3")
    Rel(api, modelo, "arquivo: carrega na subida", "JSON")
    Rel(pipeline, modelo, "arquivo: gera a cada retreino", "JSON")
    UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1")
```

### Nível 3, componentes da API

```mermaid
flowchart TB
    web["Aplicação web ou /docs"]
    subgraph api["API do SIRA-TB (unidade de implantação)"]
        obs["observabilidade: log JSON e id da requisição"]
        acesso["acesso: login, logout e sessões"]
        casos["casos: cadastro, lista, detalhe e indicadores"]
        risco["risco: PreditorDoPI e EstimadorCronometrado"]
        legado["legado/prever.py: Preditor do PI"]
    end
    banco[("SQLite")]
    modelo[("modelo/")]
    web -->|"chamada HTTP"| obs
    obs -->|"chamada"| acesso
    obs -->|"chamada"| casos
    obs -->|"chamada: GET /campos"| risco
    casos -->|"chamada: exigir_login"| acesso
    casos -->|"chamada: porta EstimadorDeRisco"| risco
    risco -->|"chamada"| legado
    legado -->|"arquivo"| modelo
    acesso -->|"arquivo"| banco
    casos -->|"arquivo"| banco
    style api fill:#ffffff,stroke:#444444,stroke-dasharray: 6 4
```

## Sequência do cadastro de um caso

O fluxo central do sistema é o cadastro, que já devolve a estimativa ao profissional.

```mermaid
sequenceDiagram
    actor P as Profissional
    participant O as observabilidade
    participant H as casos/http.py
    participant A as ServicoDeAcesso
    participant S as ServicoDeCasos
    participant C as EstimadorCronometrado
    participant D as PreditorDoPI
    participant L as Preditor (legado)
    participant R as CasosSqlite
    P->>O: POST /casos com token e ficha
    O->>H: repassa com o id da requisição
    H->>A: usuario_da_sessao(token)
    A-->>H: login
    H->>S: cadastrar(identificador, ficha, login)
    S->>C: estimar(ficha)
    C->>D: estimar(ficha)
    D->>L: prever(ficha)
    alt ficha válida
        L-->>D: dicionário do PI
        D-->>C: Estimativa
        C-->>S: Estimativa, e o log "estimativa" com duracao_ms
        S->>R: adicionar(caso)
        R-->>S: caso com id
        S-->>H: Caso
        H-->>O: 201 com o caso
    else campo obrigatório ausente ou valor fora das opções
        L-->>D: ValueError
        D-->>H: DadosInvalidos, convertido em 422 pelo app.py
    end
    O-->>P: resposta, e o log "requisicao" com o mesmo id
```
