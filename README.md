**Languages:** [English](README.md) · [Português (Brasil)](docs/lang/pt-BR/README.md) · [Español](docs/lang/es/README.md)

# ComfyUI-Diztraido

[![CI](https://github.com/jadervasque/ComyUI-Diztraido/actions/workflows/ci.yml/badge.svg)](https://github.com/jadervasque/ComyUI-Diztraido/actions/workflows/ci.yml)
[![Version](https://img.shields.io/badge/version-0.1.0-blue)](CHANGELOG.md)

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
- Multi-prompt management with one aspect ratio associated with each prompt.
- String formatting with dynamic inputs and conditional expressions.
- JavaScript extensions for dynamic widgets and previews.
- Unit tests and continuous integration with GitHub Actions.

## Installation

### ComfyUI-Manager and Comfy Registry

Search for **Diztraido Nodes** in ComfyUI-Manager and install the Registry package identified as `diztraido-nodes`.

With Comfy CLI, use:

```bash
comfy node install diztraido-nodes
```

Restart ComfyUI after installation. The nodes will be available under the `Diztraido` categories.

### Git

As a fallback, clone the repository into the `custom_nodes` directory of your ComfyUI installation:

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/jadervasque/ComyUI-Diztraido.git
```

Restart ComfyUI. The nodes will be available under the `Diztraido` categories.

### Updating a Git installation

```bash
cd ComfyUI/custom_nodes/ComyUI-Diztraido
git pull
```

Restart ComfyUI after updating. Registry installations should be updated through ComfyUI-Manager so the selected semantic version remains controlled by the Registry.

## Versioning

The current Registry release is `0.1.0`. Published Registry versions are immutable and follow Semantic Versioning. The version declared in `pyproject.toml` is the source used by the publication workflow.

## Requirements

- A working ComfyUI installation.
- Python 3.10 or later, subject to the Python versions supported by the installed ComfyUI release.
- The models and resources required by the native nodes used in each workflow.

The repository does not declare additional mandatory Python runtime dependencies. Composite nodes reuse functionality provided by ComfyUI itself.

## Available nodes

| Group | Node | Internal ID |
|---|---|---|
| Metadata | Diztraido: Metadata Reader | `DiztraidoMetadataReader` |
| Metadata | Diztraido: Metadata Reader Advanced | `DiztraidoImageMetadataReaderAdvanced` |
| Utilities | Backend Random Seed | `BackendRandomSeed` |
| Utilities | Resolution Selector Extended | `DiztraidoResolutionSelector` |
| Utilities | String Manager | `DiztraidoStringManager` |
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
├── pyproject.toml         # Registry metadata and quality-tool configuration
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
