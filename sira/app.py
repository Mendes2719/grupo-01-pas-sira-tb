"""Ponto único de montagem: escolhe os adaptadores e liga os módulos na aplicação (ADR 0002)."""

from fastapi import FastAPI

from legado.prever import Preditor
from sira.risco import http as risco_http
from sira.risco.preditor_pi import PreditorDoPI

preditor = PreditorDoPI(Preditor())

app = FastAPI(title="SIRA-TB", description="Risco de abandono do tratamento de tuberculose")
app.include_router(risco_http.criar_rotas(preditor))
