# 5. Clean Code

## Nomes claros

Os nomes dizem o que a coisa é no domínio, como `listar_priorizados`, `usuario_da_sessao`, `FaixaDeRisco.MUITO_ALTO`, `notificados_desde` e `cadastrado_por`. A diferença aparece quando se compara com o legado, que mantivemos como estava ([legado/prever.py](https://github.com/Mendes2719/grupo-01-pas-sira-tb/blob/560fb9da0972ac4ab1a1524e453f09518f9a74c0/legado/prever.py#L151-L157)), onde `d`, `x`, `dn`, `dd` e `dt` obrigam a ler o resto do método para saber o que cada um guarda. No código novo o login se lê sem precisar de comentário ([acesso/servico.py](https://github.com/Mendes2719/grupo-01-pas-sira-tb/blob/560fb9da0972ac4ab1a1524e453f09518f9a74c0/sira/acesso/servico.py#L17-L21)):

```python
def entrar(self, login: str, senha: str) -> str:
    usuario = self._usuarios.buscar(login)
    if usuario is None or not confere(senha, usuario.hash_da_senha):
        raise CredenciaisInvalidas()
    return self._sessoes.abrir(login)
```

## Funções pequenas, com uma responsabilidade e poucos parâmetros

Os métodos dos serviços têm de uma a três linhas, como `cadastrar` e `detalhar` ([casos/servico.py](https://github.com/Mendes2719/grupo-01-pas-sira-tb/blob/560fb9da0972ac4ab1a1524e453f09518f9a74c0/sira/casos/servico.py#L15-L24)). Quando a lista ganhou quatro filtros, eles passavam soltos da rota ao repositório, e o `FiltroDeCasos` juntou os quatro em um objeto ([casos/dominio.py](https://github.com/Mendes2719/grupo-01-pas-sira-tb/blob/560fb9da0972ac4ab1a1524e453f09518f9a74c0/sira/casos/dominio.py#L30-L37)):

```python
@dataclass(frozen=True)
class FiltroDeCasos:
    """Recorte da lista priorizada; campo vazio não filtra."""

    faixa: FaixaDeRisco | None = None
    desde: date | None = None
    ate: date | None = None
    municipio: str | None = None
```

Desde então nenhuma função do sistema recebe mais de três parâmetros além de `self`, e o ruff barra o que passar dos limites com as regras C901 (complexidade ciclomática até 8) e PLR0913 (no máximo 5 argumentos).

## Ausência de duplicação relevante

A lista e os indicadores precisam do mesmo recorte, então as condições são montadas em um lugar só ([casos/sqlite.py](https://github.com/Mendes2719/grupo-01-pas-sira-tb/blob/560fb9da0972ac4ab1a1524e453f09518f9a74c0/sira/casos/sqlite.py#L108-L115)), e as duas consultas partem dele ([listar e indicadores](https://github.com/Mendes2719/grupo-01-pas-sira-tb/blob/560fb9da0972ac4ab1a1524e453f09518f9a74c0/sira/casos/sqlite.py#L93-L105)):

```python
def _filtrada(selecao: str, filtro: FiltroDeCasos) -> ConsultaDeCasos:
    return (
        ConsultaDeCasos(selecao)
        .com_faixa(filtro.faixa)
        .notificados_desde(filtro.desde)
        .notificados_ate(filtro.ate)
        .do_municipio(filtro.municipio)
    )
```

## Baixo acoplamento e alta coesão

Cada módulo junta o que muda junto, e por isso o domínio, o serviço, o SQLite e as rotas de casos ficam todos em `sira/casos/`. Entre módulos a conversa passa só pela interface pública do `__init__.py`, e isso não fica só na intenção: o teste de arquitetura ([tests/test_arquitetura.py](https://github.com/Mendes2719/grupo-01-pas-sira-tb/blob/560fb9da0972ac4ab1a1524e453f09518f9a74c0/tests/test_arquitetura.py#L21-L34)) falha no CI quando um módulo importa o interno de outro, e um segundo teste impede que `dominio.py` e `portas.py` importem FastAPI, SQLite ou XGBoost.

## Comentários só para explicar o porquê

Os comentários explicam decisões que o código sozinho não mostra, como guardar só o resumo do token ([acesso/sqlite.py](https://github.com/Mendes2719/grupo-01-pas-sira-tb/blob/560fb9da0972ac4ab1a1524e453f09518f9a74c0/sira/acesso/sqlite.py#L73-L75)):

```python
def _resumo(token: str) -> str:
    # só o resumo vai para o banco: se o arquivo vazar, as sessões abertas não podem ser usadas
    return hashlib.sha256(token.encode()).hexdigest()
```

Seguem a mesma regra o comentário sobre o log não levar o corpo da requisição ([observabilidade.py](https://github.com/Mendes2719/grupo-01-pas-sira-tb/blob/560fb9da0972ac4ab1a1524e453f09518f9a74c0/sira/observabilidade.py#L59-L60)), o que explica por que a rota de indicadores vem antes de `/{id_caso}` ([casos/http.py](https://github.com/Mendes2719/grupo-01-pas-sira-tb/blob/560fb9da0972ac4ab1a1524e453f09518f9a74c0/sira/casos/http.py#L47-L48)) e o que diz por que `legado/` fica fora do linter ([pyproject.toml](https://github.com/Mendes2719/grupo-01-pas-sira-tb/blob/560fb9da0972ac4ab1a1524e453f09518f9a74c0/pyproject.toml#L4-L5)).

## Tratamento de erro explícito

O domínio lança erros com nome (`DadosInvalidos`, `CasoNaoEncontrado`, `CredenciaisInvalidas` e `SessaoInvalida`), e a conversão para status HTTP acontece em um único lugar ([app.py](https://github.com/Mendes2719/grupo-01-pas-sira-tb/blob/560fb9da0972ac4ab1a1524e453f09518f9a74c0/sira/app.py#L55-L63)). O adaptador do PI não deixa o `ValueError` do legado vazar para o resto do sistema e o encadeia no erro do domínio ([risco/preditor_pi.py](https://github.com/Mendes2719/grupo-01-pas-sira-tb/blob/560fb9da0972ac4ab1a1524e453f09518f9a74c0/sira/risco/preditor_pi.py#L21-L24)):

```python
try:
    resposta = self._preditor.prever(notificacao)
except ValueError as erro:
    raise DadosInvalidos(str(erro)) from erro
```

O `/saude` devolve 503 quando o banco não responde, e o comando `criar_usuario` avisa quando o login já existe em vez de mostrar o rastro da exceção.

## Linter

O linter é o ruff, configurado no [pyproject.toml](https://github.com/Mendes2719/grupo-01-pas-sira-tb/blob/560fb9da0972ac4ab1a1524e453f09518f9a74c0/pyproject.toml). As regras ligadas são E e W (pycodestyle), F (pyflakes), I (ordem dos imports), N (nomes da PEP 8), B (bugbear), UP (sintaxe atual do Python), SIM (simplificações), RET (retornos), C90 (complexidade até 8) e PLR (refatorações do pylint, como o limite de argumentos). Desligamos só a N818, que exige o sufixo `Error` em exceções, porque os nomes estão em português. A pasta `legado/` fica de fora pelo motivo do ADR 0003.

```bash
ruff check .
ruff format --check .
```

Os dois comandos rodam no job `lint` do [workflow de CI](https://github.com/Mendes2719/grupo-01-pas-sira-tb/blob/560fb9da0972ac4ab1a1524e453f09518f9a74c0/.github/workflows/ci.yml) em todo PR, e o main está protegido para só aceitar merge com o job verde. As execuções no main ficam em [Actions](https://github.com/Mendes2719/grupo-01-pas-sira-tb/actions?query=branch%3Amain).

## Testes

Os testes usam pytest e rodam com `pytest` na raiz do repositório, também no CI, no job `testes`. Eles cobrem:

- `test_legado.py`: caracterização do preditor do PI, escrita antes de qualquer mudança;
- `test_risco.py`: o adaptador devolve a mesma estimativa do legado, e o decorador não muda nada nem esconde erro;
- `test_casos.py` e `test_casos_sqlite.py`: cadastro, consulta, ordem da lista, filtros combinados e indicadores conferindo com a lista;
- `test_acesso.py`: login, senha errada e logout invalidando o token na hora;
- `test_observabilidade.py`: o log sai em JSON, com o id da requisição e sem o corpo;
- `test_arquitetura.py`: as fronteiras dos ADRs 0001 e 0002.

## Code smells tirados por refatoração

Usamos o catálogo do Refactoring Guru para nomear o que cada refatoração resolveu.

**Long Parameter List e Data Clumps, com Introduce Parameter Object** ([PR #11](https://github.com/Mendes2719/grupo-01-pas-sira-tb/pull/11)). Os quatro filtros da lista andavam juntos da rota ao serviço e do serviço ao repositório ([antes](https://github.com/Mendes2719/grupo-01-pas-sira-tb/blob/65bd0888993ab3c45b784268e577f94af156a728/sira/casos/sqlite.py#L51-L57)):

```python
def listar(
    self,
    faixa: FaixaDeRisco | None,
    desde: date | None,
    ate: date | None,
    municipio: str | None,
) -> list[Caso]:
```

Depois viraram o `FiltroDeCasos`, e a assinatura ficou `listar(self, filtro: FiltroDeCasos)` ([depois](https://github.com/Mendes2719/grupo-01-pas-sira-tb/blob/560fb9da0972ac4ab1a1524e453f09518f9a74c0/sira/casos/sqlite.py#L93)).

**Duplicate Code, evitado com Extract Class** (mesmo PR). A cadeia de `if` que montava as condições da lista ([antes](https://github.com/Mendes2719/grupo-01-pas-sira-tb/blob/65bd0888993ab3c45b784268e577f94af156a728/sira/casos/sqlite.py#L58-L71)) teria de ser copiada na consulta dos indicadores. Ela foi extraída para a classe `ConsultaDeCasos` ([depois](https://github.com/Mendes2719/grupo-01-pas-sira-tb/blob/560fb9da0972ac4ab1a1524e453f09518f9a74c0/sira/casos/sqlite.py#L35-L73)), que a lista e os indicadores usam.

**Primitive Obsession, com Replace Type Code with Class** ([PR #5](https://github.com/Mendes2719/grupo-01-pas-sira-tb/pull/5)). O legado devolve a faixa como texto e a estimativa como dicionário ([legado/prever.py](https://github.com/Mendes2719/grupo-01-pas-sira-tb/blob/560fb9da0972ac4ab1a1524e453f09518f9a74c0/legado/prever.py#L219-L234)). O adaptador traduz isso para o enum `FaixaDeRisco` e para a `Estimativa` imutável ([risco/dominio.py](https://github.com/Mendes2719/grupo-01-pas-sira-tb/blob/560fb9da0972ac4ab1a1524e453f09518f9a74c0/sira/risco/dominio.py#L7-L28)), e o resto do sistema nunca compara a faixa com um texto solto.
