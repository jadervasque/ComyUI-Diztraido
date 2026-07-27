**Languages:** [English](DEVELOPMENT.md) · [Português (Brasil)](lang/pt-BR/DEVELOPMENT.md) · [Español](lang/es/DEVELOPMENT.md)

# Development Guide

## Prerequisites

- Git.
- A working ComfyUI installation.
- A Python version supported by the ComfyUI installation.
- An environment with ComfyUI's own dependencies available for integration tests.

The project does not declare additional mandatory runtime dependencies. Composite nodes reuse classes and resources provided by ComfyUI.

## Environment setup

Clone the repository under `custom_nodes/`:

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/jadervasque/ComyUI-Diztraido.git
cd ComyUI-Diztraido
```

To work on a branch:

```bash
git switch -c type/short-description
```

Recommended prefixes:

- `feat/` for features;
- `fix/` for fixes;
- `docs/` for documentation;
- `refactor/` for internal reorganizations;
- `chore/` for maintenance.

## Tests

In an isolated environment, install the dependencies used by the test suite:

```bash
python -m pip install -r requirements-test.txt
```

Pillow is imported by the metadata tests and is normally already available in the ComfyUI environment.

Run the standard suite:

```bash
python -m unittest discover -s tests -v
```

Also validate module compilation:

```bash
python -m compileall -q .
```

Optional tools configured in `pyproject.toml`:

```bash
python -m pip install ruff pytest coverage
ruff check .
ruff format --check .
pytest
coverage run -m unittest discover -s tests
coverage report
```

Continuous integration installs `requirements-test.txt` and runs compilation and unit tests on multiple Python versions.

## Code conventions

### Python

- Use four spaces for indentation.
- Prefer type hints in reusable functions.
- Keep docstrings concise and objective.
- Place one node per file in `nodes/`.
- Extract reusable rules into `services/`.
- Avoid importing heavy ComfyUI modules at global scope when doing so prevents isolated tests.
- Preserve the IDs, inputs, and outputs of existing nodes.

### JavaScript

- Use two spaces for indentation.
- Register extensions with unique names.
- Locate nodes by the backend class ID.
- Preserve original callbacks when extending widgets.
- Avoid global state and generically named properties on node objects.

### Documentation

- English files are canonical.
- Update `docs/NODES.md` when creating or changing a node.
- Update `README.md` when installation or project scope changes.
- Record relevant changes in `CHANGELOG.md`.
- Keep the Brazilian Portuguese files in `docs/lang/pt-BR/` and the Spanish files in `docs/lang/es/` synchronized with the English documentation.
- Preserve the language-navigation header in every public documentation file.

## Adding a node

1. Create `nodes/my_node.py`.
2. Define a class compatible with the ComfyUI node protocol.
3. Place reusable rules in `services/`.
4. Import the class in `nodes/__init__.py`.
5. Register a stable ID in `NODE_CLASS_MAPPINGS`.
6. Register the label in `NODE_DISPLAY_NAME_MAPPINGS`.
7. Add an extension under `web/` only when necessary.
8. Add tests under `tests/`.
9. Document the node in all three versions of the node catalog.

## Adding a route

1. Implement the route in a module under `routes/`.
2. Keep business rules in `services/`.
3. Expose an idempotent registration function.
4. Call that function from `routes/__init__.py`.
5. Validate inputs and handle expected errors.
6. Add tests for parsing, validation, and responses.

## Validation in ComfyUI

In addition to unit tests:

1. Restart ComfyUI.
2. Confirm that the terminal shows no import errors.
3. Verify that nodes appear under the expected categories.
4. Load an existing workflow to detect incompatibilities.
5. Test dynamic widgets after saving and reopening the workflow.
6. Use a port other than `8188` for secondary validation instances.

## Checklist before a pull request

- New or updated tests.
- Compilation completed without errors.
- No public IDs changed accidentally.
- English, Brazilian Portuguese, and Spanish documentation updated.
- `CHANGELOG.md` updated when applicable.
- No caches, models, input images, or outputs committed.
