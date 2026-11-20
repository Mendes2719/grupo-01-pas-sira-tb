"""Cada requisição vira uma linha de log em JSON, com o id da requisição e sem o corpo enviado."""

import io
import json

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from sira.observabilidade import configurar_logs, log, medir_requisicoes


@pytest.fixture
def saida():
    destino = io.StringIO()
    configurar_logs(destino)
    yield destino
    log.handlers.clear()
    log.propagate = True


def test_requisicao_vira_uma_linha_json_sem_o_corpo(saida):
    app = FastAPI()
    medir_requisicoes(app)

    @app.post("/casos")
    def cadastrar(ficha: dict) -> dict:
        return ficha

    cliente = TestClient(app)
    resposta = cliente.post("/casos", json={"idade": 34}, headers={"x-request-id": "abc123"})
    linha = json.loads(saida.getvalue())
    assert resposta.headers["x-request-id"] == "abc123"
    assert (linha["evento"], linha["requisicao"], linha["status"]) == ("requisicao", "abc123", 200)
    assert "idade" not in saida.getvalue()
