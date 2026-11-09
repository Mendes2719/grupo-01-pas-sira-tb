"""Adaptador HTTP do módulo de risco."""

from fastapi import APIRouter

from sira.risco.preditor_pi import PreditorDoPI


def criar_rotas(preditor: PreditorDoPI) -> APIRouter:
    rotas = APIRouter(tags=["risco"])

    @rotas.get("/campos")
    def campos() -> dict:
        """Campos da ficha de notificação, valores aceitos e quais são obrigatórios."""
        return preditor.campos()

    return rotas
