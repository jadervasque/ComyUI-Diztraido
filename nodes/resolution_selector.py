"""Seletor de resolucao com proporcoes estendidas."""

from __future__ import annotations

import math


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


class DiztraidoResolutionSelector:
    """Calcula largura e altura por proporcao e alvo de megapixels."""

    CATEGORY = "Diztraido/utils"
    DESCRIPTION = (
        "Calculate width and height from aspect ratio and megapixel target, "
        "with additional landscape, portrait, and panoramic ratios."
    )
    RETURN_TYPES = ("INT", "INT")
    RETURN_NAMES = ("width", "height")
    FUNCTION = "calculate"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "aspect_ratio": (list(ASPECT_RATIOS), {"default": "1:1 (Square)"}),
                "megapixels": (
                    "FLOAT",
                    {"default": 1.0, "min": 0.1, "max": 16.0, "step": 0.1},
                ),
                "multiple": (
                    "INT",
                    {"default": 8, "min": 8, "max": 128, "step": 4, "advanced": True},
                ),
            },
        }

    @classmethod
    def calculate(cls, aspect_ratio: str, megapixels: float, multiple: int):
        width_ratio, height_ratio = ASPECT_RATIOS[aspect_ratio]
        total_pixels = megapixels * 1024 * 1024
        scale = math.sqrt(total_pixels / (width_ratio * height_ratio))
        width = round(width_ratio * scale / multiple) * multiple
        height = round(height_ratio * scale / multiple) * multiple
        return width, height