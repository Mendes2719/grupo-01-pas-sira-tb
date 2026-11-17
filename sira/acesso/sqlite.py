"""Adaptadores SQLite do módulo de acesso."""

import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from pathlib import Path

from sira.acesso.dominio import SessaoInvalida, Usuario
from sira.banco import conectar

VALIDADE = timedelta(hours=8)


class UsuariosSqlite:
    def __init__(self, banco: Path):
        self._banco = banco
        with conectar(banco) as conexao:
            conexao.execute(
                "CREATE TABLE IF NOT EXISTS acesso_usuarios"
                " (login TEXT PRIMARY KEY, hash_da_senha TEXT NOT NULL)"
            )

    def buscar(self, login: str) -> Usuario | None:
        with conectar(self._banco) as conexao:
            linha = conexao.execute(
                "SELECT login, hash_da_senha FROM acesso_usuarios WHERE login = ?", (login,)
            ).fetchone()
        return Usuario(**linha) if linha else None

    def adicionar(self, usuario: Usuario) -> None:
        with conectar(self._banco) as conexao:
            conexao.execute(
                "INSERT INTO acesso_usuarios (login, hash_da_senha) VALUES (?, ?)",
                (usuario.login, usuario.hash_da_senha),
            )


class SessoesSqlite:
    """Sessão opaca guardada no banco (ADR 0006)."""

    def __init__(self, banco: Path):
        self._banco = banco
        with conectar(banco) as conexao:
            conexao.execute(
                "CREATE TABLE IF NOT EXISTS acesso_sessoes"
                " (resumo TEXT PRIMARY KEY, login TEXT NOT NULL, expira_em TEXT NOT NULL)"
            )

    def abrir(self, login: str) -> str:
        token = secrets.token_urlsafe(32)
        expira_em = datetime.now(UTC) + VALIDADE
        with conectar(self._banco) as conexao:
            conexao.execute(
                "INSERT INTO acesso_sessoes (resumo, login, expira_em) VALUES (?, ?, ?)",
                (_resumo(token), login, expira_em.isoformat()),
            )
        return token

    def dono(self, token: str) -> str:
        with conectar(self._banco) as conexao:
            linha = conexao.execute(
                "SELECT login, expira_em FROM acesso_sessoes WHERE resumo = ?", (_resumo(token),)
            ).fetchone()
        if linha is None or datetime.fromisoformat(linha["expira_em"]) < datetime.now(UTC):
            raise SessaoInvalida()
        return linha["login"]

    def encerrar(self, token: str) -> None:
        with conectar(self._banco) as conexao:
            conexao.execute("DELETE FROM acesso_sessoes WHERE resumo = ?", (_resumo(token),))


def _resumo(token: str) -> str:
    # só o resumo vai para o banco: se o arquivo vazar, as sessões abertas não podem ser usadas
    return hashlib.sha256(token.encode()).hexdigest()
