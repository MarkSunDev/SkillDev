# Social App Delivery

A Codex skill for building or porting a production-shaped social discovery app without binding the workflow to one programming language or visual system.

The skill covers the product contract, service API, platform-neutral architecture, delivery order, and evidence-based acceptance. It includes a Flutter porting path while remaining applicable to Android, iOS, React Native, web, and other stacks.

## Install

Clone this repository into the Codex skills directory:

```sh
git clone git@gitlab.sitinai.com:max/social-app-delivery.git \
  "${CODEX_HOME:-$HOME/.codex}/skills/social-app-delivery"
```

## Use

```text
Use $social-app-delivery to build or port this social app end-to-end.
```

## Contents

- `SKILL.md` — entrypoint, invariants, and workflow
- `references/product-contract.md` — product scope and feature states
- `references/api-contract.md` — language-neutral service operations
- `references/architecture-contract.md` — layers, adapters, and concurrency
- `references/delivery-playbook.md` — vertical-slice build order and Flutter port
- `references/acceptance-playbook.md` — tests, evidence, and release gates
- `assets/` — product, design, status, and acceptance templates
