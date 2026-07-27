**Languages:** [English](ARCHITECTURE.md) · [Português (Brasil)](lang/pt-BR/ARCHITECTURE.md) · [Español](lang/es/ARCHITECTURE.md)

# Architecture

## Overview

ComfyUI-Diztraido is a custom-node extension for ComfyUI. Its architecture separates host integration, node presentation, reusable rules, HTTP endpoints, and frontend extensions.

```text
ComfyUI
  └── __init__.py
      ├── nodes/__init__.py
      │   ├── nodes/*.py
      │   └── services/*.py
      ├── routes/__init__.py
      │   └── routes/*.py
      └── WEB_DIRECTORY = ./web
          └── web/*.js
```

## Components

### Entry point

The root `__init__.py` is loaded by ComfyUI. It:

- imports `NODE_CLASS_MAPPINGS` and `NODE_DISPLAY_NAME_MAPPINGS`;
- registers local routes;
- declares `WEB_DIRECTORY` so JavaScript extensions are loaded.

This file must remain small and free of business rules.

### `nodes/`

Contains the ComfyUI adapter layer:

- input and output definitions;
- category and display name;
- the method exposed through the `FUNCTION` attribute;
- delegation to functions in `services/` when reusable logic exists.

`nodes/__init__.py` is the central registry. IDs present in `NODE_CLASS_MAPPINGS` are public contracts and must not be changed without an explicit migration strategy.

### `services/`

Contains logic independent of the node user interface, including:

- metadata reading and normalization;
- composition of native ComfyUI pipelines;
- coordinated model and LoRA loading;
- dynamic string interpretation and formatting.

This layer should receive values, execute rules, and return results without depending on frontend widgets.

### `routes/`

Contains local HTTP endpoints used by extensions. `routes/__init__.py` centralizes registration so the root entry point remains simple.

New routes must:

- use a project-specific prefix;
- validate received inputs;
- prevent exposure of arbitrary paths;
- return structured errors without sensitive data.

### `web/`

Contains JavaScript extensions loaded by ComfyUI for behavior that cannot be expressed only in the backend, including dynamic widgets, previews, and add/remove controls.

JavaScript must locate nodes by the IDs registered in the backend, not only by display names.

### `tests/`

Contains unit tests for rules and adapters. Integrations with ComfyUI modules should be mocked when the test can run outside a complete installation.

## Loading flow

1. ComfyUI discovers the directory under `custom_nodes/`.
2. The root `__init__.py` is imported.
3. The registry in `nodes/__init__.py` exposes the node classes.
4. Routes are registered.
5. The `web/` directory is exposed to the frontend.
6. ComfyUI constructs the nodes and loads the corresponding JavaScript extensions.

## Dependency rules

- `nodes/` may depend on `services/`.
- `routes/` may depend on `services/`.
- `services/` must not depend on `nodes/`, `routes/`, or `web/`.
- `web/` communicates with the backend through public contracts and local endpoints.
- The root entry point depends only on central registries.

## Compatibility

When modifying an existing node, preserve whenever possible:

- the ID in `NODE_CLASS_MAPPINGS`;
- input names and types;
- output names and types;
- output order;
- values serialized by widgets;
- endpoint names consumed by the frontend.

Incompatible changes must be documented in `CHANGELOG.md` and accompanied by a migration strategy for existing workflows.
