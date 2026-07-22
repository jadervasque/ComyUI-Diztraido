"""Nó visual de leitura instantânea de metadados."""

from __future__ import annotations

from .image_input import image_input_types, validate_image


class DiztraidoMetadataReader:
    """Exibe os metadados completos da imagem sem executar o workflow."""

    CATEGORY = "Diztraido/image"
    DESCRIPTION = (
        "Mostra o JSON completo dos metadados assim que uma imagem é escolhida. "
        "Este nó é somente visual e não possui saídas."
    )
    RETURN_TYPES = ()
    FUNCTION = "inspect"

    @classmethod
    def INPUT_TYPES(cls):
        return image_input_types()

    @classmethod
    def VALIDATE_INPUTS(cls, image):
        return validate_image(image)

    def inspect(self, image):
        """Mantém o nó compatível com a API do ComfyUI sem gerar saídas."""
        return ()
