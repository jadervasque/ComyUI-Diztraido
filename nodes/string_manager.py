"""Prompt and aspect-ratio manager for multi-image workflows."""

from __future__ import annotations

from typing import Any

from .resolution_selector import ASPECT_RATIOS

MAX_FIELDS = 24
MANAGED_ASPECT_RATIOS = list(ASPECT_RATIOS)
DEFAULT_ASPECT_RATIO = "1:1 (Square)"


def _clamp_selection(value: Any, maximum: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        parsed = 1
    return max(1, min(parsed, maximum))


def _normalize_aspect_ratio(value: Any) -> str:
    aspect_ratio = str(value or DEFAULT_ASPECT_RATIO)
    if aspect_ratio not in MANAGED_ASPECT_RATIOS:
        return DEFAULT_ASPECT_RATIO
    return aspect_ratio


class DiztraidoStringManager:
    """Select one prompt and its associated aspect-ratio option."""

    CATEGORY = "Diztraido/utils"
    DESCRIPTION = (
        "Store multiple prompts with independent aspect ratios and select one pair."
    )
    RETURN_TYPES = ("STRING", MANAGED_ASPECT_RATIOS)
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
                MANAGED_ASPECT_RATIOS,
                {"default": DEFAULT_ASPECT_RATIO},
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
        aspect_ratio = _normalize_aspect_ratio(
            kwargs.get(f"aspect_ratio_{selected}", DEFAULT_ASPECT_RATIO)
        )
        return prompt, aspect_ratio
