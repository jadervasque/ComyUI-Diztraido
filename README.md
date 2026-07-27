**Languages:** [English](README.md) · [Português (Brasil)](docs/lang/pt-BR/README.md) · [Español](docs/lang/es/README.md)

# ComfyUI-Diztraido

[![CI](https://github.com/jadervasque/ComyUI-Diztraido/actions/workflows/ci.yml/badge.svg)](https://github.com/jadervasque/ComyUI-Diztraido/actions/workflows/ci.yml)

A collection of custom nodes for ComfyUI focused on Flux workflow composition, metadata inspection, and reusable utilities. The project separates ComfyUI integration, business rules, local routes, JavaScript extensions, and automated tests.

> The project is under active development. Node IDs and public contracts are preserved to reduce incompatibilities with existing workflows.

## Features

- Visual inspection and advanced extraction of image metadata.
- Backend-generated random seeds for each workflow execution.
- Composite loaders for Flux.1 and Flux.2.
- Sequential Low-Rank Adaptation (LoRA) application for Flux models.
- Reference-image chaining with conditioning and guidance.
- Composite sampling and decoding pipeline.
- Resolution selection by aspect ratio and megapixel target.
- String formatting with dynamic inputs and conditional expressions.
- JavaScript extensions for dynamic widgets and previews.
- Unit tests and continuous integration with GitHub Actions.

## Installation

### Git

Clone the repository into the `custom_nodes` directory of your ComfyUI installation:

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/jadervasque/ComyUI-Diztraido.git
```

Restart ComfyUI. The nodes will be available under the `Diztraido` categories.

### Updating

```bash
cd ComfyUI/custom_nodes/ComyUI-Diztraido
git pull
```

Restart ComfyUI after updating.

## Requirements

- A working ComfyUI installation.
- A Python version supported by that ComfyUI installation.
- The models and resources required by the native nodes used in each workflow.

The repository does not declare additional mandatory Python runtime dependencies. Composite nodes reuse functionality provided by ComfyUI itself.

## Available nodes

| Group | Node | Internal ID |
|---|---|---|
| Metadata | Diztraido: Metadata Reader | `DiztraidoMetadataReader` |
| Metadata | Diztraido: Metadata Reader Advanced | `DiztraidoImageMetadataReaderAdvanced` |
| Utilities | Backend Random Seed | `BackendRandomSeed` |
| Utilities | Resolution Selector Extended | `DiztraidoResolutionSelector` |
| Utilities | String Format | `DiztraidoStringFormat` |
| Flux | Flux Load References | `DiztraidoReferenceChain` |
| Flux | Flux Sampler | `DiztraidoProcessingBundle` |
| Flux | Load Flux.1 Models | `DiztraidoLoadFlux1Models` |
| Flux | Load Flux.1 Models + LoRAs | `DiztraidoLoadFlux1ModelsLoras` |
| Flux | Load Flux.2 Models | `DiztraidoLoadFlux2Models` |
| Flux | Load Flux.2 Models + LoRAs | `DiztraidoLoadFlux2ModelsLoras` |

See the [node catalog](docs/NODES.md) for inputs, outputs, behavior, and examples.

## Documentation

- [Architecture](docs/ARCHITECTURE.md): layers, loading flow, and compatibility rules.
- [Development guide](docs/DEVELOPMENT.md): environment, tests, conventions, and project extension.
- [Node catalog](docs/NODES.md): functional description of the available nodes.
- [Contributing](CONTRIBUTING.md): process for issues and pull requests.
- [Code of conduct](CODE_OF_CONDUCT.md): expected behavior in project spaces.
- [Security policy](SECURITY.md): responsible vulnerability reporting.
- [Changelog](CHANGELOG.md): relevant project changes.

Translated documentation is maintained under `docs/lang/pt-BR/` and `docs/lang/es/`. Every public documentation file includes language navigation in its header.

## Repository structure

```text
.
├── .github/               # Workflows and collaboration templates
├── docs/                  # Technical and functional documentation
│   └── lang/              # Portuguese and Spanish translations
├── nodes/                 # Node adapters and definitions
├── routes/                # Local endpoints used by the frontend
├── services/              # Reusable rules and orchestration
├── tests/                 # Unit tests
├── web/                   # ComfyUI JavaScript extensions
├── __init__.py            # Extension entry point
├── PLAN0.md               # Initial professionalization plan
├── pyproject.toml         # Quality-tool configuration
└── requirements-test.txt  # Dependencies for tests outside ComfyUI
```

## Tests

In an isolated Python environment, first install the dependency used by the metadata tests:

```bash
python -m pip install -r requirements-test.txt
```

Then run:

```bash
python -m compileall -q .
python -m unittest discover -s tests -v
```

Optional tools such as Ruff, Pytest, and Coverage are configured in `pyproject.toml`. See the [development guide](docs/DEVELOPMENT.md).

## Contributing

Before contributing, read `CONTRIBUTING.md` and `CODE_OF_CONDUCT.md`. Pull requests must preserve node IDs, inputs, and outputs unless they include an explicit migration strategy.

## Security

Do not disclose unpatched vulnerabilities in public issues. Follow `SECURITY.md` for private contact and responsible disclosure instructions.

## License and usage rights

The source code is publicly visible but is not distributed under a permissive open-source license. All rights remain reserved as stated in `LICENSE`. Contact the copyright holder before reusing, redistributing, or creating derivative works.
