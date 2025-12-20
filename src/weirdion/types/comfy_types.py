"""
Type definitions for ComfyUI node system.

These types represent the ComfyUI API surface that nodes interact with.
Since ComfyUI itself isn't typed, we define these for type safety in our nodes.
"""

from typing import Any, Literal, TypeAlias

# ComfyUI tensor types (opaque to us, but we know they're passed around)
Image: TypeAlias = Any  # torch.Tensor with shape [B, H, W, C]
Latent: TypeAlias = dict[str, Any]  # Dict with 'samples' key containing tensor
Mask: TypeAlias = Any  # torch.Tensor
Model: TypeAlias = Any  # Diffusion model
Clip: TypeAlias = Any  # Text encoder
VAE: TypeAlias = Any  # Encoder/decoder
ControlNet: TypeAlias = Any  # ControlNet model
Conditioning: TypeAlias = Any  # Encoded prompts

# Primitive types
String: TypeAlias = str
Int: TypeAlias = int
Float: TypeAlias = float
Boolean: TypeAlias = bool

# ComfyUI type strings (used in INPUT_TYPES and RETURN_TYPES)
ComfyType = Literal[
    "IMAGE",
    "LATENT",
    "MASK",
    "MODEL",
    "CLIP",
    "VAE",
    "CONDITIONING",
    "CONTROL_NET",
    "STRING",
    "INT",
    "FLOAT",
    "BOOLEAN",
]


# Widget configuration types
class WidgetConfig:
    """Base type for widget configurations."""


class IntWidgetConfig(WidgetConfig):
    """Configuration for integer input widgets."""

    default: int
    min: int
    max: int
    step: int = 1
    display: Literal["number", "slider"] = "number"


class FloatWidgetConfig(WidgetConfig):
    """Configuration for float input widgets."""

    default: float
    min: float
    max: float
    step: float = 0.01
    display: Literal["number", "slider"] = "number"
    round: float | Literal[False] = 0.01  # Rounding precision


class StringWidgetConfig(WidgetConfig):
    """Configuration for string input widgets."""

    default: str = ""
    multiline: bool = False
    dynamicPrompts: bool = False  # Enable dynamic prompt syntax


# Input type specification
InputSpec = dict[
    str,
    tuple[ComfyType, dict[str, Any]]
    | tuple[list[str],]
    | tuple[list[str], dict[str, Any]],
]

# Node function return type
NodeOutput: TypeAlias = tuple[Any, ...]
