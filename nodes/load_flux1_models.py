"""No composto para carregar modelos Flux.1."""

from __future__ import annotations

from ..services.model_loaders import build_flux1_loader_schema, load_flux1_models


class DiztraidoLoadFlux1Models:
    """Agrupa UNETLoader, DualCLIPLoader e VAELoader para Flux.1."""

    CATEGORY = "Diztraido/flux"
    RETURN_TYPES = ("MODEL", "CLIP", "VAE")
    RETURN_NAMES = ("model", "clip", "vae")
    FUNCTION = "load"

    @classmethod
    def INPUT_TYPES(cls):
        required, _ = build_flux1_loader_schema()
        return {"required": required}

    def load(self, **kwargs):
        model, clip, vae = load_flux1_models(**kwargs)
        return model, clip, vae
