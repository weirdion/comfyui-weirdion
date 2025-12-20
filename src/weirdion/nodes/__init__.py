"""ComfyUI weirdion custom nodes."""

# Import all node modules to trigger registration
from . import loaders, prompting, utilities

__all__ = ["loaders", "prompting", "utilities"]
