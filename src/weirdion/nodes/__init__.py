"""ComfyUI weirdion custom nodes."""

# Import all node modules to trigger registration
from . import prompting, utilities

__all__ = ["prompting", "utilities"]
