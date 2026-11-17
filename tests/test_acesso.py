"""Login e logout com SQLite temporário."""

import pytest

from sira.acesso import CredenciaisInvalidas, SessaoInvalida
from sira.acesso.servico import ServicoDeAcesso, cadastrar_usuario
from sira.acesso.sqlite import SessoesSqlite, UsuariosSqlite


@pytest.fixture
def acesso(tmp_path):
    banco = tmp_path / "acesso.db"
    usuarios = UsuariosSqlite(banco)
    cadastrar_usuario(usuarios, "ana", "senha-de-teste")
    return ServicoDeAcesso(usuarios, SessoesSqlite(banco))


def test_login_abre_a_sessao_do_usuario(acesso):
    token = acesso.entrar("ana", "senha-de-teste")
    assert acesso.usuario_da_sessao(token) == "ana"


def test_senha_errada_nao_entra(acesso):
    with pytest.raises(CredenciaisInvalidas):
        acesso.entrar("ana", "senha-errada")


def test_logout_encerra_a_sessao_na_hora(acesso):
    token = acesso.entrar("ana", "senha-de-teste")
    acesso.sair(token)
    with pytest.raises(SessaoInvalida):
        acesso.usuario_da_sessao(token)
