"""Orquestracao de pipelines compostos usando nos nativos do ComfyUI."""

from __future__ import annotations

import inspect
from typing import Any, Callable

MAX_REFERENCES = 16
DEFAULT_RESOLUTION = 1024
DEFAULT_STEPS = 20
DEFAULT_BATCH = 1


def clamp_int(value: Any, default: int, minimum: int, maximum: int) -> int:
    """Converte e limita valores inteiros para manter parametros validos."""
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return max(minimum, min(parsed, maximum))


def extract_result(value: Any, index: int = 0) -> Any:
    """Extrai a saida principal de retornos tuple/list/dict dos nos."""
    if isinstance(value, dict) and "result" in value:
        value = value["result"]
    if isinstance(value, (tuple, list)):
        return value[index]
    return value


def _default_node_factory(node_name: str) -> Any:
    """Resolve classes de nos nativos a partir do registro global do ComfyUI."""
    import nodes as comfy_nodes

    mappings = getattr(comfy_nodes, "NODE_CLASS_MAPPINGS", {})
    node_class = mappings.get(node_name) or getattr(comfy_nodes, node_name, None)
    if node_class is None:
        raise ValueError(f"No nativo nao encontrado: {node_name}")
    return node_class()


def call_node(node: Any, **kwargs: Any) -> Any:
    """Invoca o metodo funcional do no, filtrando kwargs nao suportados."""
    function_name = getattr(node, "FUNCTION", None)
    if not function_name:
        raise ValueError(f"No sem atributo FUNCTION: {node.__class__.__name__}")

    method = getattr(node, function_name)
    signature = inspect.signature(method)

    # Alguns nos do ComfyUI expoem wrappers com assinatura (*args, **kwargs).
    # Nesses casos, filtrar por nomes remove todos os argumentos obrigatorios.
    if any(
        parameter.kind == inspect.Parameter.VAR_KEYWORD
        for parameter in signature.parameters.values()
    ):
        return method(**kwargs)

    accepted = {
        name: value
        for name, value in kwargs.items()
        if name in signature.parameters
    }
    return method(**accepted)


def collect_reference_images(reference_count: Any, kwargs: dict[str, Any]) -> list[str]:
    """Coleta referencias ativas na ordem definida pelo usuario."""
    count = clamp_int(reference_count, default=0, minimum=0, maximum=MAX_REFERENCES)
    images: list[str] = []
    for index in range(1, count + 1):
        image_name = kwargs.get(f"image_ref_{index}")
        if isinstance(image_name, str) and image_name.strip():
            images.append(image_name.strip())
    return images


def build_reference_conditioning(
    conditioning: Any,
    vae: Any,
    guidance: Any,
    reference_count: Any,
    *,
    initial_latent: Any | None = None,
    node_factory: Callable[[str], Any] | None = None,
    **kwargs: Any,
) -> Any:
    """Aplica guidance e encadeia multiplos ReferenceLatent a partir de imagens."""
    factory = node_factory or _default_node_factory

    flux_guidance = factory("FluxGuidance")
    current_conditioning = extract_result(
        call_node(flux_guidance, conditioning=conditioning, guidance=float(guidance)),
    )

    reference_latent = factory("ReferenceLatent")
    if initial_latent is not None:
        current_conditioning = extract_result(
            call_node(
                reference_latent,
                conditioning=current_conditioning,
                latent=initial_latent,
            ),
        )

    images = collect_reference_images(reference_count, kwargs)
    if not images:
        return current_conditioning

    load_image = factory("LoadImage")
    vae_encode = factory("VAEEncode")

    for image_name in images:
        loaded_image = extract_result(
            call_node(load_image, image=image_name, upload="image"),
        )
        latent = extract_result(call_node(vae_encode, pixels=loaded_image, vae=vae))
        current_conditioning = extract_result(
            call_node(reference_latent, conditioning=current_conditioning, latent=latent),
        )

    return current_conditioning


def build_reference_conditioning_from_prompt(
    clip: Any,
    text_prompt: Any,
    vae: Any,
    guidance: Any,
    reference_count: Any,
    *,
    initial_latent: Any | None = None,
    node_factory: Callable[[str], Any] | None = None,
    **kwargs: Any,
) -> Any:
    """Gera conditioning via CLIPTextEncode e aplica cadeia de referencias."""
    factory = node_factory or _default_node_factory

    clip_text_encode = factory("CLIPTextEncode")
    conditioning = extract_result(
        call_node(
            clip_text_encode,
            clip=clip,
            text=str(text_prompt or ""),
        ),
    )

    return build_reference_conditioning(
        conditioning=conditioning,
        vae=vae,
        guidance=guidance,
        reference_count=reference_count,
        initial_latent=initial_latent,
        node_factory=factory,
        **kwargs,
    )


def normalize_processing_params(
    noise_seed: Any,
    sampler_name: Any,
    steps: Any,
    width: Any,
    height: Any,
    batch_size: Any,
) -> dict[str, Any]:
    """Normaliza parametros do pipeline de processamento para faixas validas."""
    return {
        "noise_seed": clamp_int(noise_seed, default=0, minimum=0, maximum=9_223_372_036_854_775_807),
        "sampler_name": str(sampler_name or "euler"),
        "steps": clamp_int(steps, default=DEFAULT_STEPS, minimum=1, maximum=10_000),
        "width": clamp_int(width, default=DEFAULT_RESOLUTION, minimum=8, maximum=16384),
        "height": clamp_int(height, default=DEFAULT_RESOLUTION, minimum=8, maximum=16384),
        "batch_size": clamp_int(batch_size, default=DEFAULT_BATCH, minimum=1, maximum=4096),
    }


def run_processing_pipeline(
    model: Any,
    conditioning: Any,
    vae: Any,
    noise_seed: Any,
    sampler_name: Any,
    steps: Any,
    width: Any,
    height: Any,
    batch_size: Any,
    *,
    node_factory: Callable[[str], Any] | None = None,
) -> Any:
    """Replica o grupo PROCESSAMENTO em um unico ponto de execucao."""
    factory = node_factory or _default_node_factory
    params = normalize_processing_params(noise_seed, sampler_name, steps, width, height, batch_size)

    random_noise = factory("RandomNoise")
    basic_guider = factory("BasicGuider")
    sampler_select = factory("KSamplerSelect")
    flux_scheduler = factory("Flux2Scheduler")
    empty_latent = factory("EmptyFlux2LatentImage")
    sampler_advanced = factory("SamplerCustomAdvanced")
    vae_decode = factory("VAEDecode")

    noise = extract_result(call_node(random_noise, noise_seed=params["noise_seed"]))
    guider = extract_result(call_node(basic_guider, model=model, conditioning=conditioning))
    sampler = extract_result(call_node(sampler_select, sampler_name=params["sampler_name"]))
    sigmas = extract_result(
        call_node(
            flux_scheduler,
            steps=params["steps"],
            width=params["width"],
            height=params["height"],
        ),
    )
    latent_image = extract_result(
        call_node(
            empty_latent,
            width=params["width"],
            height=params["height"],
            batch_size=params["batch_size"],
        ),
    )
    sampled = extract_result(
        call_node(
            sampler_advanced,
            noise=noise,
            guider=guider,
            sampler=sampler,
            sigmas=sigmas,
            latent_image=latent_image,
        ),
    )

    return extract_result(call_node(vae_decode, samples=sampled, vae=vae))
