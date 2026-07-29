**Idiomas:** [English](../../../README.md) · [Português (Brasil)](README.md) · [Español](../es/README.md)

# ComfyUI-Diztraido

[![CI](https://github.com/jadervasque/ComyUI-Diztraido/actions/workflows/ci.yml/badge.svg)](https://github.com/jadervasque/ComyUI-Diztraido/actions/workflows/ci.yml)
[![Versão](https://img.shields.io/badge/versão-0.1.0-blue)](CHANGELOG.md)

Coleção de nós personalizados para o ComfyUI, com foco em composição de workflows Flux, leitura de metadados e utilidades reutilizáveis. O projeto separa integração com o ComfyUI, regras de negócio, rotas locais, extensões JavaScript e testes automatizados.

> O projeto está em desenvolvimento. IDs de nós e contratos públicos são preservados para reduzir incompatibilidades com workflows existentes.

## Recursos

- Leitura visual e extração avançada de metadados de imagens.
- Geração de seed no backend a cada execução.
- Carregadores compostos para Flux.1 e Flux.2.
- Aplicação sequencial de Low-Rank Adaptation (LoRA) em modelos Flux.
- Encadeamento de imagens de referência com conditioning e guidance.
- Pipeline composto de amostragem e decodificação.
- Seletor de resolução por proporção e megapixels.
- Gerenciamento de múltiplos prompts com uma proporção associada a cada prompt.
- Formatação de strings com entradas dinâmicas e expressões condicionais.
- Extensões JavaScript para widgets e pré-visualizações dinâmicas.
- Testes unitários e integração contínua no GitHub Actions.

## Instalação

### ComfyUI-Manager e Comfy Registry

Pesquise por **Diztraido Nodes** no ComfyUI-Manager e instale o pacote do Registry identificado como `diztraido-nodes`.

Com o Comfy CLI, use:

```bash
comfy node install diztraido-nodes
```

Reinicie o ComfyUI após a instalação. Os nós estarão disponíveis nas categorias `Diztraido`.

### Git

Como alternativa, clone o repositório dentro da pasta `custom_nodes` da sua instalação do ComfyUI:

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/jadervasque/ComyUI-Diztraido.git
```

Reinicie o ComfyUI. Os nós estarão disponíveis nas categorias `Diztraido`.

### Atualização de uma instalação Git

```bash
cd ComfyUI/custom_nodes/ComyUI-Diztraido
git pull
```

Reinicie o ComfyUI após atualizar. Instalações feitas pelo Registry devem ser atualizadas pelo ComfyUI-Manager, mantendo o controle da versão semântica selecionada.

## Versionamento

A versão atual publicada no Registry é `0.1.0`. Versões publicadas são imutáveis e seguem Versionamento Semântico. A versão declarada no `pyproject.toml` é a fonte usada pelo workflow de publicação.

## Requisitos

- Uma instalação funcional do ComfyUI.
- Python 3.10 ou posterior, respeitando as versões suportadas pela instalação do ComfyUI.
- Modelos e recursos exigidos pelos nós nativos usados em cada workflow.

O repositório não declara dependências Python adicionais obrigatórias de runtime. Os nós compostos reutilizam funcionalidades fornecidas pelo próprio ComfyUI.

## Nós disponíveis

| Grupo | Nó | ID interno |
|---|---|---|
| Metadados | Diztraido: Metadata Reader | `DiztraidoMetadataReader` |
| Metadados | Diztraido: Metadata Reader Advanced | `DiztraidoImageMetadataReaderAdvanced` |
| Utilidades | Backend Random Seed | `BackendRandomSeed` |
| Utilidades | Resolution Selector Extended | `DiztraidoResolutionSelector` |
| Utilidades | String Manager | `DiztraidoStringManager` |
| Utilidades | String Format | `DiztraidoStringFormat` |
| Flux | Flux Load References | `DiztraidoReferenceChain` |
| Flux | Flux Sampler | `DiztraidoProcessingBundle` |
| Flux | Load Flux.1 Models | `DiztraidoLoadFlux1Models` |
| Flux | Load Flux.1 Models + LoRAs | `DiztraidoLoadFlux1ModelsLoras` |
| Flux | Load Flux.2 Models | `DiztraidoLoadFlux2Models` |
| Flux | Load Flux.2 Models + LoRAs | `DiztraidoLoadFlux2ModelsLoras` |

Consulte o [catálogo de nós](NODES.md) para entradas, saídas, comportamento e exemplos.

## Documentação

- [Arquitetura](ARCHITECTURE.md): camadas, fluxo de carregamento e regras de compatibilidade.
- [Desenvolvimento](DEVELOPMENT.md): ambiente, testes, convenções e extensão do projeto.
- [Catálogo de nós](NODES.md): descrição funcional dos nós disponíveis.
- [Como contribuir](CONTRIBUTING.md): processo para issues e pull requests.
- [Código de conduta](CODE_OF_CONDUCT.md): comportamento esperado nos espaços do projeto.
- [Política de segurança](SECURITY.md): relato responsável de vulnerabilidades.
- [Changelog](CHANGELOG.md): alterações relevantes do projeto.

A documentação oficial em inglês é canônica. Esta tradução é mantida em `docs/lang/pt-BR/` e cada documento contém navegação entre idiomas no cabeçalho.

## Estrutura do repositório

```text
.
├── .github/               # Workflows e templates de colaboração
├── docs/                  # Documentação técnica e funcional
│   └── lang/              # Traduções em português e espanhol
├── nodes/                 # Adaptadores e definições dos nós
├── routes/                # Endpoints locais usados pelo frontend
├── services/              # Regras reutilizáveis e orquestração
├── tests/                 # Testes unitários
├── web/                   # Extensões JavaScript do ComfyUI
├── __init__.py            # Ponto de entrada da extensão
├── PLAN0.md               # Plano da profissionalização inicial
├── pyproject.toml         # Metadados do Registry e ferramentas de qualidade
└── requirements-test.txt  # Dependências para testes fora do ComfyUI
```

## Testes

Em um ambiente Python isolado, instale primeiro a dependência usada pelos testes de metadados:

```bash
python -m pip install -r requirements-test.txt
```

Depois execute:

```bash
python -m compileall -q .
python -m unittest discover -s tests -v
```

Ferramentas opcionais, como Ruff, Pytest e Coverage, possuem configuração em `pyproject.toml`. Consulte o [guia de desenvolvimento](DEVELOPMENT.md).

## Contribuição

Antes de contribuir, leia `CONTRIBUTING.md` e `CODE_OF_CONDUCT.md`. Pull requests devem preservar IDs, entradas e saídas dos nós, salvo quando incluírem uma estratégia explícita de migração.

## Segurança

Não publique vulnerabilidades ainda não corrigidas em issues. Siga as instruções de `SECURITY.md` para contato privado e divulgação responsável.

## Licença e direitos de uso

O código está publicamente visível, mas não possui licença open source permissiva. Todos os direitos permanecem reservados conforme o arquivo [`LICENSE`](../../../LICENSE). Entre em contato com o titular antes de reutilizar, redistribuir ou criar trabalhos derivados.
