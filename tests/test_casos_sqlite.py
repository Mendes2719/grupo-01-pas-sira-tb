"""Adaptador SQLite do módulo de casos, contra um banco temporário."""

import pytest

from sira.casos.sqlite import CasosSqlite


@pytest.fixture
def repositorio(tmp_path):
    return CasosSqlite(tmp_path / "casos.db")


def test_caso_gravado_volta_igual(repositorio, novo_caso):
    gravado = repositorio.adicionar(novo_caso())
    assert gravado.id is not None
    assert repositorio.buscar(gravado.id) == gravado


def test_busca_de_caso_inexistente_devolve_none(repositorio):
    assert repositorio.buscar(1) is None
