"""Adaptador do preditor herdado do Projeto Integrador (ADR 0003)."""

from legado.prever import Preditor
from sira.risco.dominio import DadosInvalidos, Estimativa, FaixaDeRisco, Fator


class PreditorDoPI:
    """Adapta o Preditor do PI, que trabalha com dicionários, à porta EstimadorDeRisco."""

    def __init__(self, preditor: Preditor):
        self._preditor = preditor

    @property
    def versao(self) -> str:
        return self._preditor.meta["versao"]

    def campos(self) -> dict:
        return self._preditor.campos

    def estimar(self, notificacao: dict) -> Estimativa:
        try:
            resposta = self._preditor.prever(notificacao)
        except ValueError as erro:
            raise DadosInvalidos(str(erro)) from erro
        return Estimativa(
            probabilidade=resposta["probabilidade"],
            faixa=FaixaDeRisco(resposta["faixa"]),
            percentil=resposta["percentil"],
            fatores=tuple(_traduzir_fator(fator) for fator in resposta["fatores"]),
            avisos=tuple(resposta["avisos"]),
            versao_modelo=self.versao,
        )


def _traduzir_fator(fator: dict) -> Fator:
    # o peso em log-odds e o efeito em texto ficam no legado: o sinal dos pontos já diz o efeito
    return Fator(
        nome=fator["fator"],
        valor=str(fator["valor"]),
        pontos_percentuais=fator["pontos_percentuais"],
    )
