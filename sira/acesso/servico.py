"""Casos de uso do módulo de acesso."""

from sira.acesso.dominio import CredenciaisInvalidas, Usuario
from sira.acesso.portas import RepositorioDeUsuarios, Sessoes
from sira.acesso.senhas import confere, gerar_hash


def cadastrar_usuario(usuarios: RepositorioDeUsuarios, login: str, senha: str) -> None:
    usuarios.adicionar(Usuario(login, gerar_hash(senha)))


class ServicoDeAcesso:
    def __init__(self, usuarios: RepositorioDeUsuarios, sessoes: Sessoes):
        self._usuarios = usuarios
        self._sessoes = sessoes

    def entrar(self, login: str, senha: str) -> str:
        usuario = self._usuarios.buscar(login)
        if usuario is None or not confere(senha, usuario.hash_da_senha):
            raise CredenciaisInvalidas()
        return self._sessoes.abrir(login)

    def usuario_da_sessao(self, token: str) -> str:
        return self._sessoes.dono(token)
