"""No para formatacao posicional com entradas de tipos variados."""

from __future__ import annotations

from typing import Any

from ..services.string_format import format_string


class AnyType(str):
    """Wildcard legado compativel com validacao de tipos do ComfyUI."""

    def __ne__(self, other: object) -> bool:
        return False


ANY_TYPE = AnyType("*")
MAX_INPUTS = 16


class DiztraidoStringFormat:
    """Formata strings com placeholders e condicoes booleanas."""

    CATEGORY = "Diztraido/utils"
    DESCRIPTION = (
        "Substitui {1}, {2}, ...; use {1?} para remover a linha quando a entrada "
        "estiver vazia e @if/@else/@endif para blocos condicionais."
    )
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("string",)
    FUNCTION = "build_string"

    @classmethod
    def INPUT_TYPES(cls):
        optional = {
            f"input_{index}": (ANY_TYPE,)
            for index in range(1, MAX_INPUTS + 1)
        }
        return {
            "required": {
                "template": (
                    "STRING",
                    {
                        "default": "File_{1}_teste_{2}",
                        "multiline": True,
                        "dynamicPrompts": False,
                    },
                ),
                "input_count": (
                    "INT",
                    {"default": 2, "min": 0, "max": MAX_INPUTS, "step": 1},
                ),
                "single_line_output": (
                    "BOOLEAN",
                    {"default": False, "label_on": "enabled", "label_off": "disabled"},
                ),
            },
            "optional": optional,
        }

    def build_string(
        self,
        template: str,
        input_count: int,
        single_line_output: bool = False,
        **kwargs: Any,
    ):
        count = max(0, min(int(input_count), MAX_INPUTS))
        values = [kwargs.get(f"input_{index}") for index in range(1, count + 1)]
        return (format_string(template, values, single_line_output),)
