**Idiomas:** [English](../../../README.md) · [Português (Brasil)](../pt-BR/README.md) · [Español](README.md)

# ComfyUI-Diztraido

[![CI](https://github.com/jadervasque/ComyUI-Diztraido/actions/workflows/ci.yml/badge.svg)](https://github.com/jadervasque/ComyUI-Diztraido/actions/workflows/ci.yml)
[![Versión](https://img.shields.io/badge/versión-0.1.0-blue)](CHANGELOG.md)

Colección de nodos personalizados para ComfyUI, centrada en la composición de flujos de trabajo Flux, la lectura de metadatos y las utilidades reutilizables. El proyecto separa la integración con ComfyUI, las reglas de negocio, las rutas locales, las extensiones JavaScript y las pruebas automatizadas.

> El proyecto está en desarrollo activo. Los identificadores de los nodos y los contratos públicos se preservan para reducir incompatibilidades con flujos de trabajo existentes.

## Características

- Inspección visual y extracción avanzada de metadatos de imágenes.
- Generación de semillas en el backend en cada ejecución.
- Cargadores compuestos para Flux.1 y Flux.2.
- Aplicación secuencial de Low-Rank Adaptation (LoRA) en modelos Flux.
- Encadenamiento de imágenes de referencia con conditioning y guidance.
- Pipeline compuesto de muestreo y decodificación.
- Selector de resolución por relación de aspecto y megapíxeles.
- Gestión de múltiples prompts con una relación de aspecto asociada a cada prompt.
- Formateo de cadenas con entradas dinámicas y expresiones condicionales.
- Extensiones JavaScript para widgets y vistas previas dinámicas.
- Pruebas unitarias e integración continua con GitHub Actions.

## Instalación

### ComfyUI-Manager y Comfy Registry

Busque **Diztraido Nodes** en ComfyUI-Manager e instale el paquete del Registry identificado como `diztraido-nodes`.

Con Comfy CLI, use:

```bash
comfy node install diztraido-nodes
```

Reinicie ComfyUI después de la instalación. Los nodos estarán disponibles en las categorías `Diztraido`.

### Git

Como alternativa, clone el repositorio dentro del directorio `custom_nodes` de su instalación de ComfyUI:

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/jadervasque/ComyUI-Diztraido.git
```

Reinicie ComfyUI. Los nodos estarán disponibles en las categorías `Diztraido`.

### Actualización de una instalación Git

```bash
cd ComfyUI/custom_nodes/ComyUI-Diztraido
git pull
```

Reinicie ComfyUI después de actualizar. Las instalaciones realizadas desde el Registry deben actualizarse mediante ComfyUI-Manager para conservar el control de la versión semántica seleccionada.

## Versionado

La versión actual publicada en el Registry es `0.1.0`. Las versiones publicadas son inmutables y siguen Versionado Semántico. La versión declarada en `pyproject.toml` es la fuente utilizada por el workflow de publicación.

## Requisitos

- Una instalación funcional de ComfyUI.
- Python 3.10 o posterior, respetando las versiones compatibles con la instalación de ComfyUI.
- Los modelos y recursos requeridos por los nodos nativos utilizados en cada flujo de trabajo.

El repositorio no declara dependencias adicionales obligatorias de Python en tiempo de ejecución. Los nodos compuestos reutilizan funcionalidades proporcionadas por ComfyUI.

## Nodos disponibles

| Grupo | Nodo | ID interno |
|---|---|---|
| Metadatos | Diztraido: Metadata Reader | `DiztraidoMetadataReader` |
| Metadatos | Diztraido: Metadata Reader Advanced | `DiztraidoImageMetadataReaderAdvanced` |
| Utilidades | Backend Random Seed | `BackendRandomSeed` |
| Utilidades | Resolution Selector Extended | `DiztraidoResolutionSelector` |
| Utilidades | String Manager | `DiztraidoStringManager` |
| Utilidades | String Format | `DiztraidoStringFormat` |
| Flux | Flux Load References | `DiztraidoReferenceChain` |
| Flux | Flux Sampler | `DiztraidoProcessingBundle` |
| Flux | Load Flux.1 Models | `DiztraidoLoadFlux1Models` |
| Flux | Load Flux.1 Models + LoRAs | `DiztraidoLoadFlux1ModelsLoras` |
| Flux | Load Flux.2 Models | `DiztraidoLoadFlux2Models` |
| Flux | Load Flux.2 Models + LoRAs | `DiztraidoLoadFlux2ModelsLoras` |

Consulte el [catálogo de nodos](NODES.md) para conocer las entradas, salidas, el comportamiento y los ejemplos.

## Documentación

- [Arquitectura](ARCHITECTURE.md): capas, flujo de carga y reglas de compatibilidad.
- [Guía de desarrollo](DEVELOPMENT.md): entorno, pruebas, convenciones y ampliación del proyecto.
- [Catálogo de nodos](NODES.md): descripción funcional de los nodos disponibles.
- [Cómo contribuir](CONTRIBUTING.md): proceso para issues y pull requests.
- [Código de conducta](CODE_OF_CONDUCT.md): comportamiento esperado en los espacios del proyecto.
- [Política de seguridad](SECURITY.md): comunicación responsable de vulnerabilidades.
- [Changelog](CHANGELOG.md): cambios relevantes del proyecto.

La documentación oficial en inglés es la versión canónica. Esta traducción se mantiene en `docs/lang/es/` y cada documento incluye navegación entre idiomas en el encabezado.

## Estructura del repositorio

```text
.
├── .github/               # Workflows y plantillas de colaboración
├── docs/                  # Documentación técnica y funcional
│   └── lang/              # Traducciones al portugués y al español
├── nodes/                 # Adaptadores y definiciones de nodos
├── routes/                # Endpoints locales utilizados por el frontend
├── services/              # Reglas reutilizables y orquestación
├── tests/                 # Pruebas unitarias
├── web/                   # Extensiones JavaScript de ComfyUI
├── __init__.py            # Punto de entrada de la extensión
├── PLAN0.md               # Plan inicial de profesionalización
├── pyproject.toml         # Metadatos del Registry y herramientas de calidad
└── requirements-test.txt  # Dependencias para pruebas fuera de ComfyUI
```

## Pruebas

En un entorno Python aislado, instale primero la dependencia utilizada por las pruebas de metadatos:

```bash
python -m pip install -r requirements-test.txt
```

Después ejecute:

```bash
python -m compileall -q .
python -m unittest discover -s tests -v
```

Las herramientas opcionales, como Ruff, Pytest y Coverage, están configuradas en `pyproject.toml`. Consulte la [guía de desarrollo](DEVELOPMENT.md).

## Contribuciones

Antes de contribuir, lea `CONTRIBUTING.md` y `CODE_OF_CONDUCT.md`. Los pull requests deben preservar los identificadores, las entradas y las salidas de los nodos, salvo que incluyan una estrategia explícita de migración.

## Seguridad

No publique vulnerabilidades aún no corregidas en issues públicas. Siga `SECURITY.md` para conocer las instrucciones de contacto privado y divulgación responsable.

## Licencia y derechos de uso

El código fuente es visible públicamente, pero no se distribuye bajo una licencia open source permisiva. Todos los derechos permanecen reservados según el archivo [`LICENSE`](../../../LICENSE). Contacte al titular de los derechos antes de reutilizar, redistribuir o crear obras derivadas.
