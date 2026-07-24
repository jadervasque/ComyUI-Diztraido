"""No composto para executar o grupo PROCESSAMENTO em uma unica etapa."""

from __future__ import annotations

from ..services.composed_pipelines import run_processing_pipeline

try:
    import comfy.samplers

    SAMPLERS = list(comfy.samplers.KSampler.SAMPLERS)
except ImportError:
    SAMPLERS = ["euler"]


class DiztraidoProcessingBundle:
    """Agrupa noise, sampler, scheduler, latent e decode em um unico no."""

    CATEGORY = "Diztraido/flux"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "process"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model": ("MODEL",),
                "conditioning": ("CONDITIONING",),
                "vae": ("VAE",),
                "noise_seed": ("INT", {"default": 0, "min": 0, "max": 9_223_372_036_854_775_807}),
                "sampler_name": (SAMPLERS,),
                "steps": ("INT", {"default": 20, "min": 1, "max": 10_000}),
                "width": ("INT", {"default": 1024, "min": 8, "max": 16384}),
                "height": ("INT", {"default": 1024, "min": 8, "max": 16384}),
                "batch_size": ("INT", {"default": 1, "min": 1, "max": 4096}),
            },
        }

    def process(self, model, conditioning, vae, noise_seed, sampler_name, steps, width, height, batch_size):
        image = run_processing_pipeline(
            model,
            conditioning,
            vae,
            noise_seed,
            sampler_name,
            steps,
            width,
            height,
            batch_size,
        )
        return (image,)
