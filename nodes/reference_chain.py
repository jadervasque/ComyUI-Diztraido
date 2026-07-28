"""No composto para codificar prompt e encadear referencias FLUX.2."""

from __future__ import annotations

import os

import folder_paths

from ..services.composed_pipelines import MAX_REFERENCES, build_reference_conditioning_from_prompt


class DiztraidoReferenceChain:
    """Codifica positivo, adiciona ReferenceLatent e gera negativo vazio."""

    CATEGORY = "Diztraido/flux"
    RETURN_TYPES = ("CONDITIONING", "CONDITIONING")
    RETURN_NAMES = ("positive", "blank_negative")
    FUNCTION = "apply_references"

    @staticmethod
    def _image_options() -> tuple[list[str], dict[str, bool]]:
        input_dir = folder_paths.get_input_directory()
        files = [
            name
            for name in os.listdir(input_dir)
            if os.path.isfile(os.path.join(input_dir, name))
        ]
        image_files = folder_paths.filter_files_content_types(files, ["image"])
        return ([""] + sorted(image_files), {"image_upload": True})

    @classmethod
    def INPUT_TYPES(cls):
        image_options = cls._image_options()
        required = {
            "clip": ("CLIP",),
            "vae": ("VAE",),
            "text_prompt": ("STRING", {"default": "", "multiline": True}),
            "reference_count": ("INT", {"default": 0, "min": 0, "max": MAX_REFERENCES}),
        }
        for index in range(1, MAX_REFERENCES + 1):
            required[f"image_ref_{index}"] = image_options

        return {"required": required}

    def apply_references(self, clip, vae, text_prompt, reference_count, **kwargs):
        positive, blank_negative = build_reference_conditioning_from_prompt(
            clip=clip,
            text_prompt=text_prompt,
            vae=vae,
            reference_count=reference_count,
            **kwargs,
        )
        return positive, blank_negative
