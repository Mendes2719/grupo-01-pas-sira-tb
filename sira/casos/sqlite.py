"""Adaptador SQLite do módulo de casos."""

import json
import sqlite3
from dataclasses import asdict, replace
from datetime import datetime
from pathlib import Path

from sira.banco import conectar
from sira.casos.dominio import Caso
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
