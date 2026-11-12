"""Conexão com o arquivo SQLite; cada módulo cria e consulta só as próprias tabelas (ADR 0004)."""

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

CAMINHO = Path("sira.db")


@contextmanager
def conectar(caminho: Path) -> Iterator[sqlite3.Connection]:
    conexao = sqlite3.connect(caminho)
    conexao.row_factory = sqlite3.Row
    try:
        with conexao:
            yield conexao
    finally:
        conexao.close()
