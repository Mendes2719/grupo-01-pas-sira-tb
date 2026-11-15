"""Caso notificado, com a estimativa congelada no momento do cadastro."""

from dataclasses import dataclass
from datetime import date, datetime

from sira.risco import Estimativa


@dataclass(frozen=True)
class Caso:
    identificador: str
    notificacao: dict
    estimativa: Estimativa
    cadastrado_por: str
    cadastrado_em: datetime
    id: int | None = None

    @property
    def data_notificacao(self) -> date:
        return date.fromisoformat(self.notificacao["data_notificacao"])

    @property
    def municipio(self) -> str:
        return str(self.notificacao["municipio_residencia"])


class CasoNaoEncontrado(Exception):
    def __init__(self, id_caso: int):
        super().__init__(f"caso {id_caso} não encontrado")
