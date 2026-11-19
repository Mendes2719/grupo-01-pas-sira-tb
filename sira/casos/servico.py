"""Casos de uso do módulo de casos."""

from datetime import datetime

from sira.casos.dominio import Caso, CasoNaoEncontrado, FiltroDeCasos
from sira.casos.portas import RepositorioDeCasos
from sira.risco import EstimadorDeRisco


class ServicoDeCasos:
    def __init__(self, repositorio: RepositorioDeCasos, estimador: EstimadorDeRisco):
        self._repositorio = repositorio
        self._estimador = estimador

    def cadastrar(self, identificador: str, notificacao: dict, usuario: str) -> Caso:
        estimativa = self._estimador.estimar(notificacao)
        caso = Caso(identificador, notificacao, estimativa, usuario, datetime.now().astimezone())
        return self._repositorio.adicionar(caso)

    def detalhar(self, id_caso: int) -> Caso:
        caso = self._repositorio.buscar(id_caso)
        if caso is None:
            raise CasoNaoEncontrado(id_caso)
        return caso

    def listar_priorizados(self, filtro: FiltroDeCasos) -> list[Caso]:
        return self._repositorio.listar(filtro)
