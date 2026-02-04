"""ComfyUI weirdion custom nodes."""

# Import all node modules to trigger registration
from . import loaders, prompting, processors, utilities

__all__ = ["loaders", "prompting", "processors", "utilities"]
