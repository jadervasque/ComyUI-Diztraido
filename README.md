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

## Como adicionar um nó

1. Crie `nodes/meu_no.py` com a classe do nó.
2. Importe-a em `nodes/__init__.py`.
3. Acrescente a classe em `NODE_CLASS_MAPPINGS` e seu rótulo em `NODE_DISPLAY_NAME_MAPPINGS`.

O ComfyUI carrega somente os mapeamentos exportados pelo `__init__.py` raiz.
