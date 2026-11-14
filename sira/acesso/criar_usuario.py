"""Cadastra um usuário do sistema: python -m sira.acesso.criar_usuario <login>"""

import argparse
import sqlite3
import sys
from getpass import getpass

from sira.acesso.servico import cadastrar_usuario
from sira.acesso.sqlite import UsuariosSqlite
from sira.banco import CAMINHO

TAMANHO_MINIMO = 8


def main(login: str) -> None:
    senha = getpass("Senha: ")
    if len(senha) < TAMANHO_MINIMO:
        sys.exit(f"Use uma senha com pelo menos {TAMANHO_MINIMO} caracteres.")
    if senha != getpass("Repita a senha: "):
        sys.exit("As senhas não conferem.")
    try:
        cadastrar_usuario(UsuariosSqlite(CAMINHO), login, senha)
    except sqlite3.IntegrityError:
        sys.exit(f"O login {login} já existe.")
    print(f"Usuário {login} cadastrado.")


if __name__ == "__main__":
    argumentos = argparse.ArgumentParser(description="Cadastra um usuário do SIRA-TB.")
    argumentos.add_argument("login")
    main(argumentos.parse_args().login)
