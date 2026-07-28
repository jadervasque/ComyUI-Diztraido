"""Testes do seletor de resolucao estendido."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


def _load_resolution_selector_module():
    module_path = Path(__file__).resolve().parents[1] / "nodes" / "resolution_selector.py"
    spec = importlib.util.spec_from_file_location("_diztraido_resolution_selector_test", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


resolution_selector = _load_resolution_selector_module()
ASPECT_RATIOS = resolution_selector.ASPECT_RATIOS
ASPECT_RATIO_OPTIONS = resolution_selector.ASPECT_RATIO_OPTIONS
CUSTOM_ASPECT_RATIO = resolution_selector.CUSTOM_ASPECT_RATIO
DiztraidoResolutionSelector = resolution_selector.DiztraidoResolutionSelector


class ResolutionSelectorTests(unittest.TestCase):
    def test_preserves_native_and_adds_requested_aspect_ratios(self):
        expected_additions = {
            "5:4 (Classic Landscape)": (5, 4),
            "4:5 (Social Portrait)": (4, 5),
            "7:5 (Photo Landscape)": (7, 5),
            "5:7 (Photo Portrait)": (5, 7),
            "10:8 (Classic Landscape)": (10, 8),
            "8:10 (Classic Portrait)": (8, 10),
            "8:5 (Wide Landscape)": (8, 5),
            "5:8 (Tall Portrait)": (5, 8),
            "3:1 (Panoramic Landscape)": (3, 1),
            "1:3 (Panoramic Portrait)": (1, 3),
            "2:1 (Wide Panorama)": (2, 1),
            "1:2 (Tall Panorama)": (1, 2),
            "7:6 (Compact Landscape)": (7, 6),
            "6:7 (Compact Portrait)": (6, 7),
        }
        self.assertEqual(len(ASPECT_RATIOS), 22)
        for label, ratio in expected_additions.items():
            with self.subTest(label=label):
                self.assertEqual(ASPECT_RATIOS[label], ratio)
        self.assertEqual(ASPECT_RATIO_OPTIONS[-1], CUSTOM_ASPECT_RATIO)

    def test_matches_native_resolution_calculation(self):
        self.assertEqual(
            DiztraidoResolutionSelector.calculate("1:1 (Square)", 1.0, 8, 640, 480),
            (1024, 1024),
        )
        width, height = DiztraidoResolutionSelector.calculate(
            "3:1 (Panoramic Landscape)", 1.0, 8, 640, 480
        )
        self.assertGreater(width, height)
        self.assertEqual(width % 8, 0)
        self.assertEqual(height % 8, 0)

    def test_custom_mode_uses_exact_dimensions(self):
        self.assertEqual(
            DiztraidoResolutionSelector.calculate(CUSTOM_ASPECT_RATIO, 1.0, 64, 1232, 832),
            (1232, 832),
        )

    def test_exposes_custom_inputs_and_outputs(self):
        required = DiztraidoResolutionSelector.INPUT_TYPES()["required"]
        self.assertEqual(required["aspect_ratio"][0], ASPECT_RATIO_OPTIONS)
        self.assertEqual(required["megapixels"][1]["default"], 1.0)
        self.assertEqual(required["multiple"][1]["default"], 8)
        self.assertEqual(required["width"][1]["default"], 1024)
        self.assertEqual(required["height"][1]["default"], 1024)
        self.assertEqual(DiztraidoResolutionSelector.RETURN_NAMES, ("width", "height"))


if __name__ == "__main__":
    unittest.main()
