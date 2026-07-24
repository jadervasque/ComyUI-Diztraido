"""Testes dos servicos de carregamento de modelos Flux."""

from __future__ import annotations

import unittest

from services.model_loaders import (
    build_flux1_loader_schema,
    build_flux2_loader_schema,
    load_flux1_models,
    load_flux2_models,
)


class _UNETLoaderClass:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "unet_name": (["u1"], {"default": "u1"}),
                "weight_dtype": (["default", "fp8"], {"default": "default"}),
            },
        }


class _CLIPLoaderClass:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "clip_name": (["c1"], {"default": "c1"}),
                "type": (["flux", "flux2"], {"default": "flux"}),
                "device": (["default", "cpu"], {"default": "default"}),
            },
        }


class _DualCLIPLoaderClass:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "clip_name1": (["a"], {"default": "a"}),
                "clip_name2": (["b"], {"default": "b"}),
                "type": (["flux", "sdxl"], {"default": "sdxl"}),
            },
        }


class _VAELoaderClass:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "vae_name": (["v1"], {"default": "v1"}),
            },
        }


class _UNETLoaderNode:
    FUNCTION = "load"

    def load(self, unet_name, weight_dtype):
        return (f"model({unet_name}|{weight_dtype})",)


class _CLIPLoaderNode:
    FUNCTION = "load"

    def load(self, clip_name, type, device):
        return (f"clip({clip_name}|{type}|{device})",)


class _DualCLIPLoaderNode:
    FUNCTION = "load"

    def load(self, clip_name1, clip_name2, type):
        return (f"clip2({clip_name1}|{clip_name2}|{type})",)


class _VAELoaderNode:
    FUNCTION = "load"

    def load(self, vae_name):
        return (f"vae({vae_name})",)


def _resolver(name):
    return {
        "UNETLoader": _UNETLoaderClass,
        "CLIPLoader": _CLIPLoaderClass,
        "DualCLIPLoader": _DualCLIPLoaderClass,
        "VAELoader": _VAELoaderClass,
    }[name]


def _factory(name):
    return {
        "UNETLoader": _UNETLoaderNode,
        "CLIPLoader": _CLIPLoaderNode,
        "DualCLIPLoader": _DualCLIPLoaderNode,
        "VAELoader": _VAELoaderNode,
    }[name]()


class ModelLoadersTests(unittest.TestCase):
    def test_flux2_schema_overrides_clip_type_default(self):
        required, _ = build_flux2_loader_schema(_resolver)
        self.assertEqual(required["type"][1]["default"], "flux2")

    def test_flux1_schema_overrides_dual_clip_type_default(self):
        required, _ = build_flux1_loader_schema(_resolver)
        self.assertEqual(required["type"][1]["default"], "flux")

    def test_flux2_loader_runs_all_three_nodes(self):
        model, clip, vae = load_flux2_models(
            node_factory=_factory,
            resolver=_resolver,
            unet_name="u1",
            weight_dtype="fp8",
            clip_name="c1",
            type="flux2",
            device="cpu",
            vae_name="v1",
        )
        self.assertEqual(model, "model(u1|fp8)")
        self.assertEqual(clip, "clip(c1|flux2|cpu)")
        self.assertEqual(vae, "vae(v1)")

    def test_flux1_loader_runs_all_three_nodes(self):
        model, clip, vae = load_flux1_models(
            node_factory=_factory,
            resolver=_resolver,
            unet_name="u1",
            weight_dtype="default",
            clip_name1="a",
            clip_name2="b",
            type="flux",
            vae_name="v1",
        )
        self.assertEqual(model, "model(u1|default)")
        self.assertEqual(clip, "clip2(a|b|flux)")
        self.assertEqual(vae, "vae(v1)")


if __name__ == "__main__":
    unittest.main()
