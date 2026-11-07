"""Função de aptidão dos ADRs 0001 e 0002: o CI falha quando uma importação quebra a fronteira."""

import ast
from pathlib import Path

SIRA = Path(__file__).parents[1] / "sira"
MODULOS = {pasta.name for pasta in SIRA.iterdir() if (pasta / "__init__.py").exists()}
TECNOLOGIA = {"fastapi", "pydantic", "sqlite3", "xgboost", "pandas", "legado"}


def importacoes(arquivo: Path) -> set[str]:
    nomes = set()
    for no in ast.walk(ast.parse(arquivo.read_text(encoding="utf-8"))):
        if isinstance(no, ast.Import):
            nomes.update(apelido.name for apelido in no.names)
        elif isinstance(no, ast.ImportFrom) and no.module:
            nomes.add(no.module)
    return nomes


def interno_de_outro_modulo(nome: str, modulo: str) -> bool:
    partes = nome.split(".")
    return partes[0] == "sira" and len(partes) > 2 and partes[1] in MODULOS - {modulo}


def test_modulo_so_importa_a_interface_publica_dos_outros():
    violacoes = [
        f"{modulo}/{arquivo.name} importa {nome}"
        for modulo in MODULOS
        for arquivo in (SIRA / modulo).glob("*.py")
        for nome in importacoes(arquivo)
        if interno_de_outro_modulo(nome, modulo)
    ]
    assert not violacoes


def test_dominio_e_portas_nao_dependem_de_tecnologia():
    violacoes = [
        f"{arquivo.parent.name}/{arquivo.name} importa {nome}"
        for arquivo in [*SIRA.glob("*/dominio.py"), *SIRA.glob("*/portas.py")]
        for nome in importacoes(arquivo)
        if nome.split(".")[0] in TECNOLOGIA
    ]
    assert not violacoes
