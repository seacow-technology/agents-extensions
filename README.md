# agents-extensions

Public extensions for AgentOS capability system.

## Layout

- `extensions/<extension-id>/manifest.json` - extension manifest
- `extensions/<extension-id>/` - extension implementation package
- `docs/` - extension authoring notes

## Conventions

- Every extension must declare capabilities in `manifest.json`
- Keep network-related behavior auditable and policy-controlled
