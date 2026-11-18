"""Portas do módulo de casos."""

from datetime import date
from typing import Protocol

from sira.casos.dominio import Caso
from sira.risco import FaixaDeRisco


class RepositorioDeCasos(Protocol):
    def adicionar(self, caso: Caso) -> Caso: ...

    def buscar(self, id_caso: int) -> Caso | None: ...

    def listar(
        self,
        faixa: FaixaDeRisco | None,
        desde: date | None,
        ate: date | None,
        municipio: str | None,
    ) -> list[Caso]: ...
