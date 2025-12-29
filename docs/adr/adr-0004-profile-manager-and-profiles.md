# ADR-0004: Profile Manager UI and Profiles Storage

Date: 2025-12-20  
Status: Accepted

## Context

Profiles should be editable by non-technical users inside ComfyUI without manual file edits.

## Decision

- Add a top-bar "Profile Manager" modal for creating/editing/deleting profiles.
- Store defaults in `.config/profiles.default.json` (read-only in UI, auto-recreated if missing).
- Store user profiles in `.config/profiles.user.json` (gitignored).
- Profiles include: steps, cfg, sampler, scheduler, denoise, clip_skip, note, and checkpoint associations.
- Support a per-checkpoint default profile mapping.
- Node `Load Profile Input Parameters` reads profiles and outputs generation parameters.

## Consequences

- Profiles persist across workflows and ComfyUI restarts.
- Workflow nodes stay compact while advanced edits live in the modal.
