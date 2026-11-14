"""Ponto único de montagem: escolhe os adaptadores e liga os módulos na aplicação (ADR 0002)."""

import os
import secrets
from collections.abc import Callable

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from legado.prever import Preditor
from sira.acesso import CredenciaisInvalidas, SessaoInvalida
from sira.acesso import http as acesso_http
from sira.acesso.servico import ServicoDeAcesso
from sira.acesso.sessoes_jwt import SessoesJwt
from sira.acesso.sqlite import UsuariosSqlite
from sira.banco import CAMINHO
from sira.risco import http as risco_http
from sira.risco.preditor_pi import PreditorDoPI

ERROS_HTTP = {CredenciaisInvalidas: 401, SessaoInvalida: 401}

preditor = PreditorDoPI(Preditor())
# sem SIRA_CHAVE, cada reinício gera uma chave nova e derruba as sessões abertas
chave = os.environ.get("SIRA_CHAVE") or secrets.token_hex(32)
acesso = ServicoDeAcesso(UsuariosSqlite(CAMINHO), SessoesJwt(chave))

app = FastAPI(title="SIRA-TB", description="Risco de abandono do tratamento de tuberculose")
app.include_router(acesso_http.criar_rotas(acesso))
app.include_router(risco_http.criar_rotas(preditor))


def _responder_com(status: int) -> Callable[[Request, Exception], JSONResponse]:
    def responder(_: Request, erro: Exception) -> JSONResponse:
        return JSONResponse(status_code=status, content={"detail": str(erro)})

    return responder


for erro, status in ERROS_HTTP.items():
    app.add_exception_handler(erro, _responder_com(status))
