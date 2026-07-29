"""Reference-conditioning composition for file and direct IMAGE sources."""

from __future__ import annotations

from typing import Any, Callable

from .composed_pipelines import (
    MAX_REFERENCES,
    _default_node_factory,
    call_node,
    clamp_int,
    extract_result,
    normalize_conditioning,
)


def collect_reference_sources(
    reference_count: Any,
    kwargs: dict[str, Any],
) -> list[tuple[str, Any]]:
    """Collect active reference sources while preserving the configured order."""
    count = clamp_int(reference_count, default=0, minimum=0, maximum=MAX_REFERENCES)
    sources: list[tuple[str, Any]] = []

    for index in range(1, count + 1):
        direct_image = kwargs.get(f"image_input_{index}")
        if direct_image is not None:
            sources.append(("pixels", direct_image))
            continue

        image_name = kwargs.get(f"image_ref_{index}")
        if isinstance(image_name, str) and image_name.strip():
            sources.append(("file", image_name.strip()))

    return sources


def build_reference_conditioning(
    conditioning: Any,
    vae: Any,
    reference_count: Any,
    *,
    node_factory: Callable[[str], Any] | None = None,
    **kwargs: Any,
) -> Any:
    """Append ReferenceLatent entries from direct IMAGE inputs or selected files."""
    factory = node_factory or _default_node_factory
    current_conditioning = normalize_conditioning(conditioning)
    sources = collect_reference_sources(reference_count, kwargs)
    if not sources:
        return current_conditioning

    vae_encode = factory("VAEEncode")
    reference_latent = factory("ReferenceLatent")
    load_image = None

    for source_type, source_value in sources:
        if source_type == "pixels":
            pixels = source_value
        else:
            if load_image is None:
                load_image = factory("LoadImage")
            pixels = extract_result(
                call_node(load_image, image=source_value, upload="image"),
            )

        latent = extract_result(call_node(vae_encode, pixels=pixels, vae=vae))
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
    """Encode positive text, append references, and encode a blank negative."""
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
    return positive, normalize_conditioning(blank_negative)
