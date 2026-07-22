"""Rotas HTTP expostas pela extensão."""

from .metadata import register_metadata_routes


def register_routes() -> None:
    """Registra as rotas da extensão quando carregada pelo ComfyUI."""
    register_metadata_routes()
