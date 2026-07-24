"""No composto para carregar modelos Flux.2."""

from __future__ import annotations

from ..services.model_loaders import build_flux2_loader_schema, load_flux2_models


class DiztraidoLoadFlux2Models:
    """Agrupa UNETLoader, CLIPLoader e VAELoader para Flux.2."""

    CATEGORY = "Diztraido/flux"
    RETURN_TYPES = ("MODEL", "CLIP", "VAE")
    RETURN_NAMES = ("model", "clip", "vae")
    FUNCTION = "load"

    @classmethod
    def INPUT_TYPES(cls):
        required, _ = build_flux2_loader_schema()
        return {"required": required}

    def load(self, **kwargs):
        model, clip, vae = load_flux2_models(**kwargs)
        return model, clip, vae
