"""
Load Checkpoint with CLIP skip.

Loads a checkpoint, applies CLIP skip, and allows optional CLIP/VAE overrides.
"""

from typing import Any

from ...core import LoaderNode, register_node
from ...types import ComfyType, InputSpec, NodeOutput
from ...utils.checkpoint_loader import load_checkpoint_with_clip_skip


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
        return load_checkpoint_with_clip_skip(checkpoint, clip_skip, opt_clip=opt_clip, opt_vae=opt_vae)
