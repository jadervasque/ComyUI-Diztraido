"""Registro central dos nós disponibilizados pelo pacote."""

from .metadata_reader_advanced import DiztraidoImageMetadataReaderAdvanced
from .random_seed import BackendRandomSeed

NODE_CLASS_MAPPINGS = {
    "DiztraidoImageMetadataReaderAdvanced": DiztraidoImageMetadataReaderAdvanced,
    "BackendRandomSeed": BackendRandomSeed,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "DiztraidoImageMetadataReaderAdvanced": "Diztraido: Metadata Reader Advanced",
    "BackendRandomSeed": "Backend Random Seed",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
