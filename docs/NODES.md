**Languages:** [English](NODES.md) · [Português (Brasil)](lang/pt-BR/NODES.md) · [Español](lang/es/NODES.md)

# Node Catalog

This document describes the nodes registered by ComfyUI-Diztraido. Internal names are contracts used by saved workflows and frontend integrations.

## Metadata

### Diztraido: Metadata Reader

- **ID:** `DiztraidoMetadataReader`
- **Purpose:** visual panel for inspecting the complete metadata of an image without executing the workflow.
- **Behavior:** refreshes the view when an image is selected or uploaded and supports real-time search.
- **Outputs:** none; the node operates as an inspection panel.

### Diztraido: Metadata Reader Advanced

- **ID:** `DiztraidoImageMetadataReaderAdvanced`
- **Purpose:** extracts common generation fields and exposes metadata in formats that can be used by the workflow.
- **Extracted data:** prompt, negative prompt, seed, steps, CFG, sampler, scheduler, model, dimensions, and complete text/JSON content when available.

## Utilities

### Backend Random Seed

- **ID:** `BackendRandomSeed`
- **Purpose:** generates a new seed in the backend for every workflow execution.
- **Typical use:** vary generations without manually refreshing a frontend widget.

### Resolution Selector Extended

- **ID:** `DiztraidoResolutionSelector`
- **Purpose:** calculates `width` and `height` from an aspect ratio, megapixel target, and alignment multiple.
- **Features:** preserves the native selector ratios and adds classic, social, photographic, and panoramic formats.
- **Outputs:** `width` and `height`.
- **Frontend:** displays the calculated resolution in real time.

### String Format

- **ID:** `DiztraidoStringFormat`
- **Purpose:** composes strings with dynamic inputs and conditional expressions.
- **Dynamic inputs:** `STRING`, `INT`, `FLOAT`, and `BOOLEAN`.
- **Output:** `string`.

#### Usage

1. Set `input_count` to create `input_1`, `input_2`, and subsequent inputs.
2. Connect the values.
3. Use `{1}`, `{2}`, and other positions in the template.
4. Enable `single_line_output` to normalize paragraphs and line breaks.

#### Examples

- `File_{1}_test_{2}` produces `File_image_test_10` for `image` and `10`.
- `@{{1}?"Text A":"Text B"}` selects text using `input_1`.
- `@{{1}=={2}?"Equal":"Different"}` compares values while preserving their types.
- `@{{1}&&{2}?"Both":"Other"}` requires two true inputs.
- `@{!({1}||{2})?"Neither":"Any"}` combines negation and grouping.
- `{{name}}_{1}` preserves the literal key and inserts the first value.
- Lines beginning with `#`, including after whitespace, are removed from the output.

Supported operators: `==`, `!=`, `<`, `<=`, `>`, `>=`, `!`, `&`, `&&`, `|`, `||`, and parentheses.

## Flux

### Flux Load References

- **ID:** `DiztraidoReferenceChain`
- **Purpose:** combines text encoding, guidance, and reference chaining in one node.
- **Internal pipeline:** `CLIPTextEncode` → `FluxGuidance` → zero or more `LoadImage` → `VAEEncode` → `ReferenceLatent` sequences.
- **Controls:** **Add Reference** and **Remove** manage the active fields.
- **Main inputs:** `clip`, `vae`, `text_prompt`, `guidance`, references, and optional `initial_latent`.
- **Outputs:** `conditioning` and `vae`.

#### Usage

1. Connect `clip` and `vae`.
2. Fill in `text_prompt`.
3. Set `guidance`.
4. Add the required references.
5. Optionally connect `initial_latent`.
6. Route `conditioning` and `vae` to the rest of the pipeline.

### Flux Sampler

- **ID:** `DiztraidoProcessingBundle`
- **Purpose:** runs the main sampling and decoding group in one node.
- **Internal pipeline:** `RandomNoise`, `BasicGuider`, `KSamplerSelect`, `Flux2Scheduler`, `EmptyFlux2LatentImage`, `SamplerCustomAdvanced`, and `VAEDecode`.
- **Main inputs:** `model`, `conditioning`, `vae`, seed, sampler, steps, width, height, and batch size.
- **Output:** `image`.

### Load Flux.2 Models

- **ID:** `DiztraidoLoadFlux2Models`
- **Purpose:** integrates diffusion model, CLIP, and VAE loading for Flux.2.
- **Composition:** `Load Diffusion Model` + `Load CLIP` + `Load VAE`.
- **Default:** `flux2` type in the CLIP loader.
- **Outputs:** `model`, `clip`, and `vae`.

### Load Flux.2 Models + LoRAs

- **ID:** `DiztraidoLoadFlux2ModelsLoras`
- **Purpose:** loads the Flux.2 set and applies multiple LoRAs sequentially.
- **Controls:** **Add LoRA** and **Remove**.
- **Per-LoRA configuration:** file, `strength_model`, and `strength_clip`.
- **Outputs:** `model`, `clip`, and `vae` after the LoRA chain.

### Load Flux.1 Models

- **ID:** `DiztraidoLoadFlux1Models`
- **Purpose:** integrates diffusion model, DualCLIP, and VAE loading for Flux.1.
- **Composition:** `Load Diffusion Model` + `DualCLIPLoader` + `Load VAE`.
- **Default:** `flux` type in `DualCLIPLoader`.
- **Outputs:** `model`, `clip`, and `vae`.

### Load Flux.1 Models + LoRAs

- **ID:** `DiztraidoLoadFlux1ModelsLoras`
- **Purpose:** loads the Flux.1 set and applies multiple LoRAs sequentially.
- **Controls:** **Add LoRA** and **Remove**.
- **Per-LoRA configuration:** file, `strength_model`, and `strength_clip`.
- **Outputs:** `model`, `clip`, and `vae` after the LoRA chain.

## Workflow compatibility

When updating the project, do not manually change class IDs in saved workflows. Display-name changes may be tolerated by ComfyUI, but changes to IDs, inputs, or outputs can prevent existing workflows from loading correctly.
