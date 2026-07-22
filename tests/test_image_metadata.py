"""Testes da camada de extração de metadados."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image, PngImagePlugin

from services.image_metadata import read_image_metadata


class ImageMetadataTests(unittest.TestCase):
    def test_reads_automatic1111_parameters_from_png(self):
        with tempfile.TemporaryDirectory() as directory:
            image_path = Path(directory) / "metadata.png"
            png_info = PngImagePlugin.PngInfo()
            png_info.add_text(
                "parameters",
                "a red fox\nNegative prompt: blurry\n"
                "Steps: 20, Sampler: euler, CFG scale: 7, Seed: 42, "
                "Size: 64x32, Model: example",
            )
            Image.new("RGB", (64, 32)).save(image_path, pnginfo=png_info)

            result = read_image_metadata(image_path)

        self.assertEqual(result["prompt"], "a red fox")
        self.assertEqual(result["negative_prompt"], "blurry")
        self.assertEqual(result["details"]["seed"], "42")
        self.assertEqual(result["details"]["cfg"], "7")
        self.assertEqual(json.loads(result["metadata_json"])["file"]["width"], 64)

    def test_converts_non_finite_json_values_to_null(self):
        with tempfile.TemporaryDirectory() as directory:
            image_path = Path(directory) / "metadata.png"
            png_info = PngImagePlugin.PngInfo()
            png_info.add_text("prompt", '{"changed": [NaN, Infinity, -Infinity]}')
            Image.new("RGB", (16, 8)).save(image_path, pnginfo=png_info)

            result = read_image_metadata(image_path)

        metadata = json.loads(result["metadata_json"])
        self.assertEqual(metadata["metadata"]["prompt"]["changed"], [None, None, None])


if __name__ == "__main__":
    unittest.main()
