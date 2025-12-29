"""
Base classes for ComfyUI nodes.

This module provides abstract base classes that eliminate boilerplate and enforce
a consistent structure across all custom nodes.
"""

from abc import ABC, abstractmethod
from typing import Any, ClassVar

from ..types import ComfyReturnType, InputSpec, NodeOutput


class BaseNode(ABC):
    """
    Abstract base class for all ComfyUI nodes.

    Provides the standard ComfyUI node interface while enforcing structure and
    enabling shared functionality.

    Subclasses must implement:
    - get_input_spec(): Define node inputs
    - get_return_types(): Define output types
    - process(): Core node logic
    """

    # Class-level configuration (override in subclasses)
    CATEGORY: ClassVar[str] = "weirdion"
    FUNCTION: ClassVar[str] = "process"  # Name of the method ComfyUI will call

    @classmethod
    @abstractmethod
    def get_input_spec(cls) -> InputSpec:
        """
        Define the input specification for this node.

        Returns:
            Dictionary with 'required' and 'optional' keys defining inputs.

        Example:
            {
                "required": {
                    "image": ("IMAGE",),
                    "strength": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 2.0}),
                },
                "optional": {
                    "mask": ("MASK",),
                }
            }
        """

    @classmethod
    @abstractmethod
    def get_return_types(cls) -> tuple[ComfyReturnType, ...]:
        """
        Define the output types for this node.

        Returns:
            Tuple of ComfyUI type strings.

        Example:
            ("IMAGE", "MASK")
        """

    @classmethod
    def get_return_names(cls) -> tuple[str, ...] | None:
        """
        Optional: Define human-readable names for outputs.

        Returns:
            Tuple of names matching return types, or None for defaults.
        """
        return None

    @classmethod
    def INPUT_TYPES(cls) -> dict[str, Any]:  # noqa: N802
        """
        ComfyUI interface method.

        This is called by ComfyUI to determine node inputs. We delegate to
        get_input_spec() which subclasses implement.
        """
        return cls.get_input_spec()

    # ComfyUI expects RETURN_TYPES as a class attribute (not a method or property)
    # We need to set this in __init_subclass__ to properly inherit from get_return_types()
    def __init_subclass__(cls, **kwargs: Any) -> None:
        """Automatically set RETURN_TYPES and RETURN_NAMES as class attributes when subclass is defined."""
        super().__init_subclass__(**kwargs)

        # Only set these if the class implements get_return_types (not abstract)
        if not getattr(cls.get_return_types, "__isabstractmethod__", False):
            cls.RETURN_TYPES = cls.get_return_types()

            # Set RETURN_NAMES if defined
            return_names = cls.get_return_names()
            if return_names is not None:
                cls.RETURN_NAMES = return_names

    @abstractmethod
    def process(self, **kwargs: Any) -> NodeOutput:
        """
        Core node processing logic.

        Args:
            **kwargs: Input values matching the input spec.

        Returns:
            Tuple of output values matching return types.
        """


class ProcessingNode(BaseNode):
    """
    Base class for nodes that process images, latents, or other data.

    Use this for nodes that transform data without side effects.
    """

    CATEGORY: ClassVar[str] = "weirdion/processing"


class UtilityNode(BaseNode):
    """
    Base class for utility nodes (switches, routers, converters).

    Use this for nodes that manage data flow or perform type conversions.
    """

    CATEGORY: ClassVar[str] = "weirdion/utility"


class LoaderNode(BaseNode):
    """
    Base class for loader nodes (models, checkpoints, LoRAs).

    Use this for nodes that load resources from disk or configuration.
    """

    CATEGORY: ClassVar[str] = "weirdion/loaders"


class PromptingNode(BaseNode):
    """
    Base class for prompting nodes (text encoding, LoRA management).

    Use this for nodes that handle text prompts and conditioning.
    """

    CATEGORY: ClassVar[str] = "weirdion/prompting"
