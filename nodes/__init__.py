"""Registro central dos nós disponibilizados pelo pacote."""

from .metadata_reader_advanced import DiztraidoImageMetadataReaderAdvanced
from .metadata_reader import DiztraidoMetadataReader
from .random_seed import BackendRandomSeed
from .reference_chain import DiztraidoReferenceChain
from .processing_bundle import DiztraidoProcessingBundle

NODE_CLASS_MAPPINGS = {
    "DiztraidoMetadataReader": DiztraidoMetadataReader,
    "DiztraidoImageMetadataReaderAdvanced": DiztraidoImageMetadataReaderAdvanced,
    "BackendRandomSeed": BackendRandomSeed,
    "DiztraidoReferenceChain": DiztraidoReferenceChain,
    "DiztraidoProcessingBundle": DiztraidoProcessingBundle,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "DiztraidoMetadataReader": "Diztraido: Metadata Reader",
    "DiztraidoImageMetadataReaderAdvanced": "Diztraido: Metadata Reader Advanced",
    "BackendRandomSeed": "Backend Random Seed",
    "DiztraidoReferenceChain": "Flux Load References",
    "DiztraidoProcessingBundle": "Flux Sampler",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
