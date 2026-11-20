"""Adaptador HTTP do módulo de casos."""

import json
from collections.abc import Callable
from datetime import date
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict, Field

from sira.casos.dominio import Caso, FiltroDeCasos
from sira.casos.servico import ServicoDeCasos

EXEMPLO = json.loads(
    (Path(__file__).parents[2] / "exemplos" / "paciente_exemplo.json").read_text(encoding="utf-8")
)


class Notificacao(BaseModel):
    """Ficha com os campos de GET /campos, datas no formato AAAA-MM-DD."""

    model_config = ConfigDict(extra="allow")
    data_notificacao: date


class NovoCaso(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={"examples": [{"identificador": "260001234", "notificacao": EXEMPLO}]}
    )
    identificador: str = Field(min_length=1, description="número da notificação no SINAN")
    notificacao: Notificacao


def criar_rotas(casos: ServicoDeCasos, usuario_logado: Callable[..., str]) -> APIRouter:
    rotas = APIRouter(prefix="/casos", tags=["casos"], dependencies=[Depends(usuario_logado)])

    @rotas.post("", status_code=201)
    def cadastrar(novo: NovoCaso, usuario: Annotated[str, Depends(usuario_logado)]) -> Caso:
        notificacao = novo.notificacao.model_dump(mode="json")
        return casos.cadastrar(novo.identificador, notificacao, usuario)

    @rotas.get("")
    def listar(filtro: Annotated[FiltroDeCasos, Depends()]) -> list[Caso]:
        return casos.listar_priorizados(filtro)

    @rotas.get("/{id_caso}")
    def detalhar(id_caso: int) -> Caso:
        return casos.detalhar(id_caso)

    return rotas
