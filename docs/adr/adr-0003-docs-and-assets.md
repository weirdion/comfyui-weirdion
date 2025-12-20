# ADR-0003: Docs and Screenshot Assets

Date: 2025-12-19  
Status: Accepted

## Context

We want lightweight, user-focused docs and consistent screenshots for node documentation.

## Decision

- `README.md` stays user-facing; development details live in `DEVELOPMENT.md`.
- ADRs live in `docs/adr/` and are indexed from `DEVELOPMENT.md`.
- Node screenshots live in `docs/assets/` and follow `node-<slug>.png` naming.
- Screenshots are collapsed in the README using `<details>` blocks.

## Consequences

- Docs are easier to scan without losing reference depth.
- Screenshots stay consistent and discoverable.
