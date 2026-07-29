"""Composite node for loading Flux.2 models and applying LoRAs."""

from __future__ import annotations

from ..services.model_loaders import build_flux2_lora_loader_schema, load_flux2_models_with_loras


def _set_clip_strength_defaults(required):
    for name, definition in list(required.items()):
        if not name.startswith("strength_clip_") or len(definition) < 2:
            continue
        config = dict(definition[1])
        config["default"] = 0.0
        required[name] = (definition[0], config)
    return required


class DiztraidoLoadFlux2ModelsLoras:
    """Combine UNETLoader, CLIPLoader, VAELoader, and multiple Flux.2 LoRAs."""

    CATEGORY = "Diztraido/flux"
    RETURN_TYPES = ("MODEL", "CLIP", "VAE")
    RETURN_NAMES = ("model", "clip", "vae")
    FUNCTION = "load"

    @classmethod
    def INPUT_TYPES(cls):
        required, _ = build_flux2_lora_loader_schema()
        return {"required": _set_clip_strength_defaults(required)}

    def load(self, **kwargs):
        model, clip, vae = load_flux2_models_with_loras(**kwargs)
        return model, clip, vae
