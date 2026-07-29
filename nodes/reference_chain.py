"""Composite node for encoding prompts and chaining FLUX.2 references."""

from __future__ import annotations

import os

import folder_paths

from ..services.composed_pipelines import MAX_REFERENCES
from ..services.reference_conditioning import build_reference_conditioning_from_prompt


class DiztraidoReferenceChain:
    """Encode positive conditioning, append references, and create a blank negative."""

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
        # Keep only the combo box. Direct uploads belong to the optional IMAGE sockets.
        return ([""] + sorted(image_files), {})

    @classmethod
    def INPUT_TYPES(cls):
        image_options = cls._image_options()
        required = {
            "clip": ("CLIP",),
            "vae": ("VAE",),
            "text_prompt": ("STRING", {"default": "", "multiline": True}),
            "reference_count": ("INT", {"default": 0, "min": 0, "max": MAX_REFERENCES}),
        }
        optional = {}
        for index in range(1, MAX_REFERENCES + 1):
            required[f"image_ref_{index}"] = image_options
            optional[f"image_input_{index}"] = ("IMAGE",)

        return {"required": required, "optional": optional}

    def apply_references(self, clip, vae, text_prompt, reference_count, **kwargs):
        positive, blank_negative = build_reference_conditioning_from_prompt(
            clip=clip,
            text_prompt=text_prompt,
            vae=vae,
            reference_count=reference_count,
            **kwargs,
        )
        return positive, blank_negative
