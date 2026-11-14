"""Portas do módulo de acesso."""

from typing import Protocol

from sira.acesso.dominio import Usuario


class RepositorioDeUsuarios(Protocol):
    def buscar(self, login: str) -> Usuario | None: ...

    def adicionar(self, usuario: Usuario) -> None: ...


class Sessoes(Protocol):
    def abrir(self, login: str) -> str: ...

    def dono(self, token: str) -> str: ...
