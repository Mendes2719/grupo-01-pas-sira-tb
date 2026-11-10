"""Estimativa de risco de abandono no vocabulário do SIRA-TB."""

from dataclasses import dataclass
from enum import Enum


class FaixaDeRisco(Enum):
    BAIXO = "Baixo"
    MODERADO = "Moderado"
    ALTO = "Alto"
    MUITO_ALTO = "Muito alto"


@dataclass(frozen=True)
class Fator:
    nome: str
    valor: str
    pontos_percentuais: float


@dataclass(frozen=True)
class Estimativa:
    probabilidade: float
    faixa: FaixaDeRisco
    percentil: int
    fatores: tuple[Fator, ...]
    avisos: tuple[str, ...]
    versao_modelo: str


class DadosInvalidos(Exception):
    """A ficha tem campo obrigatório ausente ou valor fora das opções aceitas."""
