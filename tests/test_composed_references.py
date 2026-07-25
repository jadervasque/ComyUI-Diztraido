"""Testes da composicao de referencias."""

from __future__ import annotations

import unittest

from services.composed_pipelines import (
    build_reference_conditioning,
    build_reference_conditioning_from_prompt,
)


class _ClipTextEncodeNode:
    FUNCTION = "encode"

    def encode(self, clip, text):
        return (f"cond({clip}|{text})",)


class _FluxGuidanceNode:
    FUNCTION = "apply"

    def apply(self, conditioning, guidance):
        return (f"g({conditioning},{guidance})",)


class _ReferenceLatentNode:
    FUNCTION = "apply"

    def apply(self, conditioning, latent):
        return (f"r({conditioning},{latent})",)


class _LoadImageNode:
    FUNCTION = "load"

    def load(self, image, upload=None):
        return (f"img({image})", None)


class _VAEEncodeNode:
    FUNCTION = "encode"

    def encode(self, pixels, vae):
        return (f"latent({pixels}|{vae})",)


def _factory(name):
    return {
        "CLIPTextEncode": _ClipTextEncodeNode,
        "FluxGuidance": _FluxGuidanceNode,
        "ReferenceLatent": _ReferenceLatentNode,
        "LoadImage": _LoadImageNode,
        "VAEEncode": _VAEEncodeNode,
    }[name]()


class _FluxGuidanceVarKwNode:
    FUNCTION = "execute"

    def execute(self, *args, **kwargs):
        conditioning = kwargs["conditioning"]
        guidance = kwargs["guidance"]
        return (f"g({conditioning},{guidance})",)


def _factory_varkw(name):
    return {
        "CLIPTextEncode": _ClipTextEncodeNode,
        "FluxGuidance": _FluxGuidanceVarKwNode,
        "ReferenceLatent": _ReferenceLatentNode,
        "LoadImage": _LoadImageNode,
        "VAEEncode": _VAEEncodeNode,
    }[name]()


class ComposedReferencesTests(unittest.TestCase):
    def test_builds_conditioning_from_clip_and_prompt(self):
        result = build_reference_conditioning_from_prompt(
            clip="clip0",
            text_prompt="a portrait",
            vae="vae0",
            guidance=3,
            reference_count=0,
            node_factory=_factory,
        )
        self.assertEqual(result, "g(cond(clip0|a portrait),3.0)")

    def test_returns_guidance_only_when_no_references(self):
        result = build_reference_conditioning(
            conditioning="c0",
            vae="vae0",
            guidance=4,
            reference_count=0,
            node_factory=_factory,
        )
        self.assertEqual(result, "g(c0,4.0)")

    def test_supports_nodes_wrapped_with_variadic_kwargs_signature(self):
        result = build_reference_conditioning(
            conditioning="c0",
            vae="vae0",
            guidance=4,
            reference_count=0,
            node_factory=_factory_varkw,
        )
        self.assertEqual(result, "g(c0,4.0)")

    def test_chains_initial_latent_and_all_active_references(self):
        result = build_reference_conditioning(
            conditioning="c0",
            vae="vae0",
            guidance=4,
            reference_count=3,
            initial_latent="l0",
            image_ref_1="ref_a.png",
            image_ref_2="ref_b.png",
            image_ref_3="",
            node_factory=_factory,
        )
        self.assertEqual(
            result,
            "r(r(r(g(c0,4.0),l0),latent(img(ref_a.png)|vae0)),latent(img(ref_b.png)|vae0))",
        )


if __name__ == "__main__":
    unittest.main()
