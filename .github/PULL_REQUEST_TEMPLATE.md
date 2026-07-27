## Objetivo

<!-- Descreva o problema e o resultado esperado. -->

## Alterações

<!-- Liste as mudanças principais e o motivo de cada uma. -->

- 

## Compatibilidade

<!-- Informe impactos em IDs de nós, entradas, saídas, widgets, rotas ou workflows existentes. -->

- [ ] Não altera contratos públicos do ComfyUI.
- [ ] Altera contratos públicos e inclui estratégia de migração descrita abaixo.
- [ ] Não se aplica.

## Validação

<!-- Inclua comandos executados e testes manuais relevantes. -->

```text
python -m compileall -q .
python -m unittest discover -s tests -v
```

## Checklist

- [ ] O escopo está limitado ao objetivo descrito.
- [ ] Foram adicionados ou atualizados testes.
- [ ] A documentação foi atualizada.
- [ ] O `CHANGELOG.md` foi atualizado quando necessário.
- [ ] Não foram incluídos modelos, outputs, credenciais ou arquivos locais.
- [ ] O projeto foi carregado no ComfyUI quando a mudança exige validação integrada.

## Evidências adicionais

<!-- Logs sanitizados, capturas de tela ou workflows mínimos. Remova esta seção quando não for necessária. -->
