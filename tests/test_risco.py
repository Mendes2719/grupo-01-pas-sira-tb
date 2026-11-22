"""O adaptador traduz a resposta do preditor do PI sem mudar a estimativa."""

import pytest

from sira.risco import DadosInvalidos, FaixaDeRisco
from sira.risco.cronometro import EstimadorCronometrado
from sira.risco.preditor_pi import PreditorDoPI


@pytest.fixture
def adaptador(preditor):
    return PreditorDoPI(preditor)


def test_traduz_a_resposta_para_o_dominio(adaptador, preditor, exemplo):
    estimativa = adaptador.estimar(exemplo)
    assert estimativa.probabilidade == preditor.prever(exemplo)["probabilidade"]
    assert estimativa.faixa is FaixaDeRisco.MUITO_ALTO
    assert estimativa.fatores[0].nome == "Tipo de entrada"
    assert estimativa.versao_modelo == "2.0"


def test_erro_do_legado_vira_dados_invalidos(adaptador, exemplo):
    with pytest.raises(DadosInvalidos, match="sexo"):
        adaptador.estimar({**exemplo, "sexo": "Outro"})


def test_cronometro_devolve_a_mesma_estimativa_e_repassa_o_erro(adaptador, exemplo):
    cronometrado = EstimadorCronometrado(adaptador)
    assert cronometrado.estimar(exemplo) == adaptador.estimar(exemplo)
    with pytest.raises(DadosInvalidos):
        cronometrado.estimar({**exemplo, "sexo": "Outro"})
