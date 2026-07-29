**Idiomas:** [English](../../../CHANGELOG.md) · [Português (Brasil)](CHANGELOG.md) · [Español](../es/CHANGELOG.md)

# Changelog

Todas as mudanças relevantes deste projeto serão documentadas neste arquivo.

O formato segue os princípios do [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/), e o projeto segue Versionamento Semântico para lançamentos no Registry.

## [Não lançado]

### Adicionado

- `String Manager`, nó utilitário dinâmico que armazena até 24 prompts multilinha com opções de proporção correspondentes e retorna o prompt e a proporção selecionados para uso direto com o `Resolution Selector Extended`.
- Placeholders de linha opcional do `String Format`, como `{1?}`, e blocos condicionais de linha inteira `@if` / `@else` / `@endif`, incluindo blocos aninhados e limpeza de vírgulas finais para JSON.

### Alterado

- O `String Format` agora aceita chaves JSON literais normais sem exigir duplicação.

## [0.1.0] - 2026-07-27

### Adicionado

- Primeira publicação no Comfy Registry com o ID imutável `diztraido-nodes` e o publisher `diztraido`.
- Publicação automatizada no Registry pelo GitHub Actions quando o `pyproject.toml` for alterado em `master`.
- Filtragem do pacote publicado por meio de `.comfyignore`.
- Traduções para português do Brasil e espanhol em `docs/lang/`.
- Navegação entre idiomas no cabeçalho de cada arquivo público de documentação.
- Planejamento de profissionalização em `PLAN0.md`.
- Documentação de arquitetura, desenvolvimento e catálogo de nós em `docs/`.
- Diretrizes de contribuição, código de conduta e política de segurança.
- Templates para issues e pull requests.
- Integração contínua para compilação e testes.
- Configuração do Dependabot para GitHub Actions.
- Padrões de editor, atributos Git e configuração de ferramentas Python.
- Aviso explícito de direitos autorais e ausência de licença permissiva.

### Alterado

- O inglês passa a ser o idioma canônico da documentação oficial.
- README reorganizado para instalação, recursos, documentação, manutenção e instalação pelo Registry.
- O `pyproject.toml` passa a declarar os metadados do projeto e a versão `0.1.0` para o Comfy Registry.
- `.gitignore` ampliado para artefatos de Python, editores, sistemas operacionais e runtime local do ComfyUI.

## Histórico anterior

O desenvolvimento anterior a este changelog está registrado no histórico de commits do Git.
