"""Testes do contrato publico do no Flux Sampler."""

from __future__ import annotations

import importlib.util
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import services.composed_pipelines as composed_pipelines


def _load_processing_bundle_module():
    root = Path(__file__).resolve().parents[1]
    package_name = "_diztraido_processing_test"
    module_name = f"{package_name}.nodes.processing_bundle"

    root_package = types.ModuleType(package_name)
    root_package.__path__ = [str(root)]
    nodes_package = types.ModuleType(f"{package_name}.nodes")
    nodes_package.__path__ = [str(root / "nodes")]
    services_package = types.ModuleType(f"{package_name}.services")
    services_package.__path__ = [str(root / "services")]

    resolution_name = f"{package_name}.nodes.resolution_selector"
    resolution_spec = importlib.util.spec_from_file_location(
        resolution_name, root / "nodes" / "resolution_selector.py"
    )
    resolution_module = importlib.util.module_from_spec(resolution_spec)

    modules = {
        package_name: root_package,
        f"{package_name}.nodes": nodes_package,
        f"{package_name}.services": services_package,
        f"{package_name}.services.composed_pipelines": composed_pipelines,
        resolution_name: resolution_module,
    }

    with patch.dict(sys.modules, modules):
        resolution_spec.loader.exec_module(resolution_module)
        spec = importlib.util.spec_from_file_location(
            module_name, root / "nodes" / "processing_bundle.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    return module


class ProcessingBundleNodeTests(unittest.TestCase):
    def test_exposes_cfg_inputs_image_and_latent_outputs(self):
        module = _load_processing_bundle_module()
        inputs = module.DiztraidoProcessingBundle.INPUT_TYPES()
        required = inputs["required"]
        self.assertIn("model", required)
        self.assertIn("positive", required)
        self.assertIn("negative", required)
        self.assertIn("cfg", required)
        self.assertEqual(required["cfg"][1]["default"], 4.0)
        self.assertEqual(required["steps"][1]["default"], 50)
        self.assertIn("aspect_ratio", required)
        self.assertIn("width", required)
        self.assertIn("height", required)
        self.assertTrue(inputs["optional"]["vae"][1]["lazy"])
        self.assertEqual(module.DiztraidoProcessingBundle.RETURN_TYPES, ("IMAGE", "LATENT"))

    def test_does_not_require_vae_when_decode_is_disabled(self):
        module = _load_processing_bundle_module()
        module.run_processing_pipeline = Mock(return_value=(None, "latent0"))
        result = module.DiztraidoProcessingBundle().process(
            model="m0",
            positive="p0",
            negative="n0",
            noise_seed=42,
            cfg=4.0,
            sampler_name="euler",
            steps=50,
            aspect_ratio="Custom",
            megapixels=1.0,
            multiple=8,
            width=1216,
            height=832,
            batch_size=1,
            decode_image=False,
        )
        self.assertEqual(result, (None, "latent0"))
        kwargs = module.run_processing_pipeline.call_args.kwargs
        self.assertFalse(kwargs["decode_image"])
        self.assertIsNone(kwargs["vae"])
        self.assertEqual(kwargs["width"], 1216)
        self.assertEqual(kwargs["height"], 832)

    def test_requests_connected_lazy_vae_only_when_decode_enabled(self):
        module = _load_processing_bundle_module()
        node = module.DiztraidoProcessingBundle()
        self.assertEqual(node.check_lazy_status(True, vae=None), ["vae"])
        self.assertEqual(node.check_lazy_status(False, vae=None), [])


if __name__ == "__main__":
    unittest.main()
