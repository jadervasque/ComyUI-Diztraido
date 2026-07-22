"""Endpoint local para consulta instantânea de metadados de imagens."""

from __future__ import annotations

from typing import Any

import folder_paths

try:
    from ..services.image_metadata import extract_image_metadata
except ImportError:
    # Permite executar os testes diretamente a partir da raiz do repositório.
    from services.image_metadata import extract_image_metadata

METADATA_ROUTE = "/diztraido/metadata"


def read_metadata_for_image(image: str | None) -> tuple[dict[str, Any] | None, str | None]:
    """Lê metadados de uma imagem anotada, sem expor caminhos do servidor."""
    if not image:
        return None, "Informe uma imagem."

    if not folder_paths.exists_annotated_filepath(image):
        return None, "Imagem não encontrada."

    try:
        image_path = folder_paths.get_annotated_filepath(image)
        normalized, _ = extract_image_metadata(image_path)
    except (OSError, ValueError):
        return None, "Não foi possível ler os metadados da imagem."

    return normalized, None


async def get_image_metadata(request):
    """Retorna o JSON completo de metadados da imagem solicitada."""
    from aiohttp import web

    metadata, error = read_metadata_for_image(request.query.get("image"))
    if error:
        return web.json_response({"error": error}, status=400)
    return web.json_response(metadata)


def register_metadata_routes() -> None:
    """Vincula a rota ao servidor somente quando o ComfyUI está disponível."""
    try:
        from server import PromptServer
    except ImportError:
        return

    PromptServer.instance.routes.get(METADATA_ROUTE)(get_image_metadata)
