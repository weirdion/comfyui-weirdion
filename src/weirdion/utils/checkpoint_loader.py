"""Checkpoint loading helpers."""

from typing import Any


def load_checkpoint_with_clip_skip(
    checkpoint: str,
    clip_skip: int,
    opt_clip: Any | None = None,
    opt_vae: Any | None = None,
) -> tuple[Any, Any, Any, str, str]:
    """Load a checkpoint, apply clip skip, and optional CLIP/VAE overrides."""
    try:
        import comfy.sd
        import folder_paths
        from nodes import CLIPSetLastLayer
    except Exception as exc:  # pragma: no cover - ComfyUI runtime only
        raise RuntimeError("ComfyUI runtime dependencies not available") from exc

    ckpt_path = folder_paths.get_full_path("checkpoints", checkpoint)
    outputs = comfy.sd.load_checkpoint_guess_config(
        ckpt_path,
        output_vae=True,
        output_clip=True,
        embedding_directory=folder_paths.get_folder_paths("embeddings"),
    )

    model, loaded_clip, loaded_vae = outputs[:3]

    output_clip = opt_clip if opt_clip is not None else loaded_clip
    output_vae = opt_vae if opt_vae is not None else loaded_vae

    if output_clip is not None:
        output_clip = CLIPSetLastLayer().set_last_layer(output_clip, clip_skip)[0]

    return (model, output_clip, output_vae, checkpoint, str(clip_skip))
