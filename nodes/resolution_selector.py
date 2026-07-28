"""Extended resolution selector and reusable resolution configuration helpers."""

from __future__ import annotations

import math
from collections.abc import Mapping
from typing import Any

CUSTOM_ASPECT_RATIO = "Custom"
RESOLUTION_TYPE = "DIZTRAIDO_RESOLUTION"
DEFAULT_ASPECT_RATIO = "1:1 (Square)"
DEFAULT_MEGAPIXELS = 1.0
DEFAULT_MULTIPLE = 8
DEFAULT_WIDTH = 1024
DEFAULT_HEIGHT = 1024

ASPECT_RATIOS: dict[str, tuple[int, int]] = {
    "1:1 (Square)": (1, 1),
    "2:3 (Portrait Photo)": (2, 3),
    "3:2 (Photo)": (3, 2),
    "3:4 (Portrait Standard)": (3, 4),
    "4:3 (Standard)": (4, 3),
    "9:16 (Portrait Widescreen)": (9, 16),
    "16:9 (Widescreen)": (16, 9),
    "21:9 (Ultrawide)": (21, 9),
    "5:4 (Classic Landscape)": (5, 4),
    "4:5 (Social Portrait)": (4, 5),
    "7:5 (Photo Landscape)": (7, 5),
    "5:7 (Photo Portrait)": (5, 7),
    "10:8 (Classic Landscape)": (10, 8),
    "8:10 (Classic Portrait)": (8, 10),
    "8:5 (Wide Landscape)": (8, 5),
    "5:8 (Tall Portrait)": (5, 8),
    "3:1 (Panoramic Landscape)": (3, 1),
    "1:3 (Panoramic Portrait)": (1, 3),
    "2:1 (Wide Panorama)": (2, 1),
    "1:2 (Tall Panorama)": (1, 2),
    "7:6 (Compact Landscape)": (7, 6),
    "6:7 (Compact Portrait)": (6, 7),
}
ASPECT_RATIO_OPTIONS = [*ASPECT_RATIOS, CUSTOM_ASPECT_RATIO]


def _clamp_int(value: Any, default: int, minimum: int, maximum: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return max(minimum, min(parsed, maximum))


def _clamp_float(value: Any, default: float, minimum: float, maximum: float) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return default
    return max(minimum, min(parsed, maximum))


def build_resolution_config(
    aspect_ratio: Any = DEFAULT_ASPECT_RATIO,
    megapixels: Any = DEFAULT_MEGAPIXELS,
    multiple: Any = DEFAULT_MULTIPLE,
    width: Any = DEFAULT_WIDTH,
    height: Any = DEFAULT_HEIGHT,
) -> dict[str, Any]:
    """Build a normalized configuration accepted by resolution-aware nodes."""
    normalized_ratio = str(aspect_ratio or DEFAULT_ASPECT_RATIO)
    if normalized_ratio not in ASPECT_RATIO_OPTIONS:
        normalized_ratio = DEFAULT_ASPECT_RATIO

    return {
        "aspect_ratio": normalized_ratio,
        "megapixels": _clamp_float(megapixels, DEFAULT_MEGAPIXELS, 0.1, 16.0),
        "multiple": _clamp_int(multiple, DEFAULT_MULTIPLE, 8, 128),
        "width": _clamp_int(width, DEFAULT_WIDTH, 8, 16384),
        "height": _clamp_int(height, DEFAULT_HEIGHT, 8, 16384),
    }


def normalize_resolution_config(
    resolution: Any,
    fallback: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Normalize a resolution object while preserving a caller-provided fallback."""
    base = dict(fallback or build_resolution_config())
    if not isinstance(resolution, Mapping):
        return build_resolution_config(**base)

    return build_resolution_config(
        aspect_ratio=resolution.get("aspect_ratio", base.get("aspect_ratio")),
        megapixels=resolution.get("megapixels", base.get("megapixels")),
        multiple=resolution.get("multiple", base.get("multiple")),
        width=resolution.get("width", base.get("width")),
        height=resolution.get("height", base.get("height")),
    )


def resolve_resolution(
    aspect_ratio: str,
    megapixels: float,
    multiple: int,
    width: int = DEFAULT_WIDTH,
    height: int = DEFAULT_HEIGHT,
    resolution: Any | None = None,
) -> tuple[int, int]:
    """Resolve dimensions from local widgets or a connected resolution object."""
    config = build_resolution_config(aspect_ratio, megapixels, multiple, width, height)
    if resolution is not None:
        config = normalize_resolution_config(resolution, fallback=config)

    if config["aspect_ratio"] == CUSTOM_ASPECT_RATIO:
        return config["width"], config["height"]

    width_ratio, height_ratio = ASPECT_RATIOS[config["aspect_ratio"]]
    total_pixels = config["megapixels"] * 1024 * 1024
    scale = math.sqrt(total_pixels / (width_ratio * height_ratio))
    target_multiple = config["multiple"]
    resolved_width = max(
        target_multiple,
        round(width_ratio * scale / target_multiple) * target_multiple,
    )
    resolved_height = max(
        target_multiple,
        round(height_ratio * scale / target_multiple) * target_multiple,
    )
    return resolved_width, resolved_height


class DiztraidoResolutionSelector:
    """Resolve width and height from widgets or a connected resolution object."""

    CATEGORY = "Diztraido/utils"
    DESCRIPTION = (
        "Calculate width and height from an aspect ratio and megapixel target, "
        "enter exact dimensions in Custom mode, or consume a connected resolution."
    )
    RETURN_TYPES = ("INT", "INT")
    RETURN_NAMES = ("width", "height")
    FUNCTION = "calculate"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "aspect_ratio": (ASPECT_RATIO_OPTIONS, {"default": DEFAULT_ASPECT_RATIO}),
                "megapixels": (
                    "FLOAT",
                    {"default": DEFAULT_MEGAPIXELS, "min": 0.1, "max": 16.0, "step": 0.1},
                ),
                "multiple": (
                    "INT",
                    {"default": DEFAULT_MULTIPLE, "min": 8, "max": 128, "step": 4, "advanced": True},
                ),
                "width": (
                    "INT",
                    {"default": DEFAULT_WIDTH, "min": 8, "max": 16384, "step": 8},
                ),
                "height": (
                    "INT",
                    {"default": DEFAULT_HEIGHT, "min": 8, "max": 16384, "step": 8},
                ),
            },
            "optional": {
                "resolution": (RESOLUTION_TYPE,),
            },
        }

    @classmethod
    def calculate(
        cls,
        aspect_ratio: str,
        megapixels: float,
        multiple: int,
        width: int = DEFAULT_WIDTH,
        height: int = DEFAULT_HEIGHT,
        resolution: Any | None = None,
    ):
        return resolve_resolution(
            aspect_ratio,
            megapixels,
            multiple,
            width,
            height,
            resolution=resolution,
        )
