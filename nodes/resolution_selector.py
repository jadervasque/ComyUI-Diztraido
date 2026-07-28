"""Seletor de resolucao com proporcoes estendidas e modo personalizado."""

from __future__ import annotations

import math
from typing import Any

CUSTOM_ASPECT_RATIO = "Custom"

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


def resolve_resolution(
    aspect_ratio: str,
    megapixels: float,
    multiple: int,
    width: int = 1024,
    height: int = 1024,
) -> tuple[int, int]:
    """Resolve dimensoes por megapixels ou usa dimensoes diretas no modo Custom."""
    if aspect_ratio == CUSTOM_ASPECT_RATIO:
        return (
            _clamp_int(width, default=1024, minimum=8, maximum=16384),
            _clamp_int(height, default=1024, minimum=8, maximum=16384),
        )

    if aspect_ratio not in ASPECT_RATIOS:
        aspect_ratio = "1:1 (Square)"

    width_ratio, height_ratio = ASPECT_RATIOS[aspect_ratio]
    try:
        target_megapixels = float(megapixels)
    except (TypeError, ValueError):
        target_megapixels = 1.0
    target_megapixels = max(0.1, min(target_megapixels, 16.0))
    target_multiple = _clamp_int(multiple, default=8, minimum=8, maximum=128)
    total_pixels = target_megapixels * 1024 * 1024
    scale = math.sqrt(total_pixels / (width_ratio * height_ratio))
    resolved_width = max(target_multiple, round(width_ratio * scale / target_multiple) * target_multiple)
    resolved_height = max(target_multiple, round(height_ratio * scale / target_multiple) * target_multiple)
    return resolved_width, resolved_height


class DiztraidoResolutionSelector:
    """Calcula largura e altura por proporcao/megapixels ou medidas diretas."""

    CATEGORY = "Diztraido/utils"
    DESCRIPTION = (
        "Calculate width and height from aspect ratio and megapixel target, "
        "or enter exact dimensions in Custom mode."
    )
    RETURN_TYPES = ("INT", "INT")
    RETURN_NAMES = ("width", "height")
    FUNCTION = "calculate"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
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
            },
        }

    @classmethod
    def calculate(
        cls,
        aspect_ratio: str,
        megapixels: float,
        multiple: int,
        width: int = 1024,
        height: int = 1024,
    ):
        return resolve_resolution(aspect_ratio, megapixels, multiple, width, height)
