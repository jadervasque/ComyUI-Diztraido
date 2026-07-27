**Idiomas:** [English](../../../CONTRIBUTING.md) · [Português (Brasil)](../pt-BR/CONTRIBUTING.md) · [Español](CONTRIBUTING.md)

# Cómo contribuir

Las contribuciones son bienvenidas cuando preservan la compatibilidad de los flujos de trabajo y mantienen la separación entre nodos, servicios, rutas y frontend.

## Antes de comenzar

- Busque una issue existente para evitar trabajo duplicado.
- Para cambios amplios o incompatibles, abra primero una propuesta que describa la motivación, el impacto y la estrategia de migración.
- No incluya modelos, imágenes privadas, outputs, credenciales ni archivos generados por ComfyUI.

## Comunicación de errores

Utilice el formulario de errores e incluya:

- la versión o el commit de ComfyUI;
- el sistema operativo y la versión de Python;
- pasos mínimos para reproducir el problema;
- comportamiento esperado y observado;
- logs relevantes sin datos personales;
- un flujo de trabajo mínimo cuando pueda compartirse de forma segura.

Las vulnerabilidades no deben comunicarse en issues públicas. Consulte `SECURITY.md`.

## Propuestas de funcionalidades

Explique:

- el problema que resuelve la funcionalidad;
- el comportamiento esperado;
- el impacto sobre los nodos y flujos de trabajo existentes;
- las alternativas consideradas;
- si son necesarios cambios en el backend, el frontend o ambos.

## Flujo de desarrollo

1. Cree una rama a partir de `master`.
2. Realice cambios pequeños y enfocados.
3. Añada o actualice pruebas.
4. Actualice la documentación correspondiente en inglés, portugués de Brasil y español.
5. Ejecute:

```bash
python -m pip install -r requirements-test.txt
python -m compileall -q .
python -m unittest discover -s tests -v
```

6. Abra un pull request utilizando la plantilla del repositorio.

## Estándares de implementación

- Un nodo por archivo en `nodes/`.
- Reglas reutilizables en `services/`.
- Registro central en `nodes/__init__.py`.
- Registro de rutas centralizado mediante `routes/__init__.py`.
- Extensiones visuales en `web/`.
- Pruebas en `tests/`.
- Type hints y docstrings concisas en el código Python reutilizable.
- Preservación de identificadores, entradas y salidas de los nodos, salvo que exista una migración aprobada.

Consulte `ARCHITECTURE.md` y `DEVELOPMENT.md` para obtener más información.

## Commits

Utilice mensajes breves en imperativo o el formato Conventional Commits:

- `feat: añade un nuevo nodo`
- `fix: corrige la restauración de un widget`
- `docs: actualiza la guía de instalación`
- `test: cubre el encadenamiento de referencias`
- `refactor: separa una regla en un servicio`
- `chore: actualiza la automatización`

## Pull requests

Un pull request debe:

- explicar el problema y la solución;
- limitarse a un objetivo principal;
- describir los impactos de compatibilidad;
- incluir evidencias de validación;
- actualizar las pruebas y la documentación;
- evitar archivos ajenos al alcance declarado.

La aprobación no está garantizada. Los cambios pueden requerir ajustes para preservar la compatibilidad con ComfyUI y con los flujos de trabajo guardados.
