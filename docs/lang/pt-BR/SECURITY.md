**Idiomas:** [English](../../../SECURITY.md) · [Português (Brasil)](SECURITY.md) · [Español](../es/SECURITY.md)

# Política de segurança

## Versões suportadas

Este projeto está em desenvolvimento contínuo. Correções de segurança são direcionadas à versão mais recente da branch `master`.

| Versão | Suporte |
|---|---|
| `master` / não lançada | Sim |
| Commits antigos e forks | Não garantido |

## Como relatar uma vulnerabilidade

Não abra uma issue pública para vulnerabilidades ainda não corrigidas.

Use, nesta ordem:

1. O recurso **Report a vulnerability** na aba **Security** do repositório, quando disponível.
2. Um contato privado associado ao perfil do mantenedor no GitHub.

Inclua:

- descrição e impacto potencial;
- componente e versões afetadas;
- passos mínimos para reprodução;
- prova de conceito segura, quando necessária;
- sugestões de mitigação;
- informações sobre eventual divulgação prévia.

Não inclua dados pessoais, credenciais, imagens privadas, modelos protegidos ou conteúdo de terceiros sem autorização.

## Processo esperado

O mantenedor buscará:

- confirmar o recebimento;
- reproduzir e classificar o problema;
- preparar uma correção ou mitigação;
- coordenar a divulgação após a disponibilização da correção.

Prazos dependem da gravidade, reprodutibilidade e disponibilidade de manutenção. O envio de um relato não garante recompensa financeira.

## Escopo prioritário

São especialmente relevantes:

- leitura arbitrária de arquivos;
- exposição de caminhos, metadados ou dados locais;
- execução de código ou comandos não autorizados;
- injeção em rotas HTTP locais;
- manipulação insegura de nomes de arquivos enviados;
- vulnerabilidades introduzidas por extensões JavaScript;
- vazamento de informações por logs ou respostas de erro.

## Boas práticas para usuários

- Execute o ComfyUI apenas em ambientes confiáveis.
- Evite expor a interface diretamente à internet sem autenticação e proteção de rede.
- Revise custom nodes antes de instalá-los.
- Mantenha o ComfyUI e suas extensões atualizados.
- Não compartilhe workflows que contenham caminhos, prompts ou metadados sensíveis sem revisão.
