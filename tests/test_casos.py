"""Serviço de casos com SQLite temporário e um estimador falso, sem carregar o XGBoost."""

import pytest

from sira.casos import CasoNaoEncontrado
from sira.casos.servico import ServicoDeCasos
from sira.casos.sqlite import CasosSqlite

NOTIFICACAO = {"data_notificacao": "2026-09-10", "municipio_residencia": "350950"}


class EstimadorFalso:
    def __init__(self, estimativa):
        self.estimativa = estimativa

    def estimar(self, notificacao: dict):
        return self.estimativa


@pytest.fixture
def estimador(nova_estimativa):
    return EstimadorFalso(nova_estimativa())


@pytest.fixture
def casos(tmp_path, estimador):
    return ServicoDeCasos(CasosSqlite(tmp_path / "casos.db"), estimador)


def test_cadastro_congela_a_estimativa_e_quem_cadastrou(casos, estimador):
    caso = casos.cadastrar("260001", NOTIFICACAO, "ana")
    assert caso.estimativa == estimador.estimativa
    assert caso.cadastrado_por == "ana"
    assert casos.detalhar(caso.id) == caso


def test_caso_inexistente(casos):
    with pytest.raises(CasoNaoEncontrado):
        casos.detalhar(42)
