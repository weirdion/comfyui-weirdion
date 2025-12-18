"""
Text combining utility node.

A simple example demonstrating the base node pattern.
"""

from ...core import UtilityNode, register_node
from ...types import ComfyType, InputSpec, NodeOutput


@register_node(name="weirdion_TextCombine", display_name="Text Combine (weirdion)")
class TextCombineNode(UtilityNode):
    """
    Combines multiple text inputs with a separator.

    This is a simple utility node that demonstrates the base node pattern.
    """

    @classmethod
    def get_input_spec(cls) -> InputSpec:
        """Define inputs: two text fields and a separator."""
        return {
            "required": {
                "text1": ("STRING", {"default": "", "multiline": True}),
                "text2": ("STRING", {"default": "", "multiline": True}),
                "separator": ("STRING", {"default": " "}),
            },
        }

    @classmethod
    def get_return_types(cls) -> tuple[ComfyType, ...]:
        """Returns a single STRING output."""
        return ("STRING",)

    @classmethod
    def get_return_names(cls) -> tuple[str, ...]:
        """Name the output 'combined'."""
        return ("combined",)

    def process(self, text1: str, text2: str, separator: str) -> NodeOutput:
        """Combine the text inputs with the separator."""
        combined = f"{text1}{separator}{text2}"
        return (combined,)
