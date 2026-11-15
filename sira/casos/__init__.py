"""Interface pública do módulo de casos: o que os outros módulos podem importar."""

from sira.casos.dominio import Caso, CasoNaoEncontrado

__all__ = ["Caso", "CasoNaoEncontrado"]
