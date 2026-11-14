"""Adaptadores SQLite do módulo de acesso."""

from pathlib import Path

from sira.acesso.dominio import Usuario
from sira.banco import conectar


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
