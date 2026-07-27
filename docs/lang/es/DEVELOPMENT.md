**Idiomas:** [English](../../DEVELOPMENT.md) · [Português (Brasil)](../pt-BR/DEVELOPMENT.md) · [Español](DEVELOPMENT.md)

# Guía de desarrollo

## Requisitos previos

- Git.
- Una instalación funcional de ComfyUI.
- Una versión de Python compatible con la instalación de ComfyUI.
- Un entorno con las dependencias propias de ComfyUI disponibles para pruebas de integración.

El proyecto no declara dependencias adicionales obligatorias en tiempo de ejecución. Los nodos compuestos reutilizan clases y recursos proporcionados por ComfyUI.

## Preparación del entorno

Clone el repositorio dentro de `custom_nodes/`:

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/jadervasque/ComyUI-Diztraido.git
cd ComyUI-Diztraido
```

Para trabajar en una rama:

```bash
git switch -c tipo/descripcion-corta
```

Prefijos recomendados:

- `feat/` para funcionalidades;
- `fix/` para correcciones;
- `docs/` para documentación;
- `refactor/` para reorganizaciones internas;
- `chore/` para mantenimiento.

## Pruebas

En un entorno aislado, instale las dependencias utilizadas por la suite:

```bash
python -m pip install -r requirements-test.txt
```

Pillow es importado por las pruebas de metadatos y normalmente ya está disponible en el entorno de ComfyUI.

Ejecute la suite estándar:

```bash
python -m unittest discover -s tests -v
```

Valide también la compilación de los módulos:

```bash
python -m compileall -q .
```

Herramientas opcionales configuradas en `pyproject.toml`:

```bash
python -m pip install ruff pytest coverage
ruff check .
ruff format --check .
pytest
coverage run -m unittest discover -s tests
coverage report
```

La integración continua instala `requirements-test.txt` y ejecuta la compilación y las pruebas unitarias en varias versiones de Python.

## Convenciones de código

### Python

- Utilice cuatro espacios para la indentación.
- Prefiera type hints en funciones reutilizables.
- Mantenga las docstrings breves y objetivas.
- Coloque un nodo por archivo en `nodes/`.
- Extraiga las reglas reutilizables a `services/`.
- Evite importar módulos pesados de ComfyUI en el ámbito global cuando esto impida realizar pruebas aisladas.
- Preserve los identificadores, las entradas y las salidas de los nodos existentes.

### JavaScript

- Utilice dos espacios para la indentación.
- Registre las extensiones con nombres únicos.
- Localice el nodo mediante el identificador de clase del backend.
- Preserve los callbacks originales al extender widgets.
- Evite el estado global y las propiedades con nombres genéricos en los objetos de los nodos.

### Documentación

- Los archivos en inglés son canónicos.
- Actualice `docs/NODES.md` al crear o modificar un nodo.
- Actualice `README.md` cuando cambie el proceso de instalación o el alcance del proyecto.
- Registre los cambios relevantes en `CHANGELOG.md`.
- Mantenga sincronizados con la documentación en inglés los archivos en portugués de Brasil de `docs/lang/pt-BR/` y los archivos en español de `docs/lang/es/`.
- Preserve el encabezado de navegación entre idiomas en todos los documentos públicos.

## Cómo añadir un nodo

1. Cree `nodes/mi_nodo.py`.
2. Defina una clase compatible con el protocolo de nodos de ComfyUI.
3. Coloque las reglas reutilizables en `services/`.
4. Importe la clase en `nodes/__init__.py`.
5. Registre un identificador estable en `NODE_CLASS_MAPPINGS`.
6. Registre la etiqueta en `NODE_DISPLAY_NAME_MAPPINGS`.
7. Añada una extensión en `web/` solo cuando sea necesario.
8. Añada pruebas en `tests/`.
9. Documente el nodo en las tres versiones del catálogo.

## Cómo añadir una ruta

1. Implemente la ruta en un módulo de `routes/`.
2. Mantenga las reglas de negocio en `services/`.
3. Exponga una función de registro idempotente.
4. Llame a esa función desde `routes/__init__.py`.
5. Valide las entradas y gestione los errores esperados.
6. Añada pruebas para parsing, validación y respuestas.

## Validación en ComfyUI

Además de las pruebas unitarias:

1. Reinicie ComfyUI.
2. Confirme que no aparecen errores de importación en el terminal.
3. Verifique que los nodos aparezcan en las categorías esperadas.
4. Cargue un flujo de trabajo existente para detectar incompatibilidades.
5. Pruebe los widgets dinámicos después de guardar y volver a abrir el flujo de trabajo.
6. Utilice un puerto distinto de `8188` para instancias secundarias de validación.

## Lista de comprobación antes de un pull request

- Pruebas nuevas o actualizadas.
- Compilación completada sin errores.
- Ningún identificador público modificado accidentalmente.
- Documentación en inglés, portugués de Brasil y español actualizada.
- `CHANGELOG.md` actualizado cuando corresponda.
- Ningún caché, modelo, imagen de entrada u output incluido en el repositorio.
