**Idiomas:** [English](../../ARCHITECTURE.md) · [Português (Brasil)](../pt-BR/ARCHITECTURE.md) · [Español](ARCHITECTURE.md)

# Arquitectura

## Descripción general

ComfyUI-Diztraido es una extensión de nodos personalizados para ComfyUI. La arquitectura separa la integración con el host, la presentación de los nodos, las reglas reutilizables, los endpoints HTTP y las extensiones del frontend.

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

## Componentes

### Punto de entrada

El archivo `__init__.py` de la raíz es cargado por ComfyUI. Este archivo:

- importa `NODE_CLASS_MAPPINGS` y `NODE_DISPLAY_NAME_MAPPINGS`;
- registra las rutas locales;
- declara `WEB_DIRECTORY` para cargar las extensiones JavaScript.

Este archivo debe permanecer pequeño y sin reglas de negocio.

### `nodes/`

Contiene la capa de adaptación para ComfyUI:

- definición de entradas y salidas;
- categoría y nombre visible;
- método expuesto mediante el atributo `FUNCTION`;
- delegación a funciones de `services/` cuando existe lógica reutilizable.

El archivo `nodes/__init__.py` es el registro central. Los identificadores presentes en `NODE_CLASS_MAPPINGS` son contratos públicos y no deben modificarse sin una estrategia explícita de migración.

### `services/`

Contiene lógica independiente de la interfaz visual de los nodos, como:

- lectura y normalización de metadatos;
- composición de pipelines nativos de ComfyUI;
- carga coordinada de modelos y LoRAs;
- interpretación y formateo dinámico de cadenas.

Esta capa debe recibir valores, ejecutar reglas y devolver resultados sin depender de widgets del frontend.

### `routes/`

Contiene endpoints HTTP locales utilizados por las extensiones. `routes/__init__.py` centraliza el registro para mantener sencillo el punto de entrada raíz.

Las nuevas rutas deben:

- utilizar un prefijo específico del proyecto;
- validar las entradas recibidas;
- impedir la exposición de rutas arbitrarias;
- devolver errores estructurados sin datos sensibles.

### `web/`

Contiene extensiones JavaScript cargadas por ComfyUI para comportamientos que no pueden expresarse únicamente en el backend, incluidos widgets dinámicos, vistas previas y controles para añadir o eliminar elementos.

El código JavaScript debe localizar los nodos mediante los identificadores registrados en el backend, no únicamente por sus nombres visibles.

### `tests/`

Contiene pruebas unitarias de las reglas y los adaptadores. Las integraciones con módulos de ComfyUI deben simularse cuando la prueba pueda ejecutarse fuera de una instalación completa.

## Flujo de carga

1. ComfyUI encuentra el directorio dentro de `custom_nodes/`.
2. Se importa el archivo `__init__.py` de la raíz.
3. El registro de `nodes/__init__.py` expone las clases de los nodos.
4. Se registran las rutas.
5. El directorio `web/` se expone al frontend.
6. ComfyUI construye los nodos y carga las extensiones JavaScript correspondientes.

## Reglas de dependencia

- `nodes/` puede depender de `services/`.
- `routes/` puede depender de `services/`.
- `services/` no debe depender de `nodes/`, `routes/` ni `web/`.
- `web/` se comunica con el backend mediante contratos públicos y endpoints locales.
- El punto de entrada raíz depende únicamente de los registros centrales.

## Compatibilidad

Al modificar un nodo existente, preserve siempre que sea posible:

- el identificador en `NODE_CLASS_MAPPINGS`;
- los nombres y tipos de las entradas;
- los nombres y tipos de las salidas;
- el orden de las salidas;
- los valores serializados por los widgets;
- los nombres de los endpoints utilizados por el frontend.

Los cambios incompatibles deben documentarse en `CHANGELOG.md` e incluir una estrategia de migración para los flujos de trabajo existentes.
