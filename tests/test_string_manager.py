"""Tests for the String Manager node."""

from __future__ import annotations

import importlib.util
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch


def _load_modules():
    root = Path(__file__).resolve().parents[1]
    package_name = "_diztraido_string_manager_test"

    root_package = types.ModuleType(package_name)
    root_package.__path__ = [str(root)]
    nodes_package = types.ModuleType(f"{package_name}.nodes")
    nodes_package.__path__ = [str(root / "nodes")]

    resolution_name = f"{package_name}.nodes.resolution_selector"
    resolution_spec = importlib.util.spec_from_file_location(
        resolution_name,
        root / "nodes" / "resolution_selector.py",
    )
    resolution_module = importlib.util.module_from_spec(resolution_spec)

    modules = {
        package_name: root_package,
        f"{package_name}.nodes": nodes_package,
        resolution_name: resolution_module,
    }

    with patch.dict(sys.modules, modules):
        resolution_spec.loader.exec_module(resolution_module)
        string_manager_name = f"{package_name}.nodes.string_manager"
        string_manager_spec = importlib.util.spec_from_file_location(
            string_manager_name,
            root / "nodes" / "string_manager.py",
        )
        string_manager_module = importlib.util.module_from_spec(string_manager_spec)
        sys.modules[string_manager_name] = string_manager_module
        string_manager_spec.loader.exec_module(string_manager_module)

    return resolution_module, string_manager_module


class StringManagerTests(unittest.TestCase):
    def test_exposes_widgets_without_external_inputs(self):
        resolution, module = _load_modules()
        inputs = module.DiztraidoStringManager.INPUT_TYPES()

        self.assertEqual(set(inputs["required"]), {"num_fields", "selected_string"})
        self.assertEqual(inputs["required"]["num_fields"][1]["default"], 5)
        self.assertIn("string_1", inputs["optional"])
        self.assertIn("aspect_ratio_24", inputs["optional"])
        self.assertIn("height_24", inputs["optional"])
        self.assertEqual(
            module.DiztraidoStringManager.RETURN_TYPES,
            ("STRING", resolution.RESOLUTION_TYPE),
        )
        self.assertEqual(
            module.DiztraidoStringManager.RETURN_NAMES,
            ("string_selected", "resolution_selected"),
        )

    def test_selects_matching_prompt_and_resolution(self):
        _, module = _load_modules()
        prompt, resolution = module.DiztraidoStringManager().select(
            num_fields=3,
            selected_string=2,
            string_1="first",
            string_2="second",
            aspect_ratio_2="3:4 (Portrait Standard)",
            megapixels_2=1.5,
            multiple_2=64,
        )

        self.assertEqual(prompt, "second")
        self.assertEqual(resolution["aspect_ratio"], "3:4 (Portrait Standard)")
        self.assertEqual(resolution["megapixels"], 1.5)
        self.assertEqual(resolution["multiple"], 64)

    def test_clamps_selection_to_active_field_count(self):
        _, module = _load_modules()
        prompt, _ = module.DiztraidoStringManager().select(
            num_fields=2,
            selected_string=20,
            string_1="first",
            string_2="second",
            string_20="inactive",
        )
        self.assertEqual(prompt, "second")

    def test_custom_resolution_is_consumed_by_resolution_selector(self):
        resolution_module, module = _load_modules()
        _, resolution = module.DiztraidoStringManager().select(
            num_fields=1,
            selected_string=1,
            aspect_ratio_1="Custom",
            width_1=1216,
            height_1=832,
        )

        result = resolution_module.DiztraidoResolutionSelector.calculate(
            "1:1 (Square)",
            1.0,
            8,
            resolution=resolution,
        )
        self.assertEqual(result, (1216, 832))


if __name__ == "__main__":
    unittest.main()
