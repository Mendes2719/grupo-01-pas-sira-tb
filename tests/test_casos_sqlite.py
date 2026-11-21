"""Adaptador SQLite do módulo de casos, contra um banco temporário."""

from datetime import date

import pytest

from sira.casos.dominio import FiltroDeCasos
from sira.casos.sqlite import CasosSqlite
from sira.risco import FaixaDeRisco


@pytest.fixture
def repositorio(tmp_path):
    return CasosSqlite(tmp_path / "casos.db")


def test_caso_gravado_volta_igual(repositorio, novo_caso):
    gravado = repositorio.adicionar(novo_caso())
    assert gravado.id is not None
    assert repositorio.buscar(gravado.id) == gravado


def test_busca_de_caso_inexistente_devolve_none(repositorio):
    assert repositorio.buscar(1) is None


def test_lista_vem_do_maior_para_o_menor_risco(repositorio, novo_caso):
    for probabilidade in (0.2, 0.7, 0.4):
        repositorio.adicionar(novo_caso(probabilidade))
    lista = repositorio.listar(FiltroDeCasos())
    assert [caso.estimativa.probabilidade for caso in lista] == [0.7, 0.4, 0.2]


def test_filtros_combinados(repositorio, novo_caso):
    repositorio.adicionar(novo_caso(0.6, FaixaDeRisco.MUITO_ALTO, "2026-09-01", "350950"))
    repositorio.adicionar(novo_caso(0.5, FaixaDeRisco.MUITO_ALTO, "2026-10-01", "350950"))
    repositorio.adicionar(novo_caso(0.3, FaixaDeRisco.ALTO, "2026-09-15", "350950"))
    repositorio.adicionar(novo_caso(0.7, FaixaDeRisco.MUITO_ALTO, "2026-09-20", "355030"))
    filtro = FiltroDeCasos(FaixaDeRisco.MUITO_ALTO, date(2026, 9, 1), date(2026, 9, 30), "350950")
    lista = repositorio.listar(filtro)
    assert [caso.estimativa.probabilidade for caso in lista] == [0.6]


def test_indicadores_conferem_com_a_lista_filtrada(repositorio, novo_caso):
    repositorio.adicionar(novo_caso(0.6, FaixaDeRisco.MUITO_ALTO))
    repositorio.adicionar(novo_caso(0.3, FaixaDeRisco.ALTO))
    repositorio.adicionar(novo_caso(0.06, FaixaDeRisco.BAIXO))
    repositorio.adicionar(novo_caso(0.9, FaixaDeRisco.MUITO_ALTO, municipio="355030"))
    filtro = FiltroDeCasos(municipio="350950")
    lista = repositorio.listar(filtro)
    indicadores = repositorio.indicadores(filtro)
    assert indicadores.total == len(lista) == 3
    assert indicadores.alto_ou_muito_alto == 2
    assert indicadores.probabilidade_media == 0.32
    assert indicadores.por_faixa[FaixaDeRisco.MODERADO] == 0
