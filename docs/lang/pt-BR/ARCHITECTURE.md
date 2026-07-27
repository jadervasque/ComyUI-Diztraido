**Idiomas:** [English](../../ARCHITECTURE.md) · [Português (Brasil)](ARCHITECTURE.md) · [Español](../es/ARCHITECTURE.md)

# Arquitetura

## Visão geral

O ComfyUI-Diztraido é uma extensão de nós personalizados para o ComfyUI. A arquitetura separa integração com o host, apresentação dos nós, regras reutilizáveis, endpoints HTTP e extensões do frontend.

```text
ComfyUI
  └── __init__.py
      ├── nodes/__init__.py
      │   ├── nodes/*.py
      │   └── services/*.py
      ├── routes/__init__.py
      │   └── routes/*.py
      └── WEB_DIRECTORY = ./web
          └── web/*.js
```

## Componentes

### Ponto de entrada

O `__init__.py` raiz é carregado pelo ComfyUI. Ele:

- importa `NODE_CLASS_MAPPINGS` e `NODE_DISPLAY_NAME_MAPPINGS`;
- registra as rotas locais;
- declara `WEB_DIRECTORY` para carregar as extensões JavaScript.

Esse arquivo deve permanecer pequeno e sem regras de negócio.

### `nodes/`

Contém a camada de adaptação para o ComfyUI:

- definição de entradas e saídas;
- categoria e nome exibido;
- método exposto pelo atributo `FUNCTION`;
- delegação para funções em `services/` quando existe lógica reutilizável.

O arquivo `nodes/__init__.py` é o registro central. IDs presentes em `NODE_CLASS_MAPPINGS` são contratos públicos e não devem ser alterados sem uma estratégia explícita de migração.

### `services/`

Contém lógica independente da interface visual dos nós, como:

- leitura e normalização de metadados;
- composição de pipelines nativos do ComfyUI;
- carregamento coordenado de modelos e LoRAs;
- interpretação e formatação dinâmica de strings.

Essa camada deve receber valores, executar regras e devolver resultados sem depender de widgets do frontend.

### `routes/`

Contém endpoints HTTP locais usados pelas extensões. `routes/__init__.py` centraliza o registro para manter o ponto de entrada raiz simples.

Novas rotas devem:

- usar um prefixo específico do projeto;
- validar entradas recebidas;
- evitar exposição de caminhos arbitrários;
- retornar erros estruturados e sem dados sensíveis.

### `web/`

Contém extensões JavaScript carregadas pelo ComfyUI para comportamentos que não podem ser expressos apenas no backend, incluindo widgets dinâmicos, pré-visualizações e controles de adição ou remoção.

O JavaScript deve localizar nós pelos IDs registrados no backend, não apenas pelos nomes exibidos.

### `tests/`

Contém testes unitários das regras e dos adaptadores. Integrações com módulos do ComfyUI devem ser simuladas quando o teste puder ser executado fora de uma instalação completa.

## Fluxo de carregamento

1. O ComfyUI encontra a pasta em `custom_nodes/`.
2. O `__init__.py` raiz é importado.
3. O registro em `nodes/__init__.py` disponibiliza as classes.
4. As rotas são registradas.
5. O diretório `web/` é informado ao frontend.
6. O ComfyUI constrói os nós e carrega as extensões JavaScript correspondentes.

## Regras de dependência

- `nodes/` pode depender de `services/`.
- `routes/` pode depender de `services/`.
- `services/` não deve depender de `nodes/`, `routes/` ou `web/`.
- `web/` comunica-se com o backend por contratos públicos e endpoints locais.
- O ponto de entrada raiz depende apenas dos registros centrais.

## Compatibilidade

Ao modificar um nó existente, preserve sempre que possível:

- ID em `NODE_CLASS_MAPPINGS`;
- nomes e tipos de entradas;
- nomes e tipos de saídas;
- ordem das saídas;
- valores serializados pelos widgets;
- nomes de endpoints consumidos pelo frontend.

Mudanças incompatíveis devem ser documentadas no `CHANGELOG.md` e acompanhadas de uma estratégia de migração para workflows existentes.
