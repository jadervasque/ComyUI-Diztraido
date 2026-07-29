"""Tests for Flux LoRA loader widget defaults."""

from __future__ import annotations

import importlib.util
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch


def _load_node(filename: str, build_name: str, load_name: str):
    root = Path(__file__).resolve().parents[1]
    package_name = f"_diztraido_{filename.replace('.', '_')}_test"
    module_name = f"{package_name}.nodes.{filename[:-3]}"

    root_package = types.ModuleType(package_name)
    root_package.__path__ = [str(root)]
    nodes_package = types.ModuleType(f"{package_name}.nodes")
    nodes_package.__path__ = [str(root / "nodes")]
    services_package = types.ModuleType(f"{package_name}.services")
    services_package.__path__ = [str(root / "services")]
    model_loaders = types.ModuleType(f"{package_name}.services.model_loaders")

    def build_schema():
        return (
            {
                "strength_model_1": (
                    "FLOAT",
                    {"default": 1.0, "min": -100.0, "max": 100.0, "step": 0.01},
                ),
                "strength_clip_1": (
                    "FLOAT",
                    {"default": 1.0, "min": -100.0, "max": 100.0, "step": 0.01},
                ),
            },
            {},
        )

    setattr(model_loaders, build_name, build_schema)
    setattr(model_loaders, load_name, lambda **kwargs: ("model", "clip", "vae"))

    modules = {
        package_name: root_package,
        f"{package_name}.nodes": nodes_package,
        f"{package_name}.services": services_package,
        f"{package_name}.services.model_loaders": model_loaders,
    }

    spec = importlib.util.spec_from_file_location(module_name, root / "nodes" / filename)
    module = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, modules):
        spec.loader.exec_module(module)
    return module


class LoraNodeDefaultTests(unittest.TestCase):
    def test_flux1_strength_clip_defaults_to_zero(self):
        module = _load_node(
            "load_flux1_models_loras.py",
            "build_flux1_lora_loader_schema",
            "load_flux1_models_with_loras",
        )
        inputs = module.DiztraidoLoadFlux1ModelsLoras.INPUT_TYPES()
        self.assertEqual(inputs["required"]["strength_model_1"][1]["default"], 1.0)
        self.assertEqual(inputs["required"]["strength_clip_1"][1]["default"], 0.0)

    def test_flux2_strength_clip_defaults_to_zero(self):
        module = _load_node(
            "load_flux2_models_loras.py",
            "build_flux2_lora_loader_schema",
            "load_flux2_models_with_loras",
        )
        inputs = module.DiztraidoLoadFlux2ModelsLoras.INPUT_TYPES()
        self.assertEqual(inputs["required"]["strength_model_1"][1]["default"], 1.0)
        self.assertEqual(inputs["required"]["strength_clip_1"][1]["default"], 0.0)


if __name__ == "__main__":
    unittest.main()
