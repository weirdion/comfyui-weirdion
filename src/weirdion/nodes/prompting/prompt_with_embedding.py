"""
Prompt with Embedding node.

Simplified prompt node that handles embedding insertion and optional text encoding.
"""

from typing import Any

from ...core import PromptingNode, register_node
from ...types import ComfyType, InputSpec, NodeOutput


@register_node(
    name="weirdion_PromptWithEmbedding",
    display_name="Prompt w/ Embedding (weirdion)",
)
class PromptWithEmbeddingNode(PromptingNode):
    """
    Prompt node with embedding support and optional CLIP encoding.

    Features:
    - Insert embedding tags via dropdown
    - Encode to CONDITIONING if CLIP is connected
    - Output TEXT for metadata and downstream use
    """

    @classmethod
    def get_input_spec(cls) -> InputSpec:
        """Define inputs: prompt text, embedding dropdown, and optional CLIP."""
        try:
            import folder_paths

            embedding_list = folder_paths.get_filename_list("embeddings")
            embedding_choices = ["Insert Embedding"] + [name.rsplit(".", 1)[0] for name in embedding_list]
        except Exception:
            # Fallback if ComfyUI imports fail (e.g., during testing)
            embedding_choices = ["Insert Embedding"]

        return {
            "required": {
                "prompt": ("STRING", {"multiline": True, "dynamicPrompts": False}),
                "embedding": (embedding_choices,),
            },
            "optional": {
                "opt_clip": ("CLIP",),
            },
        }

    @classmethod
    def get_return_types(cls) -> tuple[ComfyType, ...]:
        """Returns CONDITIONING and STRING."""
        return ("CONDITIONING", "STRING")

    @classmethod
    def get_return_names(cls) -> tuple[str, ...]:
        """Name the outputs."""
        return ("conditioning", "prompt_text")

    def process(
        self,
        prompt: str,
        embedding: str,
        opt_clip: Any | None = None,
    ) -> NodeOutput:
        """
        Process the prompt and optionally encode to CONDITIONING.

        Note: Embedding insertion is handled by the JavaScript web extension.
        The dropdown is used by the UI to insert text into the prompt field.
        """
        conditioning = None
        if opt_clip is not None:
            try:
                from nodes import CLIPTextEncode

                conditioning = CLIPTextEncode().encode(opt_clip, prompt)[0]
            except Exception as e:
                print(f"[weirdion_PromptWithEmbedding] Warning: Failed to encode prompt: {e}")

        return (conditioning, prompt)
