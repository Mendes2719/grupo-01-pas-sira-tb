"""Teste de caracterização: registra o que o preditor do PI devolve hoje, antes de mexer nele."""

import pytest


def test_exemplo_do_pi_mantem_a_estimativa(preditor, exemplo):
    resposta = preditor.prever(exemplo)
    assert resposta["probabilidade"] == 0.6108
    assert resposta["faixa"] == "Muito alto"
    assert resposta["fatores"][0]["fator"] == "Tipo de entrada"


def test_campo_obrigatorio_ausente_e_recusado(preditor, exemplo):
    del exemplo["tipo_entrada"]
    with pytest.raises(ValueError, match="tipo_entrada"):
        preditor.prever(exemplo)
