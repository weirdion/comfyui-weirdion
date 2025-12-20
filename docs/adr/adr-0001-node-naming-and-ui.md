# ADR-0001: Node Naming and UI Conventions

Date: 2025-12-19  
Status: Accepted

## Context

We need consistent naming and UI behavior across nodes to keep workflows readable and reduce rewiring surprises.

## Decision

- Internal node names use the `weirdion_` prefix (e.g., `weirdion_PromptWithLora`).
- Display names end with `(weirdion)` for easy identification.
- Optional inputs use the `opt_` prefix (e.g., `opt_clip`, `opt_vae`).
- Dropdown defaults use friendly labels: "Select Checkpoint", "Insert LoRA", "Insert Embedding".
- Prompt dropdowns do not auto-insert separators or trim text; users control formatting.
- Inputs include `tooltip` text where helpful.

## Consequences

- Renaming inputs may require workflow rewiring.
- Consistent UI and socket naming improves discoverability and reduces clutter.
