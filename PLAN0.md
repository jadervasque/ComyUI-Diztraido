# PLAN0 — Profissionalização do repositório

## Objetivo

Elevar o repositório a um padrão profissional de manutenção e colaboração no GitHub sem alterar os contratos públicos dos nós, os identificadores usados pelo ComfyUI ou a organização necessária para o carregamento da extensão.

## Diagnóstico inicial

A base já possui uma separação funcional adequada:

- `nodes/` contém os adaptadores e registros dos nós do ComfyUI.
- `services/` concentra regras reutilizáveis e orquestração.
- `routes/` registra endpoints HTTP locais.
- `web/` contém extensões JavaScript carregadas pelo ComfyUI.
- `tests/` contém testes automatizados.
- O `__init__.py` raiz mantém o ponto de entrada exigido pelo ComfyUI.

As principais lacunas são documentação de instalação e desenvolvimento, governança de contribuição, templates do GitHub, automação contínua, padrões de editor e uma apresentação mais objetiva do projeto.

## Restrições

- Preservar `NODE_CLASS_MAPPINGS`, `NODE_DISPLAY_NAME_MAPPINGS` e os IDs públicos dos nós.
- Preservar o ponto de entrada raiz, `WEB_DIRECTORY` e o registro das rotas.
- Não mover módulos de execução nesta etapa, evitando quebrar imports relativos ou workflows existentes.
- Não adicionar dependências obrigatórias de runtime.
- Manter documentação e mensagens de colaboração em português.
- Não conceder licença open source sem decisão explícita do proprietário; adicionar apenas um aviso de direitos reservados.

## Plano de implementação

### 1. Estrutura e padrões do repositório

- Ampliar `.gitignore` para caches, ambientes, ferramentas, sistemas operacionais e editores.
- Adicionar `.editorconfig` e `.gitattributes`.
- Adicionar `pyproject.toml` apenas para configuração de ferramentas de qualidade e testes, sem transformar o projeto em um pacote instalável obrigatório.

### 2. Documentação principal

- Reestruturar `README.md` para destacar propósito, recursos, instalação, uso, testes e links internos.
- Criar `docs/ARCHITECTURE.md` com responsabilidades e fluxo de carregamento.
- Criar `docs/DEVELOPMENT.md` com ambiente, testes e convenções.
- Criar `docs/NODES.md` como catálogo detalhado dos nós.
- Criar `CHANGELOG.md` no formato Keep a Changelog.

### 3. Governança e segurança

- Criar `CONTRIBUTING.md`.
- Criar `CODE_OF_CONDUCT.md`.
- Criar `SECURITY.md`.
- Criar `LICENSE` com aviso de direitos reservados, sem presumir uma licença permissiva.

### 4. Integração com GitHub

- Criar template de pull request.
- Criar formulários de issue para bugs e solicitações de funcionalidade.
- Criar configuração de templates e links de segurança.
- Criar workflow de integração contínua para compilação e testes em versões compatíveis do Python.
- Criar configuração do Dependabot para GitHub Actions.

### 5. Validação

- Conferir links relativos e nomes de caminhos.
- Confirmar que os arquivos de runtime existentes não foram movidos.
- Validar sintaxe YAML, TOML e Markdown por inspeção estruturada.
- Executar os testes no workflow de integração contínua após a abertura do pull request.

## Critérios de aceite

- O README permite instalar e compreender o projeto sem consultar o código-fonte.
- A documentação explica arquitetura, desenvolvimento e catálogo de nós.
- Contribuições, segurança e conduta possuem processos definidos.
- Issues e pull requests possuem templates padronizados.
- Pushes e pull requests executam compilação e testes automaticamente.
- Nenhum contrato público ou caminho de runtime do ComfyUI é alterado.
