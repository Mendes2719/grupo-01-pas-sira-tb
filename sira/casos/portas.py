"""Portas do módulo de casos."""

from typing import Protocol

from sira.casos.dominio import Caso, FiltroDeCasos, Indicadores


class RepositorioDeCasos(Protocol):
    def adicionar(self, caso: Caso) -> Caso: ...

    def buscar(self, id_caso: int) -> Caso | None: ...

    def listar(self, filtro: FiltroDeCasos) -> list[Caso]: ...

    def indicadores(self, filtro: FiltroDeCasos) -> Indicadores: ...
