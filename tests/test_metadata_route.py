"""Testes da leitura de metadados usada pela interface em tempo real."""

from __future__ import annotations

import json
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image, PngImagePlugin

if "folder_paths" not in sys.modules:
    folder_paths_stub = types.ModuleType("folder_paths")
    folder_paths_stub.exists_annotated_filepath = lambda image: False
    folder_paths_stub.get_annotated_filepath = lambda image: image
    sys.modules["folder_paths"] = folder_paths_stub

from routes.metadata import read_metadata_for_image


class MetadataRouteTests(unittest.TestCase):
    def test_returns_complete_normalized_metadata(self):
        with tempfile.TemporaryDirectory() as directory:
            image_path = Path(directory) / "metadata.png"
            png_info = PngImagePlugin.PngInfo()
            png_info.add_text("custom", "value")
            png_info.add_text("prompt", '{"changed": [NaN]}')
            Image.new("RGB", (16, 8)).save(image_path, pnginfo=png_info)

            with patch("routes.metadata.folder_paths.exists_annotated_filepath", return_value=True):
                with patch("routes.metadata.folder_paths.get_annotated_filepath", return_value=image_path):
                    metadata, error = read_metadata_for_image("metadata.png")

        self.assertIsNone(error)
        self.assertEqual(metadata["file"]["width"], 16)
        self.assertEqual(metadata["metadata"]["custom"], "value")
        self.assertEqual(metadata["metadata"]["prompt"]["changed"], [None])
        json.dumps(metadata, allow_nan=False)

    def test_rejects_unknown_images(self):
        with patch("routes.metadata.folder_paths.exists_annotated_filepath", return_value=False):
            metadata, error = read_metadata_for_image("unknown.png")

        self.assertIsNone(metadata)
        self.assertEqual(error, "Imagem não encontrada.")
