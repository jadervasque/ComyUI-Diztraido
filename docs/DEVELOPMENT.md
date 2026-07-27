# Guia de desenvolvimento

## Pré-requisitos

- Git.
- Uma instalação funcional do ComfyUI.
- A versão do Python suportada pela instalação do ComfyUI.
- Ambiente com as dependências do próprio ComfyUI disponíveis para testes de integração.

O projeto não declara dependências obrigatórias adicionais de runtime. Os nós compostos reutilizam classes e recursos fornecidos pelo ComfyUI.

## Preparação do ambiente

Clone o repositório dentro de `custom_nodes/`:

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/jadervasque/ComyUI-Diztraido.git
cd ComyUI-Diztraido
```

Para trabalhar em uma branch:

```bash
git switch -c tipo/descricao-curta
```

Prefixos recomendados:

- `feat/` para funcionalidades;
- `fix/` para correções;
- `docs/` para documentação;
- `refactor/` para reorganizações internas;
- `chore/` para manutenção.

## Testes

Execute a suíte padrão:

```bash
python -m unittest discover -s tests -v
```

Valide também a compilação dos módulos:

```bash
python -m compileall -q .
```

Ferramentas opcionais configuradas em `pyproject.toml`:

```bash
python -m pip install ruff pytest coverage
ruff check .
ruff format --check .
pytest
coverage run -m unittest discover -s tests
coverage report
```

A integração contínua executa compilação e testes unitários em múltiplas versões do Python.

## Convenções de código

### Python

- Use quatro espaços para indentação.
- Prefira type hints em funções reutilizáveis.
- Mantenha docstrings curtas e objetivas.
- Coloque um nó por arquivo em `nodes/`.
- Extraia regras reutilizáveis para `services/`.
- Evite importar módulos pesados do ComfyUI no nível global quando isso impedir testes isolados.
- Preserve IDs, entradas e saídas dos nós existentes.

### JavaScript

- Use dois espaços para indentação.
- Registre extensões com nomes exclusivos.
- Localize o nó pelo ID de classe do backend.
- Preserve callbacks originais ao estender widgets.
- Evite estado global e propriedades com nomes genéricos no objeto do nó.

### Documentação

- Atualize `docs/NODES.md` ao criar ou alterar um nó.
- Atualize `README.md` quando houver mudança no processo de instalação ou no escopo do projeto.
- Registre mudanças relevantes em `CHANGELOG.md`.

## Como adicionar um nó

1. Crie `nodes/meu_no.py`.
2. Defina uma classe compatível com o protocolo de nós do ComfyUI.
3. Coloque regras reutilizáveis em `services/`.
4. Importe a classe em `nodes/__init__.py`.
5. Registre um ID estável em `NODE_CLASS_MAPPINGS`.
6. Registre o rótulo em `NODE_DISPLAY_NAME_MAPPINGS`.
7. Adicione uma extensão em `web/` apenas quando necessário.
8. Adicione testes em `tests/`.
9. Documente o nó em `docs/NODES.md`.

## Como adicionar uma rota

1. Implemente a rota em um módulo de `routes/`.
2. Mantenha regras de negócio em `services/`.
3. Exponha uma função de registro idempotente.
4. Chame essa função em `routes/__init__.py`.
5. Valide entradas e trate erros esperados.
6. Adicione testes para parsing, validação e respostas.

## Validação no ComfyUI

Além dos testes unitários:

1. Reinicie o ComfyUI.
2. Confirme que não há erros de importação no terminal.
3. Verifique se os nós aparecem nas categorias esperadas.
4. Carregue um workflow existente para detectar incompatibilidades.
5. Teste widgets dinâmicos após salvar e reabrir o workflow.
6. Use uma porta diferente de `8188` em instâncias secundárias de validação.

## Checklist antes do pull request

- Testes novos ou atualizados.
- Compilação concluída sem erro.
- Sem IDs públicos alterados acidentalmente.
- Documentação atualizada.
- `CHANGELOG.md` atualizado quando aplicável.
- Sem caches, modelos, imagens de entrada ou saídas versionados.
