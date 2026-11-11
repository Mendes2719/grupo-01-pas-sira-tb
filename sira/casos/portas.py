"""Portas do módulo de casos."""

from typing import Protocol

from sira.casos.dominio import Caso


class RepositorioDeCasos(Protocol):
    def adicionar(self, caso: Caso) -> Caso: ...

    def buscar(self, id_caso: int) -> Caso | None: ...
