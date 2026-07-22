"""Nó avançado para leitura de metadados de imagens."""

from __future__ import annotations

import hashlib

from ..services.image_metadata import as_float, as_int, read_image_metadata
from .image_input import image_input_types, validate_image

try:
    import comfy.samplers

    SAMPLER_RETURN_TYPE = comfy.samplers.KSampler.SAMPLERS
    SCHEDULER_RETURN_TYPE = comfy.samplers.KSampler.SCHEDULERS
except ImportError:
    SAMPLER_RETURN_TYPE = "STRING"
    SCHEDULER_RETURN_TYPE = "STRING"


class DiztraidoImageMetadataReaderAdvanced:
    """Lê prompts e parâmetros de geração de uma imagem selecionada."""

    CATEGORY = "Diztraido/image"
    RETURN_TYPES = (
        "STRING", "STRING", "INT", "INT", "FLOAT", SAMPLER_RETURN_TYPE,
        SCHEDULER_RETURN_TYPE, "STRING", "INT", "INT", "STRING", "STRING",
    )
    RETURN_NAMES = (
        "prompt", "negative_prompt", "seed", "steps", "cfg", "sampler_name",
        "scheduler", "model", "width", "height", "metadata_text", "metadata_json",
    )
    FUNCTION = "read_metadata"

    @classmethod
    def INPUT_TYPES(cls):
        return image_input_types()

    @classmethod
    def IS_CHANGED(cls, image):
        from folder_paths import get_annotated_filepath

        image_path = get_annotated_filepath(image)
        with open(image_path, "rb") as image_file:
            digest = hashlib.file_digest(image_file, "sha256").hexdigest()
        return digest

    @classmethod
    def VALIDATE_INPUTS(cls, image):
        return validate_image(image)

    def read_metadata(self, image):
        from folder_paths import get_annotated_filepath

        result = read_image_metadata(get_annotated_filepath(image))
        details = result["details"]
        return {
            "ui": {"text": [result["metadata_text"]]},
            "result": (
                result["prompt"], result["negative_prompt"], as_int(details.get("seed")),
                as_int(details.get("steps")), as_float(details.get("cfg")),
                str(details.get("sampler", "")), str(details.get("scheduler", "")),
                str(details.get("model", "")), as_int(details.get("width")),
                as_int(details.get("height")), result["metadata_text"], result["metadata_json"],
            ),
        }
