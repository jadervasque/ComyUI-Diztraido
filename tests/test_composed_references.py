"""Testes da composicao de referencias."""

from __future__ import annotations

import unittest

from services.composed_pipelines import (
    build_reference_conditioning,
    build_reference_conditioning_from_prompt,
    normalize_conditioning,
)


class _ClipTextEncodeNode:
    FUNCTION = "encode"

    def encode(self, clip, text):
        return (f"cond({clip}|{text})",)


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
        "ReferenceLatent": _ReferenceLatentNode,
        "LoadImage": _LoadImageNode,
        "VAEEncode": _VAEEncodeNode,
    }[name]()


class ComposedReferencesTests(unittest.TestCase):
    def test_normalize_conditioning_unwraps_single_nested_list(self):
        conditioning = [["embed", {"k": 1}]]
        nested = [conditioning]
        self.assertEqual(normalize_conditioning(nested), conditioning)

    def test_builds_positive_and_blank_negative_from_clip(self):
        positive, blank_negative = build_reference_conditioning_from_prompt(
            clip="clip0",
            text_prompt="a portrait",
            vae="vae0",
            reference_count=0,
            node_factory=_factory,
        )
        self.assertEqual(positive, "cond(clip0|a portrait)")
        self.assertEqual(blank_negative, "cond(clip0|)")

    def test_returns_conditioning_unchanged_when_no_references(self):
        result = build_reference_conditioning(
            conditioning="c0",
            vae="vae0",
            reference_count=0,
            node_factory=_factory,
        )
        self.assertEqual(result, "c0")

    def test_accepts_nested_conditioning_when_no_references(self):
        nested_conditioning = [["embed", {"p": 1}]]
        result = build_reference_conditioning(
            conditioning=[nested_conditioning],
            vae="vae0",
            reference_count=0,
            node_factory=_factory,
        )
        self.assertEqual(result, nested_conditioning)

    def test_chains_all_active_references_in_positive_only(self):
        positive, blank_negative = build_reference_conditioning_from_prompt(
            clip="clip0",
            text_prompt="a portrait",
            vae="vae0",
            reference_count=3,
            image_ref_1="ref_a.png",
            image_ref_2="ref_b.png",
            image_ref_3="",
            node_factory=_factory,
        )
        self.assertEqual(
            positive,
            "r(r(cond(clip0|a portrait),latent(img(ref_a.png)|vae0)),latent(img(ref_b.png)|vae0))",
        )
        self.assertEqual(blank_negative, "cond(clip0|)")


if __name__ == "__main__":
    unittest.main()
