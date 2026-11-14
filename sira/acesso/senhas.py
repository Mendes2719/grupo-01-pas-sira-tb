"""Hash de senha com PBKDF2 e sal: a senha nunca é guardada em texto puro (RNF01)."""

import hashlib
import hmac
import secrets

ITERACOES = 600_000  # valor recomendado pela OWASP para PBKDF2-HMAC-SHA256


def gerar_hash(senha: str) -> str:
    sal = secrets.token_hex(16)
    return f"{sal}${_derivar(senha, sal)}"


def confere(senha: str, hash_guardado: str) -> bool:
    sal, esperado = hash_guardado.split("$")
    # compare_digest gasta o mesmo tempo com qualquer senha errada e não indica o quanto ela acertou
    return hmac.compare_digest(_derivar(senha, sal), esperado)


def _derivar(senha: str, sal: str) -> str:
    return hashlib.pbkdf2_hmac("sha256", senha.encode(), sal.encode(), ITERACOES).hex()
