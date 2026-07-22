"""Utilitários compartilhados para entradas de imagem dos nós."""

from __future__ import annotations

import os

import folder_paths


def image_input_types() -> dict:
    """Cria a entrada padrão do ComfyUI para selecionar ou enviar imagens."""
    input_dir = folder_paths.get_input_directory()
    files = [
        name
        for name in os.listdir(input_dir)
        if os.path.isfile(os.path.join(input_dir, name))
    ]
    image_files = folder_paths.filter_files_content_types(files, ["image"])
    return {"required": {"image": (sorted(image_files), {"image_upload": True})}}


def validate_image(image: str) -> bool | str:
    """Valida um caminho de imagem anotado pelo ComfyUI."""
    if not folder_paths.exists_annotated_filepath(image):
        return f"Invalid image file: {image}"
    return True
