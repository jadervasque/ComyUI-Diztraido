"""No composto para executar o sampler FLUX.2 em uma unica etapa."""

from __future__ import annotations

from .resolution_selector import ASPECT_RATIO_OPTIONS, resolve_resolution
from ..services.composed_pipelines import run_processing_pipeline

try:
    import comfy.samplers

    SAMPLERS = list(comfy.samplers.KSampler.SAMPLERS)
except ImportError:
    SAMPLERS = ["euler"]

_MISSING = object()


class DiztraidoProcessingBundle:
    """Agrupa CFG, sampler, Flux2Scheduler, latent e decode opcional."""

    CATEGORY = "Diztraido/flux"
    RETURN_TYPES = ("IMAGE", "LATENT")
    RETURN_NAMES = ("image", "latent")
    FUNCTION = "process"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model": ("MODEL",),
                "positive": ("CONDITIONING",),
                "negative": ("CONDITIONING",),
                "noise_seed": (
                    "INT",
                    {"default": 0, "min": 0, "max": 9_223_372_036_854_775_807},
                ),
                "cfg": (
                    "FLOAT",
                    {"default": 4.0, "min": 0.0, "max": 100.0, "step": 0.1},
                ),
                "sampler_name": (SAMPLERS, {"default": "euler"}),
                "steps": ("INT", {"default": 50, "min": 1, "max": 10_000}),
                "aspect_ratio": (ASPECT_RATIO_OPTIONS, {"default": "1:1 (Square)"}),
                "megapixels": (
                    "FLOAT",
                    {"default": 1.0, "min": 0.1, "max": 16.0, "step": 0.1},
                ),
                "multiple": (
                    "INT",
                    {"default": 8, "min": 8, "max": 128, "step": 4, "advanced": True},
                ),
                "width": (
                    "INT",
                    {"default": 1024, "min": 8, "max": 16384, "step": 8},
                ),
                "height": (
                    "INT",
                    {"default": 1024, "min": 8, "max": 16384, "step": 8},
                ),
                "batch_size": ("INT", {"default": 1, "min": 1, "max": 4096}),
                # Sincronizado automaticamente pelo frontend conforme a saida IMAGE.
                "decode_image": ("BOOLEAN", {"default": True}),
            },
            "optional": {
                # Lazy evita carregar/processar o VAE quando apenas LATENT esta conectado.
                "vae": ("VAE", {"lazy": True}),
            },
        }

    def check_lazy_status(self, decode_image, vae=_MISSING, **kwargs):
        if bool(decode_image) and vae is None:
            return ["vae"]
        return []

    def process(
        self,
        model,
        positive,
        negative,
        noise_seed,
        cfg,
        sampler_name,
        steps,
        aspect_ratio,
        megapixels,
        multiple,
        width,
        height,
        batch_size,
        decode_image=True,
        vae=_MISSING,
    ):
        resolved_width, resolved_height = resolve_resolution(
            aspect_ratio,
            megapixels,
            multiple,
            width,
            height,
        )

        should_decode = bool(decode_image)
        if should_decode and vae in (_MISSING, None):
            raise ValueError(
                "Connect a VAE to Flux Sampler while the image output is connected. "
                "The VAE is optional when only the latent output is used."
            )

        image, latent = run_processing_pipeline(
            model=model,
            positive=positive,
            negative=negative,
            vae=None if vae is _MISSING else vae,
            noise_seed=noise_seed,
            sampler_name=sampler_name,
            steps=steps,
            cfg=cfg,
            width=resolved_width,
            height=resolved_height,
            batch_size=batch_size,
            decode_image=should_decode,
        )
        return image, latent
