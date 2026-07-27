**Idiomas:** [English](../../../SECURITY.md) · [Português (Brasil)](../pt-BR/SECURITY.md) · [Español](SECURITY.md)

# Política de seguridad

## Versiones compatibles

Este proyecto está en desarrollo continuo. Las correcciones de seguridad se aplican a la versión más reciente de la rama `master`.

| Versión | Compatibilidad |
|---|---|
| `master` / no publicada | Sí |
| Commits antiguos y forks | No garantizada |

## Cómo comunicar una vulnerabilidad

No abra una issue pública para una vulnerabilidad que aún no haya sido corregida.

Utilice las siguientes opciones en este orden:

1. La función **Report a vulnerability** de la pestaña **Security** del repositorio, cuando esté disponible.
2. Un medio de contacto privado asociado al perfil de GitHub del mantenedor.

Incluya:

- una descripción y el impacto potencial;
- el componente y las versiones afectadas;
- pasos mínimos para reproducir el problema;
- una prueba de concepto segura cuando sea necesaria;
- sugerencias de mitigación;
- información sobre cualquier divulgación previa.

No incluya datos personales, credenciales, imágenes privadas, modelos protegidos ni contenido de terceros sin autorización.

## Proceso esperado

El mantenedor intentará:

- confirmar la recepción;
- reproducir y clasificar el problema;
- preparar una corrección o mitigación;
- coordinar la divulgación después de que la corrección esté disponible.

Los plazos dependen de la gravedad, la reproducibilidad y la disponibilidad del mantenedor. El envío de un informe no garantiza una recompensa económica.

## Alcance prioritario

Son especialmente relevantes:

- lectura arbitraria de archivos;
- exposición de rutas, metadatos o datos locales;
- ejecución no autorizada de código o comandos;
- inyección en rutas HTTP locales;
- gestión insegura de nombres de archivos subidos;
- vulnerabilidades introducidas por extensiones JavaScript;
- filtración de información mediante logs o respuestas de error.

## Buenas prácticas para usuarios

- Ejecute ComfyUI únicamente en entornos de confianza.
- Evite exponer la interfaz directamente a internet sin autenticación y protección de red.
- Revise los custom nodes antes de instalarlos.
- Mantenga ComfyUI y sus extensiones actualizados.
- Revise los flujos de trabajo antes de compartirlos para eliminar rutas, prompts o metadatos sensibles.
