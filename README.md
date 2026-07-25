# ComfyUI-Diztraido

Nós personalizados para o ComfyUI, organizados para facilitar manutenção e inclusão de novas funcionalidades.

## Estrutura

- `nodes/`: um arquivo por nó e o registro central em `nodes/__init__.py`.
- `services/`: regras reutilizáveis que não pertencem à interface dos nós.
- `routes/`: endpoints locais consumidos pela interface dos nós.
- `web/`: extensões JavaScript carregadas pelo ComfyUI.
- `__init__.py`: ponto de entrada mínimo exigido pelo ComfyUI.

## Nós disponíveis

- **Diztraido: Metadata Reader**: painel visual sem saídas. Ao escolher ou enviar uma imagem, mostra imediatamente o JSON completo dos metadados e permite buscá-lo em tempo real, sem executar o workflow.
- **Diztraido: Metadata Reader Advanced**: extrai prompt, prompt negativo, seed, steps, CFG, sampler, scheduler, modelo, dimensões e os metadados em texto/JSON.
- **Backend Random Seed**: gera uma seed nova a cada execução do workflow.
- **Flux Load References**: concentra `CLIPTextEncode` + `FluxGuidance` + encadeamento de referências (`LoadImage` -> `VAEEncode` -> `ReferenceLatent`) em um único nó. Possui botões **Add Reference** e **Remove** para controlar quantas referências ficam ativas e encaminha o `vae` de entrada para a saída.
- **Flux Sampler**: concentra o grupo de processamento (`RandomNoise`, `KSamplerSelect`, `Flux2Scheduler`, `EmptyFlux2LatentImage`, `SamplerCustomAdvanced`, `VAEDecode`) em um único nó.
- **Load Flux.2 Models**: integra `Load Diffusion Model` + `Load CLIP` + `Load VAE` em um único nó, mantendo os mesmos campos dos nós originais e com `type=flux2` como padrão no `Load CLIP`.
- **Load Flux.2 Models + LoRAs**: integra `Load Diffusion Model` + `Load CLIP` + `Load VAE` e aplica múltiplas LoRAs em sequência, com botões **Add LoRA** e **Remove**.
- **Load Flux.1 Models**: integra `Load Diffusion Model` + `DualCLIPLoader` + `Load VAE` em um único nó, mantendo os mesmos campos dos nós originais e com `type=flux` como padrão no `DualCLIPLoader`.
- **String Format**: monta uma string com entradas dinâmicas `STRING`, `INT`, `FLOAT` ou `BOOLEAN`, placeholders posicionais e expressões ternárias booleanas.

## Uso dos nós compostos

### Flux Load References

1. Conecte `clip` e `vae`.
2. Preencha `text_prompt`.
3. Defina `guidance`.
4. Clique em **Add Reference** para ativar novos campos `image_ref_N`.
5. Selecione as imagens de referência desejadas.
6. Use as saídas `conditioning` e `vae` para seguir o pipeline de forma ordenada.

Opcional: conecte `initial_latent` para aplicar um `ReferenceLatent` inicial antes das imagens.

### Flux Sampler

1. Conecte `model`, `conditioning` e `vae`.
2. Configure `noise_seed`, `sampler_name`, `steps`, `width`, `height` e `batch_size`.
3. Use a saída `image` diretamente no preview ou em pós-processamento.

### Load Flux.2 Models

1. Configure os campos de `Load Diffusion Model`.
2. Configure os campos de `Load CLIP` (com `type=flux2` por padrão).
3. Configure o `Load VAE`.
4. Use as saídas `model`, `clip` e `vae` no workflow.

### Load Flux.2 Models + LoRAs

1. Configure os campos de `Load Diffusion Model`.
2. Configure os campos de `Load CLIP` (com `type=flux2` por padrão).
3. Configure o `Load VAE`.
4. Clique em **Add LoRA** para ativar campos de LoRA.
5. Para cada LoRA, selecione o arquivo e ajuste `strength_model` e `strength_clip`.
6. Use as saídas `model`, `clip` e `vae` no workflow.

### Load Flux.1 Models

1. Configure os campos de `Load Diffusion Model`.
2. Configure os campos de `DualCLIPLoader` (com `type=flux` por padrão).
3. Configure o `Load VAE`.
4. Use as saídas `model`, `clip` e `vae` no workflow.

### String Format

1. Defina `input_count` para criar os sockets `input_1`, `input_2`, etc.
2. Conecte valores `STRING`, `INT`, `FLOAT` ou `BOOLEAN`; o tipo é reconhecido automaticamente.
3. Use `{1}`, `{2}`, etc. no campo `template` para inserir os valores pela posição.
4. Use a saída `string` no restante do workflow.

Exemplos:

- `File_{1}_teste_{2}` produz `File_image_teste_10` para as entradas `image` e `10`.
- `@{{1}?"Texto A":"Texto B"}` escolhe o texto usando `input_1`.
- `@{{1}&&{2}?"Ambos":"Outro"}` exige que as duas entradas sejam verdadeiras.
- `@{!({1}||{2})?"Nenhum":"Algum"}` combina negação e parênteses.
- `{{nome}}_{1}` produz uma chave literal: `{nome}_valor`.

Operadores suportados: `!`, `&`, `&&`, `|`, `||` e parênteses. `&&`/`&` têm precedência sobre `||`/`|`. Strings `true`, `1`, `yes` e `on` são verdadeiras; `false`, `0`, `no`, `off`, `none`, `null` e string vazia são falsas.

## Como adicionar um nó

1. Crie `nodes/meu_no.py` com a classe do nó.
2. Importe-a em `nodes/__init__.py`.
3. Acrescente a classe em `NODE_CLASS_MAPPINGS` e seu rótulo em `NODE_DISPLAY_NAME_MAPPINGS`.

O ComfyUI carrega somente os mapeamentos exportados pelo `__init__.py` raiz.
