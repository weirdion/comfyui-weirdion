"""
ComfyUI weirdion custom nodes entrypoint.

This file is imported by ComfyUI when loading custom nodes.
"""

import sys
from pathlib import Path

# Add src directory to Python path for imports to work
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from weirdion import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS  # noqa: E402
from weirdion.server import register_profile_routes  # noqa: E402

# Register web assets for ComfyUI UI extensions.
WEB_DIRECTORY = "web"

register_profile_routes()

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
