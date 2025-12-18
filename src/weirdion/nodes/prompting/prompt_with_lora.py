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
    - Load LoRAs into MODEL if connected
    - Encode to CONDITIONING if CLIP connected
    - Output clean TEXT (with LoRA tags for Image Saver compatibility)

    Design Philosophy:
    - Lego pieces: Optional MODEL/CLIP inputs
    - Opinionated: Uncapped strength, default 1.0
    - Text-first: Tags preserved for metadata tools
    """

    @classmethod
    def get_input_spec(cls) -> InputSpec:
        """Define inputs: prompt, optional MODEL/CLIP, and LoRA dropdown."""
        # Import here to avoid circular dependencies
        try:
            import folder_paths

            lora_list = folder_paths.get_filename_list("loras")
            # Strip extensions for cleaner display
            lora_choices = ["CHOOSE"] + [name.rsplit(".", 1)[0] for name in lora_list]
        except Exception:
            # Fallback if ComfyUI imports fail (e.g., during testing)
            lora_choices = ["CHOOSE"]

        return {
            "required": {
                "prompt": ("STRING", {"multiline": True, "dynamicPrompts": False}),
                "lora_strength": ("FLOAT", {"default": 1.0}),
            },
            "optional": {
                "model": ("MODEL",),
                "clip": ("CLIP",),
                "insert_lora": (lora_choices,),
            },
        }

    @classmethod
    def get_return_types(cls) -> tuple[ComfyType, ...]:
        """Returns MODEL, CONDITIONING, CLIP, STRING."""
        return ("MODEL", "CONDITIONING", "CLIP", "STRING")

    @classmethod
    def get_return_names(cls) -> tuple[str, ...]:
        """Name the outputs."""
        return ("model", "conditioning", "clip", "text")

    def process(
        self,
        prompt: str,
        lora_strength: float,
        model: Any | None = None,
        clip: Any | None = None,
        insert_lora: str | None = None,
    ) -> NodeOutput:
        """
        Process the prompt, handle LoRA insertion, loading, and encoding.

        Args:
            prompt: Input prompt text (may contain <lora:> tags)
            lora_strength: Default strength for inserted LoRAs
            model: Optional MODEL input for LoRA loading
            clip: Optional CLIP input for encoding
            insert_lora: LoRA name from dropdown (appends to prompt)

        Returns:
            (model, conditioning, clip, text) tuple
        """
        working_prompt = prompt

        # Handle LoRA dropdown insertion
        if insert_lora and insert_lora != "CHOOSE":
            # Append LoRA tag to prompt
            lora_tag = f"<lora:{insert_lora}:{lora_strength}>"
            working_prompt = f"{working_prompt.rstrip()}, {lora_tag}" if working_prompt else lora_tag

        # Parse LoRA tags from prompt
        lora_tags = parse_lora_tags(working_prompt)

        # Load LoRAs if MODEL connected
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

        # Return (model, conditioning, clip, text)
        # Text keeps LoRA tags for Image Saver compatibility
        return (model, conditioning, clip, working_prompt)
