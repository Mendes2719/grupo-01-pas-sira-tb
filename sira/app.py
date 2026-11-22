"""Ponto único de montagem: escolhe os adaptadores e liga os módulos na aplicação (ADR 0002)."""

import sqlite3
from collections.abc import Callable

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from legado.prever import Preditor
from sira.acesso import CredenciaisInvalidas, SessaoInvalida
from sira.acesso import http as acesso_http
from sira.acesso.servico import ServicoDeAcesso
from sira.acesso.sqlite import SessoesSqlite, UsuariosSqlite
from sira.banco import CAMINHO, conectar
from sira.casos import CasoNaoEncontrado
from sira.casos import http as casos_http
from sira.casos.servico import ServicoDeCasos
from sira.casos.sqlite import CasosSqlite
from sira.observabilidade import configurar_logs, medir_requisicoes
from sira.risco import DadosInvalidos
from sira.risco import http as risco_http
from sira.risco.cronometro import EstimadorCronometrado
from sira.risco.preditor_pi import PreditorDoPI

ERROS_HTTP = {
    CredenciaisInvalidas: 401,
    SessaoInvalida: 401,
    DadosInvalidos: 422,
    CasoNaoEncontrado: 404,
}

configurar_logs()
preditor = PreditorDoPI(Preditor())
acesso = ServicoDeAcesso(UsuariosSqlite(CAMINHO), SessoesSqlite(CAMINHO))
casos = ServicoDeCasos(CasosSqlite(CAMINHO), EstimadorCronometrado(preditor))

app = FastAPI(title="SIRA-TB", description="Risco de abandono do tratamento de tuberculose")
medir_requisicoes(app)
app.include_router(acesso_http.criar_rotas(acesso))
app.include_router(casos_http.criar_rotas(casos, acesso_http.exigir_login(acesso)))
app.include_router(risco_http.criar_rotas(preditor))


@app.get("/saude", tags=["observabilidade"])
def saude() -> dict[str, str]:
    """Confere o banco e informa a versão do modelo carregado, para quem monitora a instância."""
    try:
        with conectar(CAMINHO) as conexao:
            conexao.execute("SELECT 1")
    except sqlite3.Error as erro:
        raise HTTPException(status_code=503, detail="banco indisponível") from erro
    return {"status": "ok", "modelo": preditor.versao}


def _responder_com(status: int) -> Callable[[Request, Exception], JSONResponse]:
    def responder(_: Request, erro: Exception) -> JSONResponse:
        return JSONResponse(status_code=status, content={"detail": str(erro)})

    return responder


for erro, status in ERROS_HTTP.items():
    app.add_exception_handler(erro, _responder_com(status))
