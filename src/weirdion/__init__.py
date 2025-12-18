"""
ComfyUI weirdion - Structured Custom Node Suite

A type-safe, well-tested collection of ComfyUI custom nodes.
"""

# Import all node modules to trigger @register_node decorators
from . import nodes  # noqa: F401
from .core.registry import get_node_mappings

# ComfyUI expects these exact variable names in __init__.py
NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS = get_node_mappings()

__all__ = [
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS",
]
