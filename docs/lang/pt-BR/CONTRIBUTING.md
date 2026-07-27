**Idiomas:** [English](../../../CONTRIBUTING.md) · [Português (Brasil)](CONTRIBUTING.md) · [Español](../es/CONTRIBUTING.md)

# Como contribuir

Contribuições são bem-vindas quando preservam a compatibilidade dos workflows e mantêm a separação entre nós, serviços, rotas e frontend.

## Antes de começar

- Procure uma issue existente para evitar trabalho duplicado.
- Para alterações amplas ou incompatíveis, abra primeiro uma proposta descrevendo motivação, impacto e estratégia de migração.
- Não inclua modelos, imagens privadas, outputs, credenciais ou arquivos gerados pelo ComfyUI.

## Relatando bugs

Use o formulário de bug e inclua:

- versão ou commit do ComfyUI;
- sistema operacional e versão do Python;
- passos mínimos para reprodução;
- comportamento esperado e observado;
- logs relevantes sem dados pessoais;
- workflow mínimo, quando puder ser compartilhado com segurança.

Vulnerabilidades não devem ser relatadas em issues públicas. Consulte `SECURITY.md`.

## Propondo funcionalidades

Explique:

- problema que a funcionalidade resolve;
- comportamento esperado;
- impacto sobre nós e workflows existentes;
- alternativas consideradas;
- necessidade de mudanças no backend, frontend ou ambos.

## Fluxo de desenvolvimento

1. Crie uma branch a partir de `master`.
2. Faça alterações pequenas e focadas.
3. Adicione ou atualize testes.
4. Atualize a documentação correspondente em inglês, português do Brasil e espanhol.
5. Execute:

```bash
python -m pip install -r requirements-test.txt
python -m compileall -q .
python -m unittest discover -s tests -v
```

6. Abra um pull request usando o template do repositório.

## Padrões de implementação

- Um arquivo por nó em `nodes/`.
- Regras reutilizáveis em `services/`.
- Registro central em `nodes/__init__.py`.
- Rotas centralizadas por `routes/__init__.py`.
- Extensões visuais em `web/`.
- Testes em `tests/`.
- Type hints e docstrings objetivas em código Python reutilizável.
- IDs de nós, entradas e saídas preservados, salvo migração aprovada.

Consulte `ARCHITECTURE.md` e `DEVELOPMENT.md` para detalhes.

## Commits

Use mensagens curtas no imperativo ou no padrão Conventional Commits:

- `feat: adiciona novo nó`
- `fix: corrige restauração de widget`
- `docs: atualiza guia de instalação`
- `test: cobre cadeia de referências`
- `refactor: separa regra em serviço`
- `chore: atualiza automação`

## Pull requests

Um pull request deve:

- explicar o problema e a solução;
- limitar-se a um objetivo principal;
- informar impactos de compatibilidade;
- incluir evidências de validação;
- atualizar testes e documentação;
- não conter arquivos alheios ao escopo.

A aprovação não é garantida. Mudanças podem precisar de ajustes para manter a compatibilidade com o ComfyUI e com workflows salvos.
