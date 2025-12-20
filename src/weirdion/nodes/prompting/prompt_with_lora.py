"""
Prompt with LoRA node.

Clean, opinionated prompt node that handles LoRA insertion and loading.
"""

from typing import Any

from ...core import PromptingNode, register_node
from ...types import ComfyType, InputSpec, NodeOutput
from ...utils import parse_lora_tags, strip_lora_tags


@register_node(name="weirdion_PromptWithLora", display_name="Prompt w/ LoRA (weirdion)")
class PromptWithLoraNode(PromptingNode):
    """
    Prompt node with LoRA support and clean text encoding.

    Features:
    - Parse <lora:name:strength> tags from prompt
    - Load LoRAs into MODEL/CLIP if connected
    - Encode to CONDITIONING if CLIP connected
    - Output TEXT (with LoRA tags for Image Saver compatibility)
    - Insert embeddings via dropdown

    Design Philosophy:
    - Lego pieces: Optional MODEL/CLIP inputs
    - Opinionated: Uncapped strength, default 1.0
    - Text-first: Tags preserved for metadata tools
    """

    @classmethod
    def get_input_spec(cls) -> InputSpec:
        """Define inputs: prompt, LoRA/embedding dropdowns, and optional MODEL/CLIP."""
        # Import here to avoid circular dependencies
        try:
            import folder_paths

            lora_list = folder_paths.get_filename_list("loras")
            # Strip extensions for cleaner display
            lora_choices = ["CHOOSE"] + [name.rsplit(".", 1)[0] for name in lora_list]
            embedding_list = folder_paths.get_filename_list("embeddings")
            embedding_choices = ["CHOOSE"] + [name.rsplit(".", 1)[0] for name in embedding_list]
        except Exception:
            # Fallback if ComfyUI imports fail (e.g., during testing)
            lora_choices = ["CHOOSE"]
            embedding_choices = ["CHOOSE"]

        return {
            "required": {
                "prompt": ("STRING", {"multiline": True, "dynamicPrompts": False}),
                "insert_lora": (lora_choices,),
                "insert_embedding": (embedding_choices,),
            },
            "optional": {
                "model": ("MODEL",),
                "clip": ("CLIP",),
            },
        }

    @classmethod
    def get_return_types(cls) -> tuple[ComfyType, ...]:
        """Returns MODEL, CLIP, CONDITIONING, STRING."""
        return ("MODEL", "CLIP", "CONDITIONING", "STRING")

    @classmethod
    def get_return_names(cls) -> tuple[str, ...]:
        """Name the outputs."""
        return ("model", "clip", "conditioning", "prompt_text")

    def process(
        self,
        prompt: str,
        insert_lora: str,
        insert_embedding: str,
        model: Any | None = None,
        clip: Any | None = None,
    ) -> NodeOutput:
        """
        Process the prompt, handle LoRA insertion, loading, and encoding.

        Args:
            prompt: Input prompt text with <lora:name:strength> tags
            insert_lora: LoRA name from dropdown (inserts <lora:name:1.0> at cursor)
            insert_embedding: Embedding name from dropdown (inserts embedding:name at cursor)
            model: Optional MODEL input for LoRA loading
            clip: Optional CLIP input for encoding

        Returns:
            (model, clip, conditioning, text) tuple
        """
        # Handle dropdown insertions (ComfyUI doesn't provide cursor position, so we append)
        working_prompt = prompt
        insertions = []
        if insert_lora and insert_lora != "CHOOSE":
            insertions.append(f"<lora:{insert_lora}:1.0>")
        if insert_embedding and insert_embedding != "CHOOSE":
            insertions.append(f"embedding:{insert_embedding}")

        if insertions:
            inserted_text = ", ".join(insertions)
            working_prompt = f"{prompt.rstrip()}, {inserted_text}" if prompt else inserted_text

        # Parse LoRA tags from prompt
        lora_tags = parse_lora_tags(working_prompt)

        # Load LoRAs if MODEL and CLIP connected
        if model is not None and clip is not None and lora_tags:
            for lora_tag in lora_tags:
                try:
                    # Import LoraLoader from ComfyUI
                    from nodes import LoraLoader

                    # Load LoRA into model and clip
                    # LoraLoader.load_lora returns (model, clip)
                    model, clip = LoraLoader().load_lora(
                        model, clip, lora_tag.name, lora_tag.strength, lora_tag.strength
                    )
                except Exception as e:
                    # If LoRA loading fails, log but continue
                    print(f"[weirdion_PromptWithLora] Warning: Failed to load LoRA '{lora_tag.name}': {e}")

        # Encode to CONDITIONING if CLIP connected
        conditioning = None
        if clip is not None:
            try:
                from nodes import CLIPTextEncode

                # Strip LoRA tags for clean conditioning
                clean_prompt = strip_lora_tags(working_prompt)

                # Encode (CLIPTextEncode returns tuple with conditioning as first element)
                conditioning = CLIPTextEncode().encode(clip, clean_prompt)[0]
            except Exception as e:
                print(f"[weirdion_PromptWithLora] Warning: Failed to encode prompt: {e}")

        # Return (model, clip, conditioning, text)
        # Text keeps LoRA tags for Image Saver compatibility
        return (model, clip, conditioning, working_prompt)
