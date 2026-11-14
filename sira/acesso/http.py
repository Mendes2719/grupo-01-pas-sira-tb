"""Adaptador HTTP do módulo de acesso."""

from collections.abc import Callable
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from sira.acesso.servico import ServicoDeAcesso

Portador = Annotated[HTTPAuthorizationCredentials, Depends(HTTPBearer())]


class Credenciais(BaseModel):
    login: str
    senha: str


def criar_rotas(acesso: ServicoDeAcesso) -> APIRouter:
    rotas = APIRouter(tags=["acesso"])

    @rotas.post("/login")
    def entrar(credenciais: Credenciais) -> dict[str, str]:
        return {"token": acesso.entrar(credenciais.login, credenciais.senha)}

    return rotas


def exigir_login(acesso: ServicoDeAcesso) -> Callable[..., str]:
    def usuario_logado(portador: Portador) -> str:
        return acesso.usuario_da_sessao(portador.credentials)

    return usuario_logado
