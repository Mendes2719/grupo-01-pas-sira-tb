"""Sessão em JWT assinado com HS256 (ADR 0005)."""

from datetime import UTC, datetime, timedelta

import jwt

from sira.acesso.dominio import SessaoInvalida

VALIDADE = timedelta(hours=8)


class SessoesJwt:
    def __init__(self, chave: str):
        self._chave = chave

    def abrir(self, login: str) -> str:
        expira_em = datetime.now(UTC) + VALIDADE
        return jwt.encode({"sub": login, "exp": expira_em}, self._chave, algorithm="HS256")

    def dono(self, token: str) -> str:
        try:
            return jwt.decode(token, self._chave, algorithms=["HS256"])["sub"]
        except jwt.InvalidTokenError as erro:
            raise SessaoInvalida() from erro
