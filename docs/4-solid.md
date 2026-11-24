# 4. SOLID

## S: princípio da responsabilidade única

No PI, o `api.py` carregava o modelo no import, montava o esquema de entrada a partir dos metadados, configurava o CORS e, em cada rota, chamava o preditor e convertia o erro em HTTP ([antes](https://github.com/Mendes2719/grupo-01-pas-sira-tb/blob/861f231287aa64f5da8e2f96cf0e885aa0c5bea9/legado/api.py#L68-L73)):

```python
@app.post("/prever")
def prever(paciente: Paciente):
    try:
        return {"id": paciente.id, **preditor.prever(_dados(paciente))}
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
```

Hoje cada responsabilidade do cadastro tem o seu lugar. A rota só traduz a requisição em uma chamada ao serviço ([casos/http.py](https://github.com/Mendes2719/grupo-01-pas-sira-tb/blob/a8ccb5169aefabbaa21390a2744514864ffefa0b/sira/casos/http.py#L38-L41)), o serviço junta estimativa e gravação sem saber de HTTP nem de SQL ([casos/servico.py](https://github.com/Mendes2719/grupo-01-pas-sira-tb/blob/a8ccb5169aefabbaa21390a2744514864ffefa0b/sira/casos/servico.py#L15-L18)), o adaptador grava ([casos/sqlite.py](https://github.com/Mendes2719/grupo-01-pas-sira-tb/blob/a8ccb5169aefabbaa21390a2744514864ffefa0b/sira/casos/sqlite.py#L83-L86)) e a conversão de erro em status fica em um ponto só ([app.py](https://github.com/Mendes2719/grupo-01-pas-sira-tb/blob/a8ccb5169aefabbaa21390a2744514864ffefa0b/sira/app.py#L25-L30)).

```python
def cadastrar(self, identificador: str, notificacao: dict, usuario: str) -> Caso:
    estimativa = self._estimador.estimar(notificacao)
    caso = Caso(identificador, notificacao, estimativa, usuario, datetime.now().astimezone())
    return self._repositorio.adicionar(caso)
```

**Efeito:** cada arquivo muda por um motivo só. A troca do JWT pela sessão não tocou em nenhum arquivo do módulo de casos, e uma mudança no formato de erro do legado fica restrita ao adaptador do PI. O `api.py` saiu no [PR #8](https://github.com/Mendes2719/grupo-01-pas-sira-tb/pull/8), depois que o `/campos` passou para o módulo de risco no [PR #5](https://github.com/Mendes2719/grupo-01-pas-sira-tb/pull/5).

## O: princípio aberto/fechado

A medição do tempo de cada estimativa (RNF03) entrou como um decorador que envolve qualquer `EstimadorDeRisco` ([risco/cronometro.py](https://github.com/Mendes2719/grupo-01-pas-sira-tb/blob/a8ccb5169aefabbaa21390a2744514864ffefa0b/sira/risco/cronometro.py#L14-L26)), e a única linha alterada no código que já existia foi a da montagem ([app.py](https://github.com/Mendes2719/grupo-01-pas-sira-tb/blob/a8ccb5169aefabbaa21390a2744514864ffefa0b/sira/app.py#L35)):

```python
casos = ServicoDeCasos(CasosSqlite(CAMINHO), EstimadorCronometrado(preditor))
```

**Efeito:** o `PreditorDoPI` e o `ServicoDeCasos` ficaram fechados para modificação, e o comportamento foi estendido por composição. O diff do [PR #14](https://github.com/Mendes2719/grupo-01-pas-sira-tb/pull/14) mostra só o arquivo novo, o teste e essa linha.

## L: princípio da substituição de Liskov

O serviço de acesso conta com o contrato da porta `Sessoes`: `dono` devolve o login ou lança `SessaoInvalida`, que o `app.py` converte em 401. Quando o JWT deu lugar à sessão guardada no banco ([PR #9](https://github.com/Mendes2719/grupo-01-pas-sira-tb/pull/9)), a classe nova cumpriu o mesmo contrato da antiga.

Antes ([acesso/sessoes_jwt.py](https://github.com/Mendes2719/grupo-01-pas-sira-tb/blob/5050cbd42a814f083354e7621c1104b452596e81/sira/acesso/sessoes_jwt.py#L20-L24)):

```python
def dono(self, token: str) -> str:
    try:
        return jwt.decode(token, self._chave, algorithms=["HS256"])["sub"]
    except jwt.InvalidTokenError as erro:
        raise SessaoInvalida() from erro
```

Depois ([acesso/sqlite.py](https://github.com/Mendes2719/grupo-01-pas-sira-tb/blob/a8ccb5169aefabbaa21390a2744514864ffefa0b/sira/acesso/sqlite.py#L59-L66)):

```python
def dono(self, token: str) -> str:
    with conectar(self._banco) as conexao:
        linha = conexao.execute(
            "SELECT login, expira_em FROM acesso_sessoes WHERE resumo = ?", (_resumo(token),)
        ).fetchone()
    if linha is None or datetime.fromisoformat(linha["expira_em"]) < datetime.now(UTC):
        raise SessaoInvalida()
    return linha["login"]
```

O decorador da seção anterior segue a mesma regra: devolve a estimativa do estimador envolvido sem mudar nada e deixa passar o `DadosInvalidos`, o que o teste [test_cronometro_devolve_a_mesma_estimativa_e_repassa_o_erro](https://github.com/Mendes2719/grupo-01-pas-sira-tb/blob/a8ccb5169aefabbaa21390a2744514864ffefa0b/tests/test_risco.py#L28-L32) confere.

**Efeito:** `entrar` e `usuario_da_sessao` não mudaram, e a rota protegida continua respondendo 401 do mesmo jeito para token inválido, vencido ou encerrado.

## I: princípio da segregação de interfaces

O `Preditor` do PI tem uma interface larga, com `campos`, `meta`, `prever`, `prever_lote` e o próprio `booster` do XGBoost, e a API do PI dependia dela inteira. O módulo de casos só precisa de uma operação, e a porta declara só ela ([risco/portas.py](https://github.com/Mendes2719/grupo-01-pas-sira-tb/blob/a8ccb5169aefabbaa21390a2744514864ffefa0b/sira/risco/portas.py#L8-L9)):

```python
class EstimadorDeRisco(Protocol):
    def estimar(self, notificacao: dict) -> Estimativa: ...
```

No módulo de acesso, o cadastro de usuário é uma função que recebe só o repositório de usuários ([acesso/servico.py](https://github.com/Mendes2719/grupo-01-pas-sira-tb/blob/a8ccb5169aefabbaa21390a2744514864ffefa0b/sira/acesso/servico.py#L8-L9)), separada do serviço de login, que também precisa das sessões.

**Efeito:** o estimador falso dos testes de casos tem um método só ([tests/test_casos.py](https://github.com/Mendes2719/grupo-01-pas-sira-tb/blob/a8ccb5169aefabbaa21390a2744514864ffefa0b/tests/test_casos.py#L12-L17)), e o comando `criar_usuario` não precisa criar nem conhecer sessões.

## D: princípio da inversão de dependência

No PI a API dependia da classe concreta e carregava o modelo no momento do import ([antes](https://github.com/Mendes2719/grupo-01-pas-sira-tb/blob/861f231287aa64f5da8e2f96cf0e885aa0c5bea9/legado/api.py#L24-L26)):

```python
from prever import Preditor

preditor = Preditor()
```

Hoje o serviço de casos depende de duas abstrações ([casos/servico.py](https://github.com/Mendes2719/grupo-01-pas-sira-tb/blob/a8ccb5169aefabbaa21390a2744514864ffefa0b/sira/casos/servico.py#L10-L13)), e só a montagem conhece as classes concretas ([app.py](https://github.com/Mendes2719/grupo-01-pas-sira-tb/blob/a8ccb5169aefabbaa21390a2744514864ffefa0b/sira/app.py#L32-L35)):

```python
class ServicoDeCasos:
    def __init__(self, repositorio: RepositorioDeCasos, estimador: EstimadorDeRisco):
        self._repositorio = repositorio
        self._estimador = estimador
```

**Efeito:** os testes do serviço rodam com SQLite temporário e um estimador falso, sem carregar o XGBoost, e trocar uma tecnologia vira trocar o argumento passado em `app.py`, como aconteceu com as sessões. A dependência concreta saiu no [PR #5](https://github.com/Mendes2719/grupo-01-pas-sira-tb/pull/5), que criou a porta e o adaptador, e no [PR #8](https://github.com/Mendes2719/grupo-01-pas-sira-tb/pull/8), que passou a receber o estimador por injeção.
