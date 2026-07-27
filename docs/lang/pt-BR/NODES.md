**Idiomas:** [English](../../NODES.md) · [Português (Brasil)](NODES.md) · [Español](../es/NODES.md)

# Catálogo de nós

Este documento descreve os nós registrados pelo ComfyUI-Diztraido. Os nomes internos são contratos usados por workflows salvos e integrações do frontend.

## Metadados

### Diztraido: Metadata Reader

- **ID:** `DiztraidoMetadataReader`
- **Finalidade:** painel visual para consultar os metadados completos de uma imagem sem executar o workflow.
- **Comportamento:** atualiza a visualização ao selecionar ou enviar uma imagem e permite pesquisa em tempo real.
- **Saídas:** nenhuma; o nó funciona como painel de inspeção.

### Diztraido: Metadata Reader Advanced

- **ID:** `DiztraidoImageMetadataReaderAdvanced`
- **Finalidade:** extrair campos comuns de geração e disponibilizar os metadados em formatos utilizáveis no workflow.
- **Dados extraídos:** prompt, prompt negativo, seed, steps, CFG, sampler, scheduler, modelo, dimensões e conteúdo completo em texto/JSON, quando disponíveis.

## Utilidades

### Backend Random Seed

- **ID:** `BackendRandomSeed`
- **Finalidade:** gerar uma nova seed no backend a cada execução do workflow.
- **Uso típico:** variar gerações sem depender de atualização manual do widget no frontend.

### Resolution Selector Extended

- **ID:** `DiztraidoResolutionSelector`
- **Finalidade:** calcular `width` e `height` a partir de proporção, alvo em megapixels e múltiplo de alinhamento.
- **Recursos:** mantém as proporções do seletor nativo e adiciona formatos clássicos, sociais, fotográficos e panorâmicos.
- **Saídas:** `width` e `height`.
- **Frontend:** exibe a resolução calculada em tempo real.

### String Format

- **ID:** `DiztraidoStringFormat`
- **Finalidade:** compor strings com entradas dinâmicas e expressões condicionais.
- **Entradas dinâmicas:** `STRING`, `INT`, `FLOAT` e `BOOLEAN`.
- **Saída:** `string`.

#### Uso

1. Defina `input_count` para criar `input_1`, `input_2` e entradas subsequentes.
2. Conecte os valores.
3. Use `{1}`, `{2}` e demais posições no template.
4. Ative `single_line_output` para normalizar parágrafos e quebras de linha.

#### Exemplos

- `File_{1}_teste_{2}` produz `File_image_teste_10` para `image` e `10`.
- `@{{1}?"Texto A":"Texto B"}` escolhe um texto usando `input_1`.
- `@{{1}=={2}?"Iguais":"Diferentes"}` compara preservando os tipos.
- `@{{1}&&{2}?"Ambos":"Outro"}` exige duas entradas verdadeiras.
- `@{!({1}||{2})?"Nenhum":"Algum"}` combina negação e agrupamento.
- `{{nome}}_{1}` preserva a chave literal e insere o primeiro valor.
- Linhas iniciadas por `#`, inclusive após espaços, são removidas da saída.

Operadores suportados: `==`, `!=`, `<`, `<=`, `>`, `>=`, `!`, `&`, `&&`, `|`, `||` e parênteses.

## Flux

### Flux Load References

- **ID:** `DiztraidoReferenceChain`
- **Finalidade:** reunir codificação de texto, guidance e encadeamento de referências em um único nó.
- **Pipeline interno:** `CLIPTextEncode` → `FluxGuidance` → zero ou mais sequências `LoadImage` → `VAEEncode` → `ReferenceLatent`.
- **Controles:** botões **Add Reference** e **Remove** administram os campos ativos.
- **Entradas principais:** `clip`, `vae`, `text_prompt`, `guidance`, referências e `initial_latent` opcional.
- **Saídas:** `conditioning` e `vae`.

#### Uso

1. Conecte `clip` e `vae`.
2. Preencha `text_prompt`.
3. Defina `guidance`.
4. Adicione as referências necessárias.
5. Opcionalmente conecte `initial_latent`.
6. Encaminhe `conditioning` e `vae` ao restante do pipeline.

### Flux Sampler

- **ID:** `DiztraidoProcessingBundle`
- **Finalidade:** executar o grupo principal de amostragem e decodificação em um único nó.
- **Pipeline interno:** `RandomNoise`, `BasicGuider`, `KSamplerSelect`, `Flux2Scheduler`, `EmptyFlux2LatentImage`, `SamplerCustomAdvanced` e `VAEDecode`.
- **Entradas principais:** `model`, `conditioning`, `vae`, seed, sampler, steps, largura, altura e batch.
- **Saída:** `image`.

### Load Flux.2 Models

- **ID:** `DiztraidoLoadFlux2Models`
- **Finalidade:** integrar carregamento do modelo de difusão, CLIP e VAE para Flux.2.
- **Composição:** `Load Diffusion Model` + `Load CLIP` + `Load VAE`.
- **Padrão:** tipo `flux2` no carregador CLIP.
- **Saídas:** `model`, `clip` e `vae`.

### Load Flux.2 Models + LoRAs

- **ID:** `DiztraidoLoadFlux2ModelsLoras`
- **Finalidade:** carregar o conjunto Flux.2 e aplicar múltiplas LoRAs em sequência.
- **Controles:** **Add LoRA** e **Remove**.
- **Configuração por LoRA:** arquivo, `strength_model` e `strength_clip`.
- **Saídas:** `model`, `clip` e `vae` após a cadeia de LoRAs.

### Load Flux.1 Models

- **ID:** `DiztraidoLoadFlux1Models`
- **Finalidade:** integrar carregamento do modelo de difusão, DualCLIP e VAE para Flux.1.
- **Composição:** `Load Diffusion Model` + `DualCLIPLoader` + `Load VAE`.
- **Padrão:** tipo `flux` no `DualCLIPLoader`.
- **Saídas:** `model`, `clip` e `vae`.

### Load Flux.1 Models + LoRAs

- **ID:** `DiztraidoLoadFlux1ModelsLoras`
- **Finalidade:** carregar o conjunto Flux.1 e aplicar múltiplas LoRAs em sequência.
- **Controles:** **Add LoRA** e **Remove**.
- **Configuração por LoRA:** arquivo, `strength_model` e `strength_clip`.
- **Saídas:** `model`, `clip` e `vae` após a cadeia de LoRAs.

## Compatibilidade de workflows

Ao atualizar o projeto, não altere manualmente IDs de classe em workflows salvos. Mudanças de nomes exibidos podem ser toleradas pelo ComfyUI, mas mudanças em IDs, entradas ou saídas podem impedir o carregamento correto de workflows existentes.
