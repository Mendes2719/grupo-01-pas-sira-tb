"""Adaptador SQLite do módulo de casos."""

import json
import sqlite3
from dataclasses import asdict, replace
from datetime import date, datetime
from pathlib import Path
from typing import Self

from sira.banco import conectar
from sira.casos.dominio import Caso, FiltroDeCasos, Indicadores
from sira.risco import Estimativa, FaixaDeRisco, Fator

TABELA = """
CREATE TABLE IF NOT EXISTS casos (
    id INTEGER PRIMARY KEY,
    identificador TEXT NOT NULL,
    data_notificacao TEXT NOT NULL,
    municipio TEXT NOT NULL,
    probabilidade REAL NOT NULL,
    faixa TEXT NOT NULL,
    versao_modelo TEXT NOT NULL,
    explicacao TEXT NOT NULL,
    notificacao TEXT NOT NULL,
    cadastrado_por TEXT NOT NULL,
    cadastrado_em TEXT NOT NULL
)"""
INDICE = "CREATE INDEX IF NOT EXISTS casos_por_risco ON casos (probabilidade DESC)"
INSERCAO = """
INSERT INTO casos (identificador, data_notificacao, municipio, probabilidade, faixa,
                   versao_modelo, explicacao, notificacao, cadastrado_por, cadastrado_em)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""


class ConsultaDeCasos:
    """Builder da consulta de casos: cada filtro informado acrescenta uma condição."""

    def __init__(self, selecao: str):
        self._selecao = selecao
        self._condicoes: list[str] = []
        self._parametros: list[str] = []
        self._agrupamento = ""
        self._ordem = ""

    def com_faixa(self, faixa: FaixaDeRisco | None) -> Self:
        return self._condicao("faixa = ?", faixa.value if faixa else None)

    def notificados_desde(self, data: date | None) -> Self:
        return self._condicao("data_notificacao >= ?", data.isoformat() if data else None)

    def notificados_ate(self, data: date | None) -> Self:
        return self._condicao("data_notificacao <= ?", data.isoformat() if data else None)

    def do_municipio(self, municipio: str | None) -> Self:
        return self._condicao("municipio = ?", municipio)

    def agrupada_por(self, coluna: str) -> Self:
        self._agrupamento = f" GROUP BY {coluna}"
        return self

    def ordenada_por(self, ordem: str) -> Self:
        self._ordem = f" ORDER BY {ordem}"
        return self

    def montar(self) -> tuple[str, list[str]]:
        onde = f" WHERE {' AND '.join(self._condicoes)}" if self._condicoes else ""
        return f"{self._selecao}{onde}{self._agrupamento}{self._ordem}", self._parametros

    def _condicao(self, condicao: str, valor: str | None) -> Self:
        if valor:
            self._condicoes.append(condicao)
            self._parametros.append(valor)
        return self


class CasosSqlite:
    def __init__(self, banco: Path):
        self._banco = banco
        with conectar(banco) as conexao:
            conexao.execute(TABELA)
            conexao.execute(INDICE)

    def adicionar(self, caso: Caso) -> Caso:
        with conectar(self._banco) as conexao:
            id_caso = conexao.execute(INSERCAO, _para_colunas(caso)).lastrowid
        return replace(caso, id=id_caso)

    def buscar(self, id_caso: int) -> Caso | None:
        with conectar(self._banco) as conexao:
            linha = conexao.execute("SELECT * FROM casos WHERE id = ?", (id_caso,)).fetchone()
        return _para_caso(linha) if linha else None

    def listar(self, filtro: FiltroDeCasos) -> list[Caso]:
        consulta = _filtrada("SELECT * FROM casos", filtro).ordenada_por("probabilidade DESC")
        with conectar(self._banco) as conexao:
            linhas = conexao.execute(*consulta.montar()).fetchall()
        return [_para_caso(linha) for linha in linhas]

    def indicadores(self, filtro: FiltroDeCasos) -> Indicadores:
        selecao = "SELECT faixa, COUNT(*) AS casos, SUM(probabilidade) AS soma FROM casos"
        consulta = _filtrada(selecao, filtro).agrupada_por("faixa")
        with conectar(self._banco) as conexao:
            linhas = conexao.execute(*consulta.montar()).fetchall()
        casos_por_faixa = {FaixaDeRisco(linha["faixa"]): linha["casos"] for linha in linhas}
        return Indicadores.das_faixas(casos_por_faixa, sum(linha["soma"] for linha in linhas))


def _filtrada(selecao: str, filtro: FiltroDeCasos) -> ConsultaDeCasos:
    return (
        ConsultaDeCasos(selecao)
        .com_faixa(filtro.faixa)
        .notificados_desde(filtro.desde)
        .notificados_ate(filtro.ate)
        .do_municipio(filtro.municipio)
    )


def _para_colunas(caso: Caso) -> tuple:
    estimativa = caso.estimativa
    explicacao = {
        "percentil": estimativa.percentil,
        "fatores": [asdict(fator) for fator in estimativa.fatores],
        "avisos": estimativa.avisos,
    }
    return (
        caso.identificador,
        caso.data_notificacao.isoformat(),
        caso.municipio,
        estimativa.probabilidade,
        estimativa.faixa.value,
        estimativa.versao_modelo,
        json.dumps(explicacao, ensure_ascii=False),
        json.dumps(caso.notificacao, ensure_ascii=False),
        caso.cadastrado_por,
        caso.cadastrado_em.isoformat(),
    )


def _para_caso(linha: sqlite3.Row) -> Caso:
    explicacao = json.loads(linha["explicacao"])
    estimativa = Estimativa(
        probabilidade=linha["probabilidade"],
        faixa=FaixaDeRisco(linha["faixa"]),
        percentil=explicacao["percentil"],
        fatores=tuple(Fator(**fator) for fator in explicacao["fatores"]),
        avisos=tuple(explicacao["avisos"]),
        versao_modelo=linha["versao_modelo"],
    )
    return Caso(
        identificador=linha["identificador"],
        notificacao=json.loads(linha["notificacao"]),
        estimativa=estimativa,
        cadastrado_por=linha["cadastrado_por"],
        cadastrado_em=datetime.fromisoformat(linha["cadastrado_em"]),
        id=linha["id"],
    )
