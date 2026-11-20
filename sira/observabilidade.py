"""Observabilidade: log em JSON com o id da requisição em cada linha (livro, seção 18.5)."""

import json
import logging
import sys
from collections.abc import Awaitable, Callable
from contextvars import ContextVar
from time import perf_counter
from typing import TextIO
from uuid import uuid4

from fastapi import FastAPI, Request, Response

log = logging.getLogger("sira")
id_da_requisicao: ContextVar[str] = ContextVar("id_da_requisicao", default="-")


class FormatoJson(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        linha = {
            "momento": self.formatTime(record),
            "nivel": record.levelname,
            "evento": record.getMessage(),
            "requisicao": id_da_requisicao.get(),
            **getattr(record, "dados", {}),
        }
        if record.exc_info:
            linha["erro"] = self.formatException(record.exc_info)
        return json.dumps(linha, ensure_ascii=False)


def configurar_logs(destino: TextIO = sys.stderr) -> None:
    saida = logging.StreamHandler(destino)
    saida.setFormatter(FormatoJson())
    log.handlers = [saida]
    log.setLevel(logging.INFO)
    log.propagate = False


def medir_requisicoes(app: FastAPI) -> None:
    @app.middleware("http")
    async def medir(
        requisicao: Request, seguir: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        marca = id_da_requisicao.set(requisicao.headers.get("x-request-id") or uuid4().hex[:12])
        inicio = perf_counter()
        try:
            resposta = await seguir(requisicao)
            resposta.headers["x-request-id"] = id_da_requisicao.get()
            _registrar(requisicao, resposta.status_code, inicio)
            return resposta
        except Exception:
            log.exception("erro_nao_tratado", extra={"dados": {"rota": requisicao.url.path}})
            raise
        finally:
            id_da_requisicao.reset(marca)


def _registrar(requisicao: Request, status: int, inicio: float) -> None:
    # só método, rota e status: o corpo e os parâmetros podem trazer dado de paciente (RNF02)
    dados = {
        "metodo": requisicao.method,
        "rota": requisicao.url.path,
        "status": status,
        "duracao_ms": round((perf_counter() - inicio) * 1000, 1),
    }
    log.info("requisicao", extra={"dados": dados})
