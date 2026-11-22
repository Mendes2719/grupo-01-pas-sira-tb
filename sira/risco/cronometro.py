"""Decorador que mede cada estimativa sem mexer no estimador que ele envolve."""

import logging
from time import perf_counter

from sira.risco.dominio import Estimativa
from sira.risco.portas import EstimadorDeRisco

LIMITE_MS = 1000  # RNF03: a estimativa com a explicação aparece em até 1 segundo

log = logging.getLogger("sira.risco")


class EstimadorCronometrado:
    def __init__(self, estimador: EstimadorDeRisco, limite_ms: float = LIMITE_MS):
        self._estimador = estimador
        self._limite_ms = limite_ms

    def estimar(self, notificacao: dict) -> Estimativa:
        inicio = perf_counter()
        estimativa = self._estimador.estimar(notificacao)
        duracao_ms = round((perf_counter() - inicio) * 1000, 1)
        nivel = logging.WARNING if duracao_ms > self._limite_ms else logging.INFO
        dados = {"duracao_ms": duracao_ms, "versao_modelo": estimativa.versao_modelo}
        log.log(nivel, "estimativa", extra={"dados": dados})
        return estimativa
