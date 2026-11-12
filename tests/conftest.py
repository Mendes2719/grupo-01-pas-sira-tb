import json
from datetime import datetime
from pathlib import Path

import pytest

from legado.prever import Preditor
from sira.casos import Caso
from sira.risco import Estimativa, FaixaDeRisco, Fator

EXEMPLO = Path(__file__).parents[1] / "exemplos" / "paciente_exemplo.json"


@pytest.fixture(scope="session")
def preditor() -> Preditor:
    return Preditor()


@pytest.fixture
def exemplo() -> dict:
    return json.loads(EXEMPLO.read_text(encoding="utf-8"))


@pytest.fixture
def nova_estimativa():
    def criar(probabilidade: float = 0.3, faixa: FaixaDeRisco = FaixaDeRisco.ALTO) -> Estimativa:
        fatores = (Fator("Idade", "34", 2.5),)
        return Estimativa(probabilidade, faixa, 60, fatores, (), "teste")

    return criar


@pytest.fixture
def novo_caso(nova_estimativa):
    def criar(
        probabilidade: float = 0.3,
        faixa: FaixaDeRisco = FaixaDeRisco.ALTO,
        data: str = "2026-09-10",
        municipio: str = "350950",
    ) -> Caso:
        notificacao = {"data_notificacao": data, "municipio_residencia": municipio}
        estimativa = nova_estimativa(probabilidade, faixa)
        return Caso("260001", notificacao, estimativa, "ana", datetime(2026, 9, 10, 8, 30))

    return criar
