"""Ponto único de montagem: escolhe os adaptadores e liga os módulos na aplicação (ADR 0002)."""

from fastapi import FastAPI

app = FastAPI(title="SIRA-TB", description="Risco de abandono do tratamento de tuberculose")
