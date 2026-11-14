"""Interface pública do módulo de acesso: o que os outros módulos podem importar."""

from sira.acesso.dominio import CredenciaisInvalidas, SessaoInvalida

__all__ = ["CredenciaisInvalidas", "SessaoInvalida"]
