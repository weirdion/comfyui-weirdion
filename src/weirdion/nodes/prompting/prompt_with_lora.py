"""
Prompt with LoRA node.

Clean, opinionated prompt node that handles LoRA insertion and loading.
"""

from pathlib import Path
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

    DESCRIPTION = "Prompt with LoRA and embedding dropdowns, with optional LoRA loading and encoding."
    OUTPUT_TOOLTIPS = (
        "MODEL with LoRAs applied (if model input provided)",
        "CLIP with LoRAs applied (if clip input provided)",
        "CONDITIONING (if clip input provided)",
        "Prompt text (LoRA tags preserved)",
    )

    @classmethod
    def get_input_spec(cls) -> InputSpec:
        """Define inputs: prompt, LoRA/embedding dropdowns, and optional MODEL/CLIP."""
        # Import here to avoid circular dependencies
        try:
            import folder_paths

            lora_list = folder_paths.get_filename_list("loras")
            # Strip extensions for cleaner display
            lora_choices = ["Insert LoRA"] + [name.rsplit(".", 1)[0] for name in lora_list]
            embedding_list = folder_paths.get_filename_list("embeddings")
            embedding_choices = ["Insert Embedding"] + [name.rsplit(".", 1)[0] for name in embedding_list]
        except Exception:
            # Fallback if ComfyUI imports fail (e.g., during testing)
            lora_choices = ["Insert LoRA"]
            embedding_choices = ["Insert Embedding"]

        return {
            "required": {
                "prompt": (
                    "STRING",
                    {
                        "multiline": True,
                        "dynamicPrompts": False,
                        "tooltip": "Prompt text. LoRA tags like <lora:name:strength> are supported.",
                    },
                ),
                "lora": (
                    lora_choices,
                    {"default": "Insert LoRA", "tooltip": "Insert a LoRA tag into the prompt"},
                ),
                "embedding": (
                    embedding_choices,
                    {"default": "Insert Embedding", "tooltip": "Insert an embedding tag into the prompt"},
                ),
            },
            "optional": {
                "opt_model": ("MODEL", {"tooltip": "Optional MODEL input for LoRA loading"}),
                "opt_clip": ("CLIP", {"tooltip": "Optional CLIP input for LoRA loading and encoding"}),
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
        lora: str,
        embedding: str,
        opt_model: Any | None = None,
        opt_clip: Any | None = None,
    ) -> NodeOutput:
        """
        Process the prompt, handle LoRA loading, and encoding.

        Note: LoRA/embedding insertion is handled by the JavaScript web extension.
        The dropdowns are just used by the UI to insert text into the prompt field.

        Args:
            prompt: Input prompt text with <lora:name:strength> tags and embedding:name tags
            insert_lora: LoRA dropdown (handled by JS, should always be "CHOOSE" at execution)
            insert_embedding: Embedding dropdown (handled by JS, should always be "CHOOSE" at execution)
            model: Optional MODEL input for LoRA loading
            clip: Optional CLIP input for encoding

        Returns:
            (model, clip, conditioning, text) tuple
        """
        # Parse LoRA tags from prompt (insertion already handled by JS extension)
        lora_tags = parse_lora_tags(prompt)

        # Load LoRAs if MODEL and CLIP connected
        if opt_model is not None and opt_clip is not None and lora_tags:
            for lora_tag in lora_tags:
                try:
                    # Import LoraLoader from ComfyUI
                    from nodes import LoraLoader

                    lora_name = self._resolve_lora_name(lora_tag.name)

                    # Load LoRA into model and clip
                    # LoraLoader.load_lora returns (model, clip)
                    opt_model, opt_clip = LoraLoader().load_lora(
                        opt_model, opt_clip, lora_name, lora_tag.strength, lora_tag.strength
                    )
                except Exception as e:
                    # If LoRA loading fails, log but continue
                    print(f"[weirdion_PromptWithLora] Warning: Failed to load LoRA '{lora_tag.name}': {e}")

        # Encode to CONDITIONING if CLIP connected
        conditioning = None
        if opt_clip is not None:
            try:
                from nodes import CLIPTextEncode

                # Strip LoRA tags for clean conditioning
                clean_prompt = strip_lora_tags(prompt)

                # Encode (CLIPTextEncode returns tuple with conditioning as first element)
                conditioning = CLIPTextEncode().encode(opt_clip, clean_prompt)[0]
            except Exception as e:
                print(f"[weirdion_PromptWithLora] Warning: Failed to encode prompt: {e}")

        # Return (model, clip, conditioning, text)
        # Text keeps LoRA tags for Image Saver compatibility
        return (opt_model, opt_clip, conditioning, prompt)

    @staticmethod
    def _resolve_lora_name(name: str) -> str:
        """Resolve a LoRA tag name to a file name if possible."""
        try:
            import folder_paths

            lora_files = folder_paths.get_filename_list("loras")
        except Exception:
            return name

        if name in lora_files:
            return name

        lowered = name.lower()
        for candidate in lora_files:
            candidate_lower = candidate.lower()
            if candidate_lower == lowered:
                return candidate

            candidate_no_ext = Path(candidate).with_suffix("").as_posix().lower()
            if candidate_no_ext == lowered:
                return candidate

        for candidate in lora_files:
            if Path(candidate).stem.lower() == lowered:
                return candidate

        return name
