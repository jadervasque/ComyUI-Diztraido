"""Tests for file-based and direct IMAGE reference conditioning."""

from __future__ import annotations

import unittest

from services.reference_conditioning import (
    build_reference_conditioning,
    build_reference_conditioning_from_prompt,
    collect_reference_sources,
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


class ReferenceConditioningTests(unittest.TestCase):
    def test_collects_direct_input_before_same_slot_combo(self):
        direct = object()
        sources = collect_reference_sources(
            2,
            {
                "image_input_1": direct,
                "image_ref_1": "ignored.png",
                "image_ref_2": "selected.png",
            },
        )
        self.assertEqual(sources, [("pixels", direct), ("file", "selected.png")])

    def test_returns_conditioning_unchanged_without_sources(self):
        result = build_reference_conditioning(
            conditioning="c0",
            vae="vae0",
            reference_count=2,
            node_factory=_factory,
        )
        self.assertEqual(result, "c0")

    def test_chains_direct_and_file_sources_in_slot_order(self):
        positive, blank_negative = build_reference_conditioning_from_prompt(
            clip="clip0",
            text_prompt="portrait",
            vae="vae0",
            reference_count=3,
            image_input_1="direct-a",
            image_ref_1="ignored.png",
            image_ref_2="selected.png",
            image_input_3="direct-c",
            node_factory=_factory,
        )

        self.assertEqual(
            positive,
            "r(r(r(cond(clip0|portrait),latent(direct-a|vae0)),"
            "latent(img(selected.png)|vae0)),latent(direct-c|vae0))",
        )
        self.assertEqual(blank_negative, "cond(clip0|)")


if __name__ == "__main__":
    unittest.main()
