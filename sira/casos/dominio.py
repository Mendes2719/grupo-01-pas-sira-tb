"""Caso notificado, com a estimativa congelada no momento do cadastro."""

from dataclasses import dataclass
from datetime import date, datetime
from typing import Self

from sira.risco import Estimativa, FaixaDeRisco

FAIXAS_PRIORITARIAS = (FaixaDeRisco.ALTO, FaixaDeRisco.MUITO_ALTO)


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


@dataclass(frozen=True)
class Indicadores:
    total: int
    alto_ou_muito_alto: int
    probabilidade_media: float
    por_faixa: dict[FaixaDeRisco, int]

    @classmethod
    def das_faixas(cls, casos_por_faixa: dict[FaixaDeRisco, int], soma: float) -> Self:
        total = sum(casos_por_faixa.values())
        return cls(
            total=total,
            alto_ou_muito_alto=sum(casos_por_faixa.get(faixa, 0) for faixa in FAIXAS_PRIORITARIAS),
            probabilidade_media=round(soma / total, 4) if total else 0.0,
            por_faixa={faixa: casos_por_faixa.get(faixa, 0) for faixa in FaixaDeRisco},
        )


class CasoNaoEncontrado(Exception):
    def __init__(self, id_caso: int):
        super().__init__(f"caso {id_caso} não encontrado")
