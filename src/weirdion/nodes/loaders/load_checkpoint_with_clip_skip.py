"""
Load Checkpoint with CLIP skip.

Loads a checkpoint, applies CLIP skip, and allows optional CLIP/VAE overrides.
"""

from typing import Any

from ...core import LoaderNode, register_node
from ...types import ComfyType, InputSpec, NodeOutput


@register_node(
    name="weirdion_LoadCheckpointWithClipSkip",
    display_name="Load Checkpoint w/ Clip Skip (weirdion)",
)
class LoadCheckpointWithClipSkipNode(LoaderNode):
    """
    Load a checkpoint with CLIP skip and optional CLIP/VAE overrides.

    If CLIP and/or VAE are provided as inputs, they override the loaded ones.
    """

    DESCRIPTION = "Load a checkpoint, apply clip skip, and optionally override CLIP/VAE."
    OUTPUT_TOOLTIPS = (
        "U-Net model (denoising latents)",
        "CLIP (text encoder, after clip skip)",
        "VAE (latent/pixel conversion)",
        "Checkpoint name",
        "Clip skip value (string)",
    )

    @classmethod
    def get_input_spec(cls) -> InputSpec:
        """Define inputs: checkpoint name, clip skip, and optional CLIP/VAE."""
        try:
            import folder_paths

            ckpt_list = folder_paths.get_filename_list("checkpoints")
            ckpt_choices = ["Select Checkpoint"] + ckpt_list
        except Exception:
            ckpt_choices = ["Select Checkpoint"]

        return {
            "required": {
                "checkpoint": (
                    ckpt_choices,
                    {"default": "Select Checkpoint", "tooltip": "Checkpoint to load"},
                ),
                "clip_skip": (
                    "INT",
                    {
                        "default": -2,
                        "min": -24,
                        "max": -1,
                        "step": 1,
                        "tooltip": "Stop CLIP at this layer (-1 = no skip)",
                    },
                ),
            },
            "optional": {
                "opt_clip": ("CLIP", {"tooltip": "Optional CLIP override"}),
                "opt_vae": ("VAE", {"tooltip": "Optional VAE override"}),
            },
        }

    @classmethod
    def get_return_types(cls) -> tuple[ComfyType, ...]:
        """Returns MODEL, CLIP, VAE, STRING, STRING."""
        return ("MODEL", "CLIP", "VAE", "STRING", "STRING")

    @classmethod
    def get_return_names(cls) -> tuple[str, ...]:
        """Name the outputs."""
        return ("model", "clip", "vae", "model_name", "clip_skip_value")

    def process(
        self,
        checkpoint: str,
        clip_skip: int,
        opt_clip: Any | None = None,
        opt_vae: Any | None = None,
    ) -> NodeOutput:
        """Load checkpoint, apply clip skip, and apply optional overrides."""
        try:
            import comfy.sd
            import folder_paths
            from nodes import CLIPSetLastLayer
        except Exception as e:  # pragma: no cover - ComfyUI runtime only
            raise RuntimeError("ComfyUI runtime dependencies not available") from e

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
