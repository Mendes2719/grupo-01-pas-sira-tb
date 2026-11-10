"""Porta pela qual os outros módulos pedem uma estimativa de risco."""

from typing import Protocol

from sira.risco.dominio import Estimativa


class EstimadorDeRisco(Protocol):
    def estimar(self, notificacao: dict) -> Estimativa: ...
