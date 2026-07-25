"""No composto para carregar modelos Flux.2 e aplicar LoRAs."""

from __future__ import annotations

from ..services.model_loaders import build_flux2_lora_loader_schema, load_flux2_models_with_loras


class DiztraidoLoadFlux2ModelsLoras:
    """Agrupa UNETLoader, CLIPLoader, VAELoader e multiplas LoRAs para Flux.2."""

    CATEGORY = "Diztraido/flux"
    RETURN_TYPES = ("MODEL", "CLIP", "VAE")
    RETURN_NAMES = ("model", "clip", "vae")
    FUNCTION = "load"

    @classmethod
    def INPUT_TYPES(cls):
        required, _ = build_flux2_lora_loader_schema()
        return {"required": required}

    def load(self, **kwargs):
        model, clip, vae = load_flux2_models_with_loras(**kwargs)
        return model, clip, vae
