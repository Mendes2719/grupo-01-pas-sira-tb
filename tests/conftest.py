import json
from pathlib import Path

import pytest

from legado.prever import Preditor

EXEMPLO = Path(__file__).parents[1] / "exemplos" / "paciente_exemplo.json"


@pytest.fixture(scope="session")
def preditor() -> Preditor:
    return Preditor()


@pytest.fixture
def exemplo() -> dict:
    return json.loads(EXEMPLO.read_text(encoding="utf-8"))
