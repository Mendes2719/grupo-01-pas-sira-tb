"""
API do SIRA-TB.

Rodar:        python -m uvicorn api:app --app-dir api --reload   (a partir da raiz do projeto)
Documentacao: http://localhost:8000/docs  (da para testar tudo por la)

  GET  /saude      status e metricas do modelo carregado
  GET  /campos     campos do formulario, valores aceitos e quais sao obrigatorios
  POST /prever     risco de um paciente
  POST /priorizar  varios pacientes, ordenados do maior para o menor risco

O esquema de entrada e montado a partir de modelo/metadados.json:
se o modelo for retreinado com outras categorias, a API acompanha
sem precisar mudar este arquivo.
"""

from datetime import date
from typing import Literal, Optional, Union

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ConfigDict, create_model

from prever import Preditor

preditor = Preditor()

TIPOS = {"data": date, "numero": float, "municipio": str, "escolaridade": Union[int, str]}

def _campo(info):
    t = Literal[tuple(info["valores"])] if info["tipo"] == "categoria" else TIPOS[info["tipo"]]
    # obrigatorio precisa vir preenchido; opcional aceita null = ignorado
    return (t, ...) if info["obrigatorio"] else (Optional[t], None)


Paciente = create_model(
    "Paciente",
    __config__=ConfigDict(extra="forbid"),   # campo com nome errado vira erro, nao some calado
    id=(Optional[str], None),                # identificador do caso; nao entra no modelo
    **{nome: _campo(info) for nome, info in preditor.campos.items()},
)

app = FastAPI(title="SIRA-TB",
              description="Risco de abandono do tratamento de tuberculose",
              version=preditor.meta["versao"])

# o front roda em outra porta durante o desenvolvimento.
# Em producao, trocar "*" pelo endereco do front.
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


def _dados(p):
    return p.model_dump(exclude={"id"}, exclude_none=True)


@app.get("/saude")
def saude():
    m = preditor.meta
    return {"status": "ok", "versao": m["versao"], "treinado_em": m["treinado_em"],
            "anos_treino": m["anos_treino"], "metricas_teste_2023": m["metricas"]}


@app.get("/campos")
def campos():
    return preditor.campos


@app.post("/prever")
def prever(paciente: Paciente):
    try:
        return {"id": paciente.id, **preditor.prever(_dados(paciente))}
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@app.post("/priorizar")
def priorizar(pacientes: list[Paciente]):
    try:
        resultados = preditor.prever_lote([_dados(p) for p in pacientes], n_fatores=3)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    for p, r in zip(pacientes, resultados):
        r["id"] = p.id
    return sorted(resultados, key=lambda r: -r["probabilidade"])
