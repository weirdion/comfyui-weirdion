# ADR-0002: Checkpoint Loading and CLIP Skip

Date: 2025-12-19  
Status: Accepted

## Context

We want checkpoint loaders that align with ComfyUI core behavior and keep CLIP handling consistent across prompts.

## Decision

- Checkpoint loaders use `comfy.sd.load_checkpoint_guess_config(...)`.
- Optional `opt_clip`/`opt_vae` inputs override the loaded CLIP/VAE when connected.
- CLIP skip is applied via `CLIPSetLastLayer` on the chosen CLIP output.
- CLIP skip is applied before encoding both positive and negative prompts.

## Consequences

- Loader behavior stays aligned with upstream ComfyUI.
- CLIP skip remains consistent across prompts unless explicitly split.
