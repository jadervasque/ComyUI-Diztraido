**Languages:** [English](CHANGELOG.md) · [Português (Brasil)](docs/lang/pt-BR/CHANGELOG.md) · [Español](docs/lang/es/CHANGELOG.md)

# Changelog

All notable changes to this project will be documented in this file.

The format follows the principles of [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project follows Semantic Versioning for Registry releases.

## [Unreleased]

## [0.1.0] - 2026-07-27

### Added

- Initial Comfy Registry release under the immutable node ID `diztraido-nodes` and publisher `diztraido`.
- Automated Registry publishing through GitHub Actions when `pyproject.toml` changes on `master`.
- Registry package filtering through `.comfyignore`.
- Brazilian Portuguese and Spanish translations under `docs/lang/`.
- Language navigation in the header of every public documentation file.
- Professionalization planning in `PLAN0.md`.
- Architecture, development, and node catalog documentation under `docs/`.
- Contribution guidelines, code of conduct, and security policy.
- Issue and pull request templates.
- Continuous integration for compilation and tests.
- Dependabot configuration for GitHub Actions.
- Editor standards, Git attributes, and Python tooling configuration.
- Explicit copyright notice and statement that no permissive license is granted.

### Changed

- English is now the canonical language for official documentation.
- README reorganized around installation, features, documentation, maintenance, and Registry installation.
- `pyproject.toml` now declares project metadata and version `0.1.0` for the Comfy Registry.
- `.gitignore` expanded for Python artifacts, editors, operating systems, and local ComfyUI runtime data.

## Previous history

Development before this changelog is recorded in the Git commit history.
