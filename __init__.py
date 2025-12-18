"""
ComfyUI Weirdion custom nodes entrypoint.

This file is imported by ComfyUI when loading custom nodes.
"""

from src.weirdion import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
