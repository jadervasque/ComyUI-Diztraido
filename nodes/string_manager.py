"""Prompt and aspect-ratio manager for multi-image workflows."""

from __future__ import annotations

from typing import Any

from .resolution_selector import ASPECT_RATIO_OPTIONS

MAX_FIELDS = 24
DEFAULT_FIELDS = 5
DEFAULT_ASPECT_RATIO = "1:1 (Square)"


def _clamp_integer(value: Any, default: int, minimum: int, maximum: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        parsed = default
    return max(minimum, min(parsed, maximum))


def _normalize_aspect_ratio(value: Any) -> str:
    aspect_ratio = str(value or DEFAULT_ASPECT_RATIO)
    if aspect_ratio not in ASPECT_RATIO_OPTIONS:
        return DEFAULT_ASPECT_RATIO
    return aspect_ratio


class DiztraidoStringManager:
    """Select one prompt and its associated aspect-ratio option."""

    CATEGORY = "Diztraido/utils"
    DESCRIPTION = (
        "Store multiple prompts with independent aspect ratios and select one pair. "
        "Connect resolution_selected directly to the aspect_ratio input of "
        "Resolution Selector Extended."
    )
    RETURN_TYPES = ("STRING", ASPECT_RATIO_OPTIONS)
    RETURN_NAMES = ("string_selected", "resolution_selected")
    FUNCTION = "select"

    @classmethod
    def INPUT_TYPES(cls):
        optional: dict[str, Any] = {}
        for index in range(1, MAX_FIELDS + 1):
            optional[f"string_{index}"] = (
                "STRING",
                {
                    "default": "",
                    "multiline": True,
                    "dynamicPrompts": False,
                    "socketless": True,
                },
            )
            optional[f"aspect_ratio_{index}"] = (
                ASPECT_RATIO_OPTIONS,
                {
                    "default": DEFAULT_ASPECT_RATIO,
                    "socketless": True,
                },
            )

        return {
            "required": {
                "num_fields": (
                    "INT",
                    {
                        "default": DEFAULT_FIELDS,
                        "min": 1,
                        "max": MAX_FIELDS,
                        "step": 1,
                        "socketless": True,
                    },
                ),
                "selected_string": (
                    "INT",
                    {
                        "default": 1,
                        "min": 1,
                        "max": MAX_FIELDS,
                        "step": 1,
                        "control_after_generate": True,
                        "socketless": True,
                    },
                ),
            },
            "optional": optional,
        }

    def select(self, num_fields: Any, selected_string: Any, **kwargs: Any):
        field_count = _clamp_integer(
            num_fields,
            default=DEFAULT_FIELDS,
            minimum=1,
            maximum=MAX_FIELDS,
        )
        selected = _clamp_integer(
            selected_string,
            default=1,
            minimum=1,
            maximum=field_count,
        )

        prompt = str(kwargs.get(f"string_{selected}", "") or "")
        aspect_ratio = _normalize_aspect_ratio(
            kwargs.get(f"aspect_ratio_{selected}", DEFAULT_ASPECT_RATIO)
        )
        return prompt, aspect_ratio
