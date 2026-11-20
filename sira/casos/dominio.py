"""Caso notificado, com a estimativa congelada no momento do cadastro."""

from dataclasses import dataclass
from datetime import date, datetime

from sira.risco import Estimativa, FaixaDeRisco


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


@dataclass(frozen=True)
class FiltroDeCasos:
    """Recorte da lista priorizada; campo vazio não filtra."""

    faixa: FaixaDeRisco | None = None
    desde: date | None = None
    ate: date | None = None
    municipio: str | None = None


class CasoNaoEncontrado(Exception):
    def __init__(self, id_caso: int):
        super().__init__(f"caso {id_caso} não encontrado")
