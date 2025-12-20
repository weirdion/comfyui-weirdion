"""
Load Checkpoint node.

Loads a checkpoint and allows optional CLIP/VAE overrides.
"""

from typing import Any

from ...core import LoaderNode, register_node
from ...types import ComfyType, InputSpec, NodeOutput


@register_node(name="weirdion_LoadCheckpointWithOverrides", display_name="Load Checkpoint w/ Overrides (weirdion)")
class LoadCheckpointNode(LoaderNode):
    """
    Load a checkpoint with optional CLIP/VAE overrides.

    If CLIP and/or VAE are provided as inputs, they override the loaded ones.
    """

    @classmethod
    def get_input_spec(cls) -> InputSpec:
        """Define inputs: checkpoint name and optional CLIP/VAE."""
        try:
            import folder_paths

            ckpt_list = folder_paths.get_filename_list("checkpoints")
            ckpt_choices = ["CHOOSE"] + ckpt_list
        except Exception:
            ckpt_choices = ["CHOOSE"]

        return {
            "required": {
                "ckpt_name": (ckpt_choices,),
            },
            "optional": {
                "opt_clip": ("CLIP",),
                "opt_vae": ("VAE",),
            },
        }

    @classmethod
    def get_return_types(cls) -> tuple[ComfyType, ...]:
        """Returns MODEL, CLIP, VAE, STRING."""
        return ("MODEL", "CLIP", "VAE", "STRING")

    @classmethod
    def get_return_names(cls) -> tuple[str, ...]:
        """Name the outputs."""
        return ("model", "clip", "vae", "model_name")

    def process(
        self,
        ckpt_name: str,
        opt_clip: Any | None = None,
        opt_vae: Any | None = None,
    ) -> NodeOutput:
        """Load checkpoint and apply optional overrides."""
        try:
            import comfy.sd
            import folder_paths
        except Exception as e:  # pragma: no cover - ComfyUI runtime only
            raise RuntimeError("ComfyUI runtime dependencies not available") from e

        ckpt_path = folder_paths.get_full_path("checkpoints", ckpt_name)
        outputs = comfy.sd.load_checkpoint_guess_config(
            ckpt_path,
            output_vae=True,
            output_clip=True,
            embedding_directory=folder_paths.get_folder_paths("embeddings"),
        )

        model, loaded_clip, loaded_vae = outputs[:3]

        output_clip = opt_clip if opt_clip is not None else loaded_clip
        output_vae = opt_vae if opt_vae is not None else loaded_vae

        return (model, output_clip, output_vae, ckpt_name)
