"""Registro central dos nós disponibilizados pelo pacote."""

from .metadata_reader_advanced import DiztraidoImageMetadataReaderAdvanced
from .metadata_reader import DiztraidoMetadataReader
from .random_seed import BackendRandomSeed
from .reference_chain import DiztraidoReferenceChain
from .processing_bundle import DiztraidoProcessingBundle
from .load_flux2_models import DiztraidoLoadFlux2Models
from .load_flux1_models import DiztraidoLoadFlux1Models
from .load_flux1_models_loras import DiztraidoLoadFlux1ModelsLoras
from .load_flux2_models_loras import DiztraidoLoadFlux2ModelsLoras
from .resolution_selector import DiztraidoResolutionSelector
from .string_format import DiztraidoStringFormat
from .string_manager import DiztraidoStringManager

NODE_CLASS_MAPPINGS = {
    "DiztraidoMetadataReader": DiztraidoMetadataReader,
    "DiztraidoImageMetadataReaderAdvanced": DiztraidoImageMetadataReaderAdvanced,
    "BackendRandomSeed": BackendRandomSeed,
    "DiztraidoReferenceChain": DiztraidoReferenceChain,
    "DiztraidoProcessingBundle": DiztraidoProcessingBundle,
    "DiztraidoLoadFlux2Models": DiztraidoLoadFlux2Models,
    "DiztraidoLoadFlux1Models": DiztraidoLoadFlux1Models,
    "DiztraidoLoadFlux1ModelsLoras": DiztraidoLoadFlux1ModelsLoras,
    "DiztraidoLoadFlux2ModelsLoras": DiztraidoLoadFlux2ModelsLoras,
    "DiztraidoResolutionSelector": DiztraidoResolutionSelector,
    "DiztraidoStringFormat": DiztraidoStringFormat,
    "DiztraidoStringManager": DiztraidoStringManager,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "DiztraidoMetadataReader": "Diztraido: Metadata Reader",
    "DiztraidoImageMetadataReaderAdvanced": "Diztraido: Metadata Reader Advanced",
    "BackendRandomSeed": "Backend Random Seed",
    "DiztraidoReferenceChain": "Flux Load References",
    "DiztraidoProcessingBundle": "Flux Sampler",
    "DiztraidoLoadFlux2Models": "Load Flux.2 Models",
    "DiztraidoLoadFlux1Models": "Load Flux.1 Models",
    "DiztraidoLoadFlux1ModelsLoras": "Load Flux.1 Models + LoRAs",
    "DiztraidoLoadFlux2ModelsLoras": "Load Flux.2 Models + LoRAs",
    "DiztraidoResolutionSelector": "Resolution Selector Extended",
    "DiztraidoStringFormat": "String Format",
    "DiztraidoStringManager": "String Manager",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
