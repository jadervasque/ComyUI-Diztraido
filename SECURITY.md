**Languages:** [English](SECURITY.md) · [Português (Brasil)](docs/lang/pt-BR/SECURITY.md) · [Español](docs/lang/es/SECURITY.md)

# Security Policy

## Supported versions

This project is under continuous development. Security fixes target the latest version of the `master` branch.

| Version | Supported |
|---|---|
| `master` / unreleased | Yes |
| Older commits and forks | Not guaranteed |

## Reporting a vulnerability

Do not open a public issue for an unpatched vulnerability.

Use the following options in this order:

1. The **Report a vulnerability** feature in the repository's **Security** tab, when available.
2. A private contact method associated with the maintainer's GitHub profile.

Include:

- a description and potential impact;
- the affected component and versions;
- minimal reproduction steps;
- a safe proof of concept when necessary;
- suggested mitigations;
- information about any prior disclosure.

Do not include personal data, credentials, private images, protected models, or third-party content without authorization.

## Expected process

The maintainer will seek to:

- confirm receipt;
- reproduce and classify the issue;
- prepare a fix or mitigation;
- coordinate disclosure after the fix is available.

Timelines depend on severity, reproducibility, and maintainer availability. Submitting a report does not guarantee a financial reward.

## Priority scope

Particularly relevant reports include:

- arbitrary file reads;
- exposure of paths, metadata, or local data;
- unauthorized code or command execution;
- injection into local HTTP routes;
- unsafe handling of uploaded filenames;
- vulnerabilities introduced by JavaScript extensions;
- information leakage through logs or error responses.

## Security practices for users

- Run ComfyUI only in trusted environments.
- Avoid exposing the interface directly to the internet without authentication and network protection.
- Review custom nodes before installing them.
- Keep ComfyUI and its extensions updated.
- Review workflows before sharing them to remove sensitive paths, prompts, or metadata.
