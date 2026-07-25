"""No composto para encadear multiplas referencias com guidance embutido."""

from __future__ import annotations

import os

import folder_paths

from ..services.composed_pipelines import MAX_REFERENCES, build_reference_conditioning_from_prompt


class DiztraidoReferenceChain:
    """Aplica FluxGuidance + cadeia de ReferenceLatent em um unico no."""

    CATEGORY = "Diztraido/flux"
    RETURN_TYPES = ("CONDITIONING", "VAE")
    RETURN_NAMES = ("conditioning", "vae")
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
            "text_prompt": ("STRING", {"default": "", "multiline": True}),
            "vae": ("VAE",),
            "guidance": ("FLOAT", {"default": 4.0, "min": 0.0, "max": 100.0, "step": 0.1}),
            "reference_count": ("INT", {"default": 0, "min": 0, "max": MAX_REFERENCES}),
        }
        for index in range(1, MAX_REFERENCES + 1):
            required[f"image_ref_{index}"] = image_options

        return {
            "required": required,
            "optional": {
                "initial_latent": ("LATENT",),
            },
        }

    def apply_references(self, clip, text_prompt, vae, guidance, reference_count, initial_latent=None, **kwargs):
        result = build_reference_conditioning_from_prompt(
            clip,
            text_prompt,
            vae,
            guidance,
            reference_count,
            initial_latent=initial_latent,
            **kwargs,
        )
        return result, vae
