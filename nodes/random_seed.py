"""Nó gerador de seeds aleatórias."""

from __future__ import annotations

import secrets


class BackendRandomSeed:
    """Gera uma nova seed no backend em cada execução real do workflow."""

    CATEGORY = "utils/random"
    RETURN_TYPES = ("INT", "STRING")
    RETURN_NAMES = ("seed", "seed_text")
    FUNCTION = "generate"

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"maximum": ("INT", {"default": 9_223_372_036_854_775_807, "min": 1, "max": 9_223_372_036_854_775_807})}}

    @classmethod
    def IS_CHANGED(cls, maximum):
        return float("nan")

    def generate(self, maximum):
        seed = secrets.randbelow(maximum)
        return seed, str(seed)
