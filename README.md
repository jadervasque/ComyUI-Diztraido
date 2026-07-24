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
- **Flux Load References**: concentra `CLIPTextEncode` + `FluxGuidance` + encadeamento de referências (`LoadImage` -> `VAEEncode` -> `ReferenceLatent`) em um único nó. Possui botões **Add Reference** e **Remove** para controlar quantas referências ficam ativas.
- **Flux Sampler**: concentra o grupo de processamento (`RandomNoise`, `KSamplerSelect`, `Flux2Scheduler`, `EmptyFlux2LatentImage`, `SamplerCustomAdvanced`, `VAEDecode`) em um único nó.

## Uso dos nós compostos

### Flux Load References

1. Conecte `clip` e `vae`.
2. Preencha `text_prompt`.
3. Defina `guidance`.
4. Clique em **Add Reference** para ativar novos campos `image_ref_N`.
5. Selecione as imagens de referência desejadas.
6. Use a saída `conditioning` para seguir o pipeline.

Opcional: conecte `initial_latent` para aplicar um `ReferenceLatent` inicial antes das imagens.

### Flux Sampler

1. Conecte `model`, `conditioning` e `vae`.
2. Configure `noise_seed`, `sampler_name`, `steps`, `width`, `height` e `batch_size`.
3. Use a saída `image` diretamente no preview ou em pós-processamento.

## Como adicionar um nó

1. Crie `nodes/meu_no.py` com a classe do nó.
2. Importe-a em `nodes/__init__.py`.
3. Acrescente a classe em `NODE_CLASS_MAPPINGS` e seu rótulo em `NODE_DISPLAY_NAME_MAPPINGS`.

O ComfyUI carrega somente os mapeamentos exportados pelo `__init__.py` raiz.
