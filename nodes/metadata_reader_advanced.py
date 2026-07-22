"""Nó avançado para leitura de metadados de imagens."""

from __future__ import annotations

import hashlib
import os

import folder_paths

from ..services.image_metadata import as_float, as_int, read_image_metadata

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
        input_dir = folder_paths.get_input_directory()
        files = [name for name in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, name))]
        image_files = folder_paths.filter_files_content_types(files, ["image"])
        return {"required": {"image": (sorted(image_files), {"image_upload": True})}}

    @classmethod
    def IS_CHANGED(cls, image):
        image_path = folder_paths.get_annotated_filepath(image)
        with open(image_path, "rb") as image_file:
            digest = hashlib.file_digest(image_file, "sha256").hexdigest()
        return digest

    @classmethod
    def VALIDATE_INPUTS(cls, image):
        if not folder_paths.exists_annotated_filepath(image):
            return f"Invalid image file: {image}"
        return True

    def read_metadata(self, image):
        result = read_image_metadata(folder_paths.get_annotated_filepath(image))
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
