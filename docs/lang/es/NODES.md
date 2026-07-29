**Idiomas:** [English](../../NODES.md) · [Português (Brasil)](../pt-BR/NODES.md) · [Español](NODES.md)

# Catálogo de nodos

Este documento describe los nodos registrados por ComfyUI-Diztraido. Los nombres internos son contratos utilizados por los flujos de trabajo guardados y las integraciones del frontend.

## Metadatos

### Diztraido: Metadata Reader

- **ID:** `DiztraidoMetadataReader`
- **Finalidad:** panel visual para consultar los metadatos completos de una imagen sin ejecutar el flujo de trabajo.
- **Comportamiento:** actualiza la vista al seleccionar o subir una imagen y permite realizar búsquedas en tiempo real.
- **Salidas:** ninguna; el nodo funciona como panel de inspección.

### Diztraido: Metadata Reader Advanced

- **ID:** `DiztraidoImageMetadataReaderAdvanced`
- **Finalidad:** extraer campos comunes de generación y exponer los metadatos en formatos utilizables por el flujo de trabajo.
- **Datos extraídos:** prompt, prompt negativo, seed, steps, CFG, sampler, scheduler, modelo, dimensiones y contenido completo en texto/JSON, cuando estén disponibles.

## Utilidades

### Backend Random Seed

- **ID:** `BackendRandomSeed`
- **Finalidad:** generar una nueva seed en el backend en cada ejecución del flujo de trabajo.
- **Uso habitual:** variar las generaciones sin depender de una actualización manual del widget en el frontend.

### Resolution Selector Extended

- **ID:** `DiztraidoResolutionSelector`
- **Finalidad:** calcular `width` y `height` a partir de una relación de aspecto, un objetivo en megapíxeles y un múltiplo de alineación.
- **Características:** conserva las proporciones del selector nativo y añade formatos clásicos, sociales, fotográficos y panorámicos.
- **Salidas:** `width` y `height`.
- **Frontend:** muestra la resolución calculada en tiempo real.

### String Manager

- **ID:** `DiztraidoStringManager`
- **Finalidad:** almacenar hasta 24 prompts multilínea, asociar cada prompt con una opción de relación de aspecto y devolver el par seleccionado.
- **Widgets:** `num_fields` controla la cantidad de pares prompt/proporción visibles; `selected_string` elige el par activo.
- **Widgets por campo:** un prompt multilínea y un combo de relación de aspecto con las mismas opciones que **Resolution Selector Extended**.
- **Salidas:** `string_selected` y `resolution_selected`.
- **Conexión:** conecte `resolution_selected` directamente a la entrada `aspect_ratio` de **Resolution Selector Extended**. Los megapíxeles, el múltiplo de alineación y las dimensiones personalizadas permanecen controlados por ese único nodo selector.
- **Automatización:** `selected_string` admite el control posterior a la generación de ComfyUI, lo que permite seleccionar secuencialmente prompts y proporciones en generaciones en cola.

### String Format

- **ID:** `DiztraidoStringFormat`
- **Finalidad:** componer cadenas con entradas dinámicas, líneas opcionales y expresiones condicionales.
- **Entradas dinámicas:** `STRING`, `INT`, `FLOAT` y `BOOLEAN`.
- **Salida:** `string`.

#### Uso

1. Defina `input_count` para crear `input_1`, `input_2` y las entradas siguientes.
2. Conecte los valores.
3. Utilice `{1}`, `{2}` y las demás posiciones para la sustitución normal.
4. Utilice `{1?}`, `{2?}` y las siguientes posiciones cuando deba eliminarse toda la línea física si la entrada es `None` o una cadena vacía/compuesta solo por espacios. El cero numérico y el booleano `false` se conservan como valores válidos.
5. Utilice las directivas de línea completa `@if condición`, `@else` y `@endif` para bloques condicionales. Los bloques pueden anidarse y utilizan los mismos operadores que los ternarios inline.
6. Active `single_line_output` para normalizar párrafos y saltos de línea.

Las llaves literales de objetos, incluidas las llaves JSON normales `{` y `}`, pueden escribirse directamente. Las llaves dobles siguen disponibles cuando debe conservarse literalmente una secuencia similar a un placeholder. Cuando se eliminan líneas opcionales o bloques condicionales, las comas estructurales finales antes de `}` o `]` se limpian automáticamente.

#### Ejemplos

- `Archivo_{1}_prueba_{2}` produce `Archivo_image_prueba_10` para `image` y `10`.
- `"style": "{1?}",` elimina toda la línea cuando `input_1` está vacío.
- `@{{1}?"Texto A":"Texto B"}` selecciona un texto mediante `input_1`.
- `@{{1}=={2}?"Iguales":"Diferentes"}` compara los valores conservando sus tipos.
- `@{{1}&&{2}?"Ambos":"Otro"}` requiere dos entradas verdaderas.
- `@{!({1}||{2})?"Ninguno":"Alguno"}` combina negación y agrupación.
- Un bloque puede contener JSON sin procesar, sin escapar comillas ni llaves:

```text
@if {1}
  "style": "{2}",
@else
  "style": "default",
@endif
```

- `{{nombre}}_{1}` conserva la clave literal e inserta el primer valor.
- Las líneas que comienzan con `#`, incluso después de espacios, se eliminan de la salida.

Operadores compatibles: `==`, `!=`, `<`, `<=`, `>`, `>=`, `!`, `&`, `&&`, `|`, `||` y paréntesis.

## Flux

### Flux Load References

- **ID:** `DiztraidoReferenceChain`
- **Finalidad:** reunir la codificación de texto, el guidance y el encadenamiento de referencias en un solo nodo.
- **Pipeline interno:** `CLIPTextEncode` → `FluxGuidance` → cero o más secuencias `LoadImage` → `VAEEncode` → `ReferenceLatent`.
- **Controles:** los botones **Add Reference** y **Remove** gestionan los campos activos.
- **Entradas principales:** `clip`, `vae`, `text_prompt`, `guidance`, referencias y `initial_latent` opcional.
- **Salidas:** `conditioning` y `vae`.

#### Uso

1. Conecte `clip` y `vae`.
2. Complete `text_prompt`.
3. Defina `guidance`.
4. Añada las referencias necesarias.
5. Conecte opcionalmente `initial_latent`.
6. Envíe `conditioning` y `vae` al resto del pipeline.

### Flux Sampler

- **ID:** `DiztraidoProcessingBundle`
- **Finalidad:** ejecutar el grupo principal de muestreo y decodificación en un único nodo.
- **Pipeline interno:** `RandomNoise`, `BasicGuider`, `KSamplerSelect`, `Flux2Scheduler`, `EmptyFlux2LatentImage`, `SamplerCustomAdvanced` y `VAEDecode`.
- **Entradas principales:** `model`, `conditioning`, `vae`, seed, sampler, steps, anchura, altura y tamaño del batch.
- **Salida:** `image`.

### Load Flux.2 Models

- **ID:** `DiztraidoLoadFlux2Models`
- **Finalidad:** integrar la carga del modelo de difusión, CLIP y VAE para Flux.2.
- **Composición:** `Load Diffusion Model` + `Load CLIP` + `Load VAE`.
- **Valor predeterminado:** tipo `flux2` en el cargador CLIP.
- **Salidas:** `model`, `clip` y `vae`.

### Load Flux.2 Models + LoRAs

- **ID:** `DiztraidoLoadFlux2ModelsLoras`
- **Finalidad:** cargar el conjunto Flux.2 y aplicar varias LoRAs de forma secuencial.
- **Controles:** **Add LoRA** y **Remove**.
- **Configuración por LoRA:** archivo, `strength_model` y `strength_clip`.
- **Salidas:** `model`, `clip` y `vae` después de la cadena de LoRAs.

### Load Flux.1 Models

- **ID:** `DiztraidoLoadFlux1Models`
- **Finalidad:** integrar la carga del modelo de difusión, DualCLIP y VAE para Flux.1.
- **Composición:** `Load Diffusion Model` + `DualCLIPLoader` + `Load VAE`.
- **Valor predeterminado:** tipo `flux` en `DualCLIPLoader`.
- **Salidas:** `model`, `clip` y `vae`.

### Load Flux.1 Models + LoRAs

- **ID:** `DiztraidoLoadFlux1ModelsLoras`
- **Finalidad:** cargar el conjunto Flux.1 y aplicar varias LoRAs de forma secuencial.
- **Controles:** **Add LoRA** y **Remove**.
- **Configuración por LoRA:** archivo, `strength_model` y `strength_clip`.
- **Salidas:** `model`, `clip` y `vae` después de la cadena de LoRAs.

## Compatibilidad de los flujos de trabajo

Al actualizar el proyecto, no modifique manualmente los identificadores de clase en los flujos de trabajo guardados. ComfyUI puede tolerar cambios en los nombres visibles, pero los cambios en identificadores, entradas o salidas pueden impedir que los flujos de trabajo existentes se carguen correctamente.
