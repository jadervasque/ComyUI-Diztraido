# Diretrizes do Repositório

- Mantenha o ponto de entrada __init__.py mínimo; registre os nós em nodes/__init__.py.
- Crie um arquivo por nó em nodes/. Não concentre implementações de nós em um único arquivo.
- Coloque regras reutilizáveis e independentes da interface do ComfyUI em services/.
- Preserve IDs de nós e contratos públicos (entradas, saídas e tipos) existentes, salvo solicitação explícita de alteração.
- Use tipagem, docstrings curtas e nomes claros. Evite duplicação e código morto.
- Não versione artefatos gerados, caches, ambientes virtuais ou arquivos temporários.
- Para novas funcionalidades e correções, adicione ou atualize testes em tests/.
- Antes de finalizar, execute os testes relevantes e valide a compatibilidade com o carregamento do ComfyUI.
- Ao iniciar uma instância do ComfyUI para testes, use uma porta alternativa e preserve a porta padrão 8188 para a sessão principal do usuário.
- Documente no README.md novos nós, alterações relevantes e o processo de extensão do projeto.
