"""Tests for the public Flux Load References node contract."""

from __future__ import annotations

import importlib.util
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import services.composed_pipelines as composed_pipelines


def _load_reference_chain_module():
    root = Path(__file__).resolve().parents[1]
    package_name = "_diztraido_reference_test"
    module_name = f"{package_name}.nodes.reference_chain"

    root_package = types.ModuleType(package_name)
    root_package.__path__ = [str(root)]
    nodes_package = types.ModuleType(f"{package_name}.nodes")
    nodes_package.__path__ = [str(root / "nodes")]
    services_package = types.ModuleType(f"{package_name}.services")
    services_package.__path__ = [str(root / "services")]
    reference_conditioning = types.ModuleType(
        f"{package_name}.services.reference_conditioning"
    )
    reference_conditioning.build_reference_conditioning_from_prompt = Mock()
    folder_paths = types.ModuleType("folder_paths")

    modules = {
        package_name: root_package,
        f"{package_name}.nodes": nodes_package,
        f"{package_name}.services": services_package,
        f"{package_name}.services.composed_pipelines": composed_pipelines,
        f"{package_name}.services.reference_conditioning": reference_conditioning,
        "folder_paths": folder_paths,
    }

    spec = importlib.util.spec_from_file_location(module_name, root / "nodes" / "reference_chain.py")
    module = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, modules):
        spec.loader.exec_module(module)
    return module


class ReferenceChainNodeTests(unittest.TestCase):
    def test_returns_positive_and_blank_negative(self):
        module = _load_reference_chain_module()
        positive = object()
        blank_negative = object()
        module.build_reference_conditioning_from_prompt = Mock(
            return_value=(positive, blank_negative)
        )

        result = module.DiztraidoReferenceChain().apply_references(
            clip=object(),
            vae=object(),
            text_prompt="prompt",
            reference_count=0,
        )

        self.assertIs(result[0], positive)
        self.assertIs(result[1], blank_negative)
        self.assertEqual(
            module.DiztraidoReferenceChain.RETURN_TYPES,
            ("CONDITIONING", "CONDITIONING"),
        )
        self.assertEqual(
            module.DiztraidoReferenceChain.RETURN_NAMES,
            ("positive", "blank_negative"),
        )

    def test_contract_uses_combo_and_optional_image_inputs(self):
        module = _load_reference_chain_module()
        module.DiztraidoReferenceChain._image_options = staticmethod(lambda: ([""], {}))
        inputs = module.DiztraidoReferenceChain.INPUT_TYPES()

        self.assertNotIn("guidance", inputs["required"])
        self.assertNotIn("initial_latent", inputs.get("optional", {}))
        self.assertIn("clip", inputs["required"])
        self.assertIn("vae", inputs["required"])
        self.assertIn("image_ref_1", inputs["required"])
        self.assertEqual(inputs["required"]["image_ref_1"][1], {})
        self.assertEqual(inputs["optional"]["image_input_1"], ("IMAGE",))
        self.assertEqual(inputs["optional"]["image_input_16"], ("IMAGE",))


if __name__ == "__main__":
    unittest.main()
