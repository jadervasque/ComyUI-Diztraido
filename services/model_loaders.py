"""Servicos para composicao de nos de carregamento de modelos Flux."""

from __future__ import annotations

import copy
import inspect
from typing import Any, Callable

MAX_LORAS = 16


def _default_node_factory(node_name: str) -> Any:
    import nodes as comfy_nodes

    mappings = getattr(comfy_nodes, "NODE_CLASS_MAPPINGS", {})
    node_class = mappings.get(node_name) or getattr(comfy_nodes, node_name, None)
    if node_class is None:
        raise ValueError(f"No nativo nao encontrado: {node_name}")
    return node_class()


def _default_node_class_resolver(node_name: str) -> Any:
    import nodes as comfy_nodes

    mappings = getattr(comfy_nodes, "NODE_CLASS_MAPPINGS", {})
    node_class = mappings.get(node_name) or getattr(comfy_nodes, node_name, None)
    if node_class is None:
        raise ValueError(f"Classe do no nativo nao encontrada: {node_name}")
    return node_class


def call_node(node: Any, **kwargs: Any) -> Any:
    """Invoca o metodo funcional do no filtrando kwargs suportados."""
    function_name = getattr(node, "FUNCTION", None)
    if not function_name:
        raise ValueError(f"No sem atributo FUNCTION: {node.__class__.__name__}")

    method = getattr(node, function_name)
    signature = inspect.signature(method)

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


def extract_result(value: Any, index: int = 0) -> Any:
    if isinstance(value, dict) and "result" in value:
        value = value["result"]

    if not isinstance(value, dict) and hasattr(value, "result"):
        value = value.result

    # Mesma regra dos pipelines: apenas tuple representa envelope de outputs.
    if isinstance(value, tuple):
        return value[index]
    return value


def _required_inputs_for(node_name: str, resolver: Callable[[str], Any] | None = None) -> dict[str, Any]:
    resolver_func = resolver or _default_node_class_resolver
    node_class = resolver_func(node_name)
    input_types = node_class.INPUT_TYPES()
    required = input_types.get("required", {})
    return copy.deepcopy(required)


def _override_default(required_inputs: dict[str, Any], field_name: str, default_value: Any) -> dict[str, Any]:
    if field_name not in required_inputs:
        return required_inputs

    definition = required_inputs[field_name]
    if not isinstance(definition, tuple) or len(definition) < 2 or not isinstance(definition[1], dict):
        return required_inputs

    new_config = copy.deepcopy(definition[1])
    new_config["default"] = default_value
    required_inputs[field_name] = (definition[0], new_config)
    return required_inputs


def build_flux2_loader_schema(
    resolver: Callable[[str], Any] | None = None,
) -> tuple[dict[str, Any], dict[str, list[str]]]:
    """Monta schema do no composto Flux.2 com defaults ajustados."""
    model_inputs = _required_inputs_for("UNETLoader", resolver)
    clip_inputs = _required_inputs_for("CLIPLoader", resolver)
    clip_inputs = _override_default(clip_inputs, "type", "flux2")
    vae_inputs = _required_inputs_for("VAELoader", resolver)

    required: dict[str, Any] = {}
    required.update(model_inputs)
    required.update(clip_inputs)
    required.update(vae_inputs)

    sections = {
        "model": list(model_inputs.keys()),
        "clip": list(clip_inputs.keys()),
        "vae": list(vae_inputs.keys()),
    }
    return required, sections


def build_flux2_lora_loader_schema(
    resolver: Callable[[str], Any] | None = None,
    lora_options: tuple[list[str], dict[str, Any]] | None = None,
) -> tuple[dict[str, Any], dict[str, list[str]]]:
    """Monta schema Flux.2 com campos dinamicos predefinidos para LoRAs."""
    required, sections = build_flux2_loader_schema(resolver)
    return _add_lora_inputs(required, sections, resolver, lora_options)


def _add_lora_inputs(
    required: dict[str, Any],
    sections: dict[str, list[str]],
    resolver: Callable[[str], Any] | None = None,
    lora_options: tuple[list[str], dict[str, Any]] | None = None,
) -> tuple[dict[str, Any], dict[str, list[str]]]:
    lora_select = lora_options or _required_inputs_for("LoraLoader", resolver)["lora_name"]
    lora_choices = list(lora_select[0]) if isinstance(lora_select, tuple) else []
    if "" not in lora_choices:
        lora_choices = [""] + lora_choices
    lora_select = (lora_choices, copy.deepcopy(lora_select[1]) if isinstance(lora_select, tuple) and len(lora_select) > 1 else {})

    required["lora_count"] = ("INT", {"default": 0, "min": 0, "max": MAX_LORAS})

    lora_keys: list[str] = []
    for index in range(1, MAX_LORAS + 1):
        lora_name = f"lora_{index}"
        strength_model = f"strength_model_{index}"
        strength_clip = f"strength_clip_{index}"
        required[lora_name] = lora_select
        required[strength_model] = ("FLOAT", {"default": 1.0, "min": -100.0, "max": 100.0, "step": 0.01})
        required[strength_clip] = ("FLOAT", {"default": 1.0, "min": -100.0, "max": 100.0, "step": 0.01})
        lora_keys.extend([lora_name, strength_model, strength_clip])

    sections["loras"] = lora_keys
    return required, sections


def build_flux1_loader_schema(
    resolver: Callable[[str], Any] | None = None,
) -> tuple[dict[str, Any], dict[str, list[str]]]:
    """Monta schema do no composto Flux.1 com defaults ajustados."""
    model_inputs = _required_inputs_for("UNETLoader", resolver)
    clip_inputs = _required_inputs_for("DualCLIPLoader", resolver)
    clip_inputs = _override_default(clip_inputs, "type", "flux")
    vae_inputs = _required_inputs_for("VAELoader", resolver)

    required: dict[str, Any] = {}
    required.update(model_inputs)
    required.update(clip_inputs)
    required.update(vae_inputs)

    sections = {
        "model": list(model_inputs.keys()),
        "clip": list(clip_inputs.keys()),
        "vae": list(vae_inputs.keys()),
    }
    return required, sections


def build_flux1_lora_loader_schema(
    resolver: Callable[[str], Any] | None = None,
    lora_options: tuple[list[str], dict[str, Any]] | None = None,
) -> tuple[dict[str, Any], dict[str, list[str]]]:
    """Monta schema Flux.1 com campos dinamicos predefinidos para LoRAs."""
    required, sections = build_flux1_loader_schema(resolver)
    return _add_lora_inputs(required, sections, resolver, lora_options)


def _pick_values(keys: list[str], values: dict[str, Any]) -> dict[str, Any]:
    return {key: values[key] for key in keys if key in values}


def load_flux2_models(
    *,
    node_factory: Callable[[str], Any] | None = None,
    resolver: Callable[[str], Any] | None = None,
    **kwargs: Any,
) -> tuple[Any, Any, Any]:
    """Carrega MODEL, CLIP e VAE para Flux.2."""
    factory = node_factory or _default_node_factory
    _, sections = build_flux2_loader_schema(resolver)

    unet_loader = factory("UNETLoader")
    clip_loader = factory("CLIPLoader")
    vae_loader = factory("VAELoader")

    model = extract_result(call_node(unet_loader, **_pick_values(sections["model"], kwargs)))
    clip = extract_result(call_node(clip_loader, **_pick_values(sections["clip"], kwargs)))
    vae = extract_result(call_node(vae_loader, **_pick_values(sections["vae"], kwargs)))
    return model, clip, vae


def _active_lora_values(values: dict[str, Any]) -> list[dict[str, Any]]:
    try:
        count = int(values.get("lora_count", 0))
    except (TypeError, ValueError):
        count = 0
    count = max(0, min(count, MAX_LORAS))

    loras: list[dict[str, Any]] = []
    for index in range(1, count + 1):
        lora_name = values.get(f"lora_{index}")
        if not isinstance(lora_name, str) or not lora_name.strip():
            continue
        strength_model = float(values.get(f"strength_model_{index}", 1.0))
        strength_clip = float(values.get(f"strength_clip_{index}", strength_model))
        if strength_model == 0 and strength_clip == 0:
            continue
        loras.append({
            "lora_name": lora_name.strip(),
            "strength_model": strength_model,
            "strength_clip": strength_clip,
        })
    return loras


def load_flux2_models_with_loras(
    *,
    node_factory: Callable[[str], Any] | None = None,
    resolver: Callable[[str], Any] | None = None,
    **kwargs: Any,
) -> tuple[Any, Any, Any]:
    """Carrega modelos Flux.2 e aplica LoRAs sequencialmente em MODEL/CLIP."""
    factory = node_factory or _default_node_factory
    model, clip, vae = load_flux2_models(node_factory=factory, resolver=resolver, **kwargs)
    lora_loader = factory("LoraLoader")

    for lora_values in _active_lora_values(kwargs):
        loaded = call_node(
            lora_loader,
            model=model,
            clip=clip,
            **lora_values,
        )
        model = extract_result(loaded, 0)
        clip = extract_result(loaded, 1)

    return model, clip, vae


def load_flux1_models(
    *,
    node_factory: Callable[[str], Any] | None = None,
    resolver: Callable[[str], Any] | None = None,
    **kwargs: Any,
) -> tuple[Any, Any, Any]:
    """Carrega MODEL, CLIP e VAE para Flux.1 usando DualCLIPLoader."""
    factory = node_factory or _default_node_factory
    _, sections = build_flux1_loader_schema(resolver)

    unet_loader = factory("UNETLoader")
    dual_clip_loader = factory("DualCLIPLoader")
    vae_loader = factory("VAELoader")

    model = extract_result(call_node(unet_loader, **_pick_values(sections["model"], kwargs)))
    clip = extract_result(call_node(dual_clip_loader, **_pick_values(sections["clip"], kwargs)))
    vae = extract_result(call_node(vae_loader, **_pick_values(sections["vae"], kwargs)))
    return model, clip, vae


def load_flux1_models_with_loras(
    *,
    node_factory: Callable[[str], Any] | None = None,
    resolver: Callable[[str], Any] | None = None,
    **kwargs: Any,
) -> tuple[Any, Any, Any]:
    """Carrega modelos Flux.1 e aplica LoRAs sequencialmente em MODEL/CLIP."""
    factory = node_factory or _default_node_factory
    model, clip, vae = load_flux1_models(node_factory=factory, resolver=resolver, **kwargs)
    lora_loader = factory("LoraLoader")

    for lora_values in _active_lora_values(kwargs):
        loaded = call_node(
            lora_loader,
            model=model,
            clip=clip,
            **lora_values,
        )
        model = extract_result(loaded, 0)
        clip = extract_result(loaded, 1)

    return model, clip, vae
