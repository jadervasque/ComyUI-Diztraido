"""Orquestracao de pipelines compostos usando nos nativos do ComfyUI."""

from __future__ import annotations

import inspect
from typing import Any, Callable

MAX_REFERENCES = 16
DEFAULT_RESOLUTION = 1024
DEFAULT_STEPS = 50
DEFAULT_CFG = 4.0
DEFAULT_BATCH = 1


def clamp_int(value: Any, default: int, minimum: int, maximum: int) -> int:
    """Converte e limita valores inteiros para manter parametros validos."""
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return max(minimum, min(parsed, maximum))


def clamp_float(value: Any, default: float, minimum: float, maximum: float) -> float:
    """Converte e limita valores de ponto flutuante."""
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return default
    return max(minimum, min(parsed, maximum))


def extract_result(value: Any, index: int = 0) -> Any:
    """Extrai a saida principal de retornos tuple/list/dict dos nos."""
    if isinstance(value, dict) and "result" in value:
        value = value["result"]

    if not isinstance(value, dict) and hasattr(value, "result"):
        value = value.result

    # Outputs do ComfyUI costumam vir em tuple; ja tipos de dados validos,
    # como CONDITIONING, podem ser list e nao devem ser truncados.
    if isinstance(value, tuple):
        return value[index]
    return value


def is_conditioning_list(value: Any) -> bool:
    """Detecta estrutura de CONDITIONING esperada pelo ComfyUI."""
    if not isinstance(value, list):
        return False
    if not value:
        return True
    for item in value:
        if not isinstance(item, (list, tuple)) or len(item) < 2:
            return False
        if not isinstance(item[1], dict):
            return False
    return True


def normalize_conditioning(value: Any) -> Any:
    """Normaliza condicionamento para evitar listas aninhadas de um unico output."""
    if isinstance(value, dict) and "result" in value:
        value = value["result"]

    if isinstance(value, tuple) and len(value) == 1 and is_conditioning_list(value[0]):
        return value[0]

    if is_conditioning_list(value):
        return value

    if (
        isinstance(value, list)
        and len(value) == 1
        and isinstance(value[0], list)
        and is_conditioning_list(value[0])
    ):
        return value[0]

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
    reference_count: Any,
    *,
    node_factory: Callable[[str], Any] | None = None,
    **kwargs: Any,
) -> Any:
    """Encadeia ReferenceLatent para todas as imagens de referencia ativas."""
    factory = node_factory or _default_node_factory
    current_conditioning = normalize_conditioning(conditioning)

    images = collect_reference_images(reference_count, kwargs)
    if not images:
        return current_conditioning

    load_image = factory("LoadImage")
    vae_encode = factory("VAEEncode")
    reference_latent = factory("ReferenceLatent")

    for image_name in images:
        loaded_image = extract_result(
            call_node(load_image, image=image_name, upload="image"),
        )
        latent = extract_result(call_node(vae_encode, pixels=loaded_image, vae=vae))
        current_conditioning = extract_result(
            call_node(reference_latent, conditioning=current_conditioning, latent=latent),
        )
        current_conditioning = normalize_conditioning(current_conditioning)

    return current_conditioning


def build_reference_conditioning_from_prompt(
    clip: Any,
    text_prompt: Any,
    vae: Any,
    reference_count: Any,
    *,
    node_factory: Callable[[str], Any] | None = None,
    **kwargs: Any,
) -> tuple[Any, Any]:
    """Codifica o prompt positivo, adiciona referencias e cria negativo vazio."""
    factory = node_factory or _default_node_factory
    clip_text_encode = factory("CLIPTextEncode")

    positive = extract_result(
        call_node(
            clip_text_encode,
            clip=clip,
            text=str(text_prompt or ""),
        ),
    )
    positive = build_reference_conditioning(
        conditioning=positive,
        vae=vae,
        reference_count=reference_count,
        node_factory=factory,
        **kwargs,
    )

    blank_negative = extract_result(
        call_node(
            clip_text_encode,
            clip=clip,
            text="",
        ),
    )
    blank_negative = normalize_conditioning(blank_negative)
    return positive, blank_negative


def normalize_processing_params(
    noise_seed: Any,
    sampler_name: Any,
    steps: Any,
    cfg: Any,
    width: Any,
    height: Any,
    batch_size: Any,
) -> dict[str, Any]:
    """Normaliza parametros do pipeline de processamento para faixas validas."""
    return {
        "noise_seed": clamp_int(noise_seed, default=0, minimum=0, maximum=9_223_372_036_854_775_807),
        "sampler_name": str(sampler_name or "euler"),
        "steps": clamp_int(steps, default=DEFAULT_STEPS, minimum=1, maximum=10_000),
        "cfg": clamp_float(cfg, default=DEFAULT_CFG, minimum=0.0, maximum=100.0),
        "width": clamp_int(width, default=DEFAULT_RESOLUTION, minimum=8, maximum=16384),
        "height": clamp_int(height, default=DEFAULT_RESOLUTION, minimum=8, maximum=16384),
        "batch_size": clamp_int(batch_size, default=DEFAULT_BATCH, minimum=1, maximum=4096),
    }


def run_processing_pipeline(
    model: Any,
    positive: Any,
    negative: Any,
    vae: Any,
    noise_seed: Any,
    sampler_name: Any,
    steps: Any,
    cfg: Any,
    width: Any,
    height: Any,
    batch_size: Any,
    *,
    decode_image: bool = True,
    node_factory: Callable[[str], Any] | None = None,
) -> tuple[Any | None, Any]:
    """Executa CFGGuider + sampler selecionado + Flux2Scheduler e decode opcional."""
    factory = node_factory or _default_node_factory
    params = normalize_processing_params(
        noise_seed,
        sampler_name,
        steps,
        cfg,
        width,
        height,
        batch_size,
    )
    positive = normalize_conditioning(positive)
    negative = normalize_conditioning(negative)

    random_noise = factory("RandomNoise")
    cfg_guider = factory("CFGGuider")
    sampler_select = factory("KSamplerSelect")
    flux_scheduler = factory("Flux2Scheduler")
    empty_latent = factory("EmptyFlux2LatentImage")
    sampler_advanced = factory("SamplerCustomAdvanced")

    noise = extract_result(call_node(random_noise, noise_seed=params["noise_seed"]))
    guider = extract_result(
        call_node(
            cfg_guider,
            model=model,
            positive=positive,
            negative=negative,
            cfg=params["cfg"],
        ),
    )
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

    image = None
    if decode_image:
        if vae is None:
            raise ValueError("Connect a VAE when the image output is in use.")
        vae_decode = factory("VAEDecode")
        image = extract_result(call_node(vae_decode, samples=sampled, vae=vae))

    return image, sampled
