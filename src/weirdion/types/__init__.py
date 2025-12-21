"""Type definitions for ComfyUI weirdion."""

from .comfy_types import (
    VAE,
    Boolean,
    Clip,
    ComfyReturnType,
    ComfyType,
    Conditioning,
    ControlNet,
    Float,
    FloatWidgetConfig,
    Image,
    InputSpec,
    Int,
    IntWidgetConfig,
    Latent,
    Mask,
    Model,
    NodeOutput,
    String,
    StringWidgetConfig,
    WidgetConfig,
)

__all__ = [
    # Type aliases
    "Image",
    "Latent",
    "Mask",
    "Model",
    "Clip",
    "VAE",
    "Conditioning",
    "ControlNet",
    "String",
    "Int",
    "Float",
    "Boolean",
    "ComfyType",
    "ComfyReturnType",
    "InputSpec",
    "NodeOutput",
    # Widget configs
    "WidgetConfig",
    "IntWidgetConfig",
    "FloatWidgetConfig",
    "StringWidgetConfig",
]
