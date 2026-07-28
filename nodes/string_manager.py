"""Prompt and resolution manager for multi-image workflows."""

from __future__ import annotations

from typing import Any

from .resolution_selector import (
    ASPECT_RATIO_OPTIONS,
    DEFAULT_ASPECT_RATIO,
    DEFAULT_HEIGHT,
    DEFAULT_MEGAPIXELS,
    DEFAULT_MULTIPLE,
    DEFAULT_WIDTH,
    RESOLUTION_TYPE,
    build_resolution_config,
)

MAX_FIELDS = 24


def _clamp_selection(value: Any, maximum: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        parsed = 1
    return max(1, min(parsed, maximum))


class DiztraidoStringManager:
    """Select one prompt and its associated resolution configuration."""

    CATEGORY = "Diztraido/utils"
    DESCRIPTION = (
        "Store multiple prompts with independent resolution settings and select one pair."
    )
    RETURN_TYPES = ("STRING", RESOLUTION_TYPE)
    RETURN_NAMES = ("string_selected", "resolution_selected")
    FUNCTION = "select"

    @classmethod
    def INPUT_TYPES(cls):
        optional: dict[str, Any] = {}
        for index in range(1, MAX_FIELDS + 1):
            optional[f"string_{index}"] = (
                "STRING",
                {"default": "", "multiline": True},
            )
            optional[f"aspect_ratio_{index}"] = (
                ASPECT_RATIO_OPTIONS,
                {"default": DEFAULT_ASPECT_RATIO},
            )
            optional[f"megapixels_{index}"] = (
                "FLOAT",
                {
                    "default": DEFAULT_MEGAPIXELS,
                    "min": 0.1,
                    "max": 16.0,
                    "step": 0.1,
                },
            )
            optional[f"multiple_{index}"] = (
                "INT",
                {
                    "default": DEFAULT_MULTIPLE,
                    "min": 8,
                    "max": 128,
                    "step": 4,
                    "advanced": True,
                },
            )
            optional[f"width_{index}"] = (
                "INT",
                {
                    "default": DEFAULT_WIDTH,
                    "min": 8,
                    "max": 16384,
                    "step": 8,
                },
            )
            optional[f"height_{index}"] = (
                "INT",
                {
                    "default": DEFAULT_HEIGHT,
                    "min": 8,
                    "max": 16384,
                    "step": 8,
                },
            )

        return {
            "required": {
                "num_fields": (
                    "INT",
                    {"default": 5, "min": 1, "max": MAX_FIELDS, "step": 1},
                ),
                "selected_string": (
                    "INT",
                    {"default": 1, "min": 1, "max": MAX_FIELDS, "step": 1},
                ),
            },
            "optional": optional,
        }

    def select(self, num_fields: Any, selected_string: Any, **kwargs: Any):
        field_count = _clamp_selection(num_fields, MAX_FIELDS)
        selected = _clamp_selection(selected_string, field_count)

        prompt = str(kwargs.get(f"string_{selected}", "") or "")
        resolution = build_resolution_config(
            aspect_ratio=kwargs.get(f"aspect_ratio_{selected}", DEFAULT_ASPECT_RATIO),
            megapixels=kwargs.get(f"megapixels_{selected}", DEFAULT_MEGAPIXELS),
            multiple=kwargs.get(f"multiple_{selected}", DEFAULT_MULTIPLE),
            width=kwargs.get(f"width_{selected}", DEFAULT_WIDTH),
            height=kwargs.get(f"height_{selected}", DEFAULT_HEIGHT),
        )
        return prompt, resolution
