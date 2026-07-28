# Diretrizes do repositório

## Arquitetura

- Mantenha o ponto de entrada `__init__.py` mínimo; registre os nós em `nodes/__init__.py`.
- Crie um arquivo por nó em `nodes/`. Não concentre implementações independentes no mesmo módulo.
- Coloque regras reutilizáveis e independentes da interface do ComfyUI em `services/`.
- Centralize endpoints em `routes/` e o registro em `routes/__init__.py`.
- Coloque comportamentos de frontend específicos do ComfyUI em `web/`.
- Preserve a direção de dependências definida em `docs/ARCHITECTURE.md`.

## Compatibilidade

- Preserve IDs de nós e contratos públicos existentes: entradas, saídas, tipos, ordem e estado serializado.
- Não renomeie endpoints consumidos pelo frontend sem migração coordenada.
- Documente mudanças incompatíveis no `CHANGELOG.md` e forneça uma estratégia de migração.

## Idioma

- Toda a aplicação deve usar inglês, incluindo nomes e descrições de nós, widgets, botões, menus, rótulos, previews, mensagens de status, avisos, alertas, erros, exceções e qualquer outro texto visível ao usuário.
- Não adicione textos de interface em português ou espanhol, mesmo quando o código, os comentários internos ou a solicitação original estiverem nesses idiomas.
- A documentação pública é a única parte multilíngue do projeto e deve ser mantida em inglês, português do Brasil e espanhol nas estruturas de tradução já existentes.
- O inglês é a versão canônica da documentação. As versões em português e espanhol devem permanecer semanticamente sincronizadas com ela.

## Qualidade

- Use tipagem, docstrings curtas e nomes claros.
- Evite duplicação, estado global desnecessário e código morto.
- Para novas funcionalidades e correções, adicione ou atualize testes em `tests/`.
- Não versione artefatos gerados, caches, ambientes virtuais, modelos, inputs, outputs ou arquivos temporários.

## Validação

Execute antes de finalizar:

```bash
python -m compileall -q .
python -m unittest discover -s tests -v
```

Quando ferramentas opcionais estiverem instaladas:

```bash
ruff check .
ruff format --check .
```

Valide no ComfyUI quando houver alteração em nós, rotas ou JavaScript. Em instâncias secundárias de teste, use uma porta alternativa e preserve a porta padrão `8188` para a sessão principal do usuário.

## Documentação

- Atualize `docs/NODES.md` ao adicionar ou alterar nós.
- Atualize `docs/ARCHITECTURE.md` ao alterar camadas ou dependências.
- Atualize `docs/DEVELOPMENT.md` ao alterar o processo de desenvolvimento.
- Atualize `README.md` quando houver mudanças de instalação, escopo ou uso.
- Registre alterações relevantes em `CHANGELOG.md`.
- Ao alterar documentação pública, atualize a versão canônica em inglês e sincronize as traduções em português do Brasil e espanhol.
