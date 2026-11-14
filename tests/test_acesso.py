"""Login com SQLite temporário."""

import pytest

from sira.acesso import CredenciaisInvalidas
from sira.acesso.servico import ServicoDeAcesso, cadastrar_usuario
from sira.acesso.sessoes_jwt import SessoesJwt
from sira.acesso.sqlite import UsuariosSqlite


@pytest.fixture
def acesso(tmp_path):
    usuarios = UsuariosSqlite(tmp_path / "acesso.db")
    cadastrar_usuario(usuarios, "ana", "senha-de-teste")
    return ServicoDeAcesso(usuarios, SessoesJwt("chave-de-teste-com-mais-de-32-caracteres"))


def test_login_abre_a_sessao_do_usuario(acesso):
    token = acesso.entrar("ana", "senha-de-teste")
    assert acesso.usuario_da_sessao(token) == "ana"


def test_senha_errada_nao_entra(acesso):
    with pytest.raises(CredenciaisInvalidas):
        acesso.entrar("ana", "senha-errada")
