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
    def test_exposes_only_manager_widgets_and_prompt_ratio_pairs(self):
        resolution, module = _load_modules()
        inputs = module.DiztraidoStringManager.INPUT_TYPES()
        required = inputs["required"]
        optional = inputs["optional"]

        self.assertEqual(set(required), {"num_fields", "selected_string"})
        self.assertEqual(required["num_fields"][1]["default"], 5)
        self.assertTrue(required["num_fields"][1]["socketless"])
        self.assertTrue(required["selected_string"][1]["control_after_generate"])
        self.assertTrue(required["selected_string"][1]["socketless"])

        self.assertIn("string_1", optional)
        self.assertIn("aspect_ratio_1", optional)
        self.assertIn("string_24", optional)
        self.assertIn("aspect_ratio_24", optional)
        self.assertNotIn("megapixels_1", optional)
        self.assertNotIn("multiple_1", optional)
        self.assertNotIn("width_1", optional)
        self.assertNotIn("height_1", optional)

        self.assertEqual(
            module.DiztraidoStringManager.RETURN_TYPES,
            ("STRING", resolution.ASPECT_RATIO_OPTIONS),
        )
        self.assertEqual(
            module.DiztraidoStringManager.RETURN_NAMES,
            ("string_selected", "resolution_selected"),
        )

    def test_selects_matching_prompt_and_aspect_ratio(self):
        _, module = _load_modules()
        prompt, aspect_ratio = module.DiztraidoStringManager().select(
            num_fields=3,
            selected_string=2,
            string_1="first",
            string_2="second",
            aspect_ratio_2="3:4 (Portrait Standard)",
        )

        self.assertEqual(prompt, "second")
        self.assertEqual(aspect_ratio, "3:4 (Portrait Standard)")

    def test_clamps_selection_to_active_field_count(self):
        _, module = _load_modules()
        prompt, aspect_ratio = module.DiztraidoStringManager().select(
            num_fields=2,
            selected_string=20,
            string_1="first",
            string_2="second",
            string_20="inactive",
            aspect_ratio_2="16:9 (Widescreen)",
            aspect_ratio_20="Custom",
        )

        self.assertEqual(prompt, "second")
        self.assertEqual(aspect_ratio, "16:9 (Widescreen)")

    def test_supports_custom_and_falls_back_for_invalid_values(self):
        _, module = _load_modules()
        node = module.DiztraidoStringManager()

        _, custom = node.select(
            num_fields=1,
            selected_string=1,
            aspect_ratio_1="Custom",
        )
        _, fallback = node.select(
            num_fields=1,
            selected_string=1,
            aspect_ratio_1="invalid",
        )

        self.assertEqual(custom, "Custom")
        self.assertEqual(fallback, "1:1 (Square)")


if __name__ == "__main__":
    unittest.main()
