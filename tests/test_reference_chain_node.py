"""Testes do contrato publico do no Flux Load References."""

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
    folder_paths = types.ModuleType("folder_paths")

    modules = {
        package_name: root_package,
        f"{package_name}.nodes": nodes_package,
        f"{package_name}.services": services_package,
        f"{package_name}.services.composed_pipelines": composed_pipelines,
        "folder_paths": folder_paths,
    }

    spec = importlib.util.spec_from_file_location(module_name, root / "nodes" / "reference_chain.py")
    module = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, modules):
        spec.loader.exec_module(module)
    return module


class ReferenceChainNodeTests(unittest.TestCase):
    def test_returns_input_vae_as_second_output(self):
        module = _load_reference_chain_module()
        conditioning = object()
        vae = object()
        module.build_reference_conditioning_from_prompt = Mock(return_value=conditioning)

        result = module.DiztraidoReferenceChain().apply_references(
            clip=object(),
            text_prompt="prompt",
            vae=vae,
            guidance=4.0,
            reference_count=0,
        )

        self.assertIs(result[0], conditioning)
        self.assertIs(result[1], vae)
        self.assertEqual(module.DiztraidoReferenceChain.RETURN_TYPES, ("CONDITIONING", "VAE"))


if __name__ == "__main__":
    unittest.main()