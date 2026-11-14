"""Usuário do sistema e os erros de acesso."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Usuario:
    login: str
    hash_da_senha: str


class CredenciaisInvalidas(Exception):
    def __init__(self):
        super().__init__("login ou senha incorretos")


class SessaoInvalida(Exception):
    def __init__(self):
        super().__init__("sessão inexistente ou expirada, faça login de novo")
