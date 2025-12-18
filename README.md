# ComfyUI weirdion

A structured, type-safe custom node suite for ComfyUI.

## Philosophy

Built with **structure**, **typing**, and **testing** as first-class concerns. Following DRY and KISS principles while leveraging abstraction and encapsulation for maintainability and scalability.

## Features

- **Type-safe**: Pydantic models and type hints throughout
- **Well-tested**: pytest with fixtures and comprehensive coverage
- **DRY architecture**: Base classes eliminate boilerplate
- **Developer-friendly**: Modern tooling (uv, ruff, mypy)
- **Organized namespaces**: Nodes categorized by purpose

## Installation

### Prerequisites

- Python 3.12+
- [ComfyUI](https://github.com/comfyanonymous/ComfyUI) installed

### Install as Custom Node

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/weirdion/comfyui-weirdion.git
cd comfyui-weirdion
make setup
```

Restart ComfyUI. Nodes will appear under the `weirdion` category.

## Development

### Setup Development Environment

```bash
# Install dependencies
make setup

# Or manually with uv
uv venv
uv pip install -e ".[dev]"
```

### Development Commands

```bash
make test         # Run tests
make lint         # Run linter
make format       # Format code
make type-check   # Run type checking
make all          # Run all checks
```

### Project Structure

```
comfyui-weirdion/
├── src/weirdion/
│   ├── core/              # Base abstractions
│   │   ├── base.py        # BaseNode, ProcessingNode, etc.
│   │   └── registry.py    # Node registration system
│   ├── types/             # Type definitions
│   │   └── comfy_types.py # ComfyUI type aliases
│   ├── nodes/             # Node implementations
│   │   ├── loaders/       # Model/resource loaders
│   │   ├── processors/    # Image/latent processing
│   │   └── utilities/     # Flow control & utilities
│   └── utils/             # Shared utilities
├── tests/
│   ├── unit/              # Unit tests
│   ├── integration/       # Integration tests
│   └── conftest.py        # Pytest fixtures
├── pyproject.toml         # Project configuration
└── Makefile               # Development commands
```

## Creating New Nodes

### Simple Example

```python
from weirdion.core import UtilityNode, register_node
from weirdion.types import ComfyType, InputSpec, NodeOutput


@register_node(name="WDN_MyNode", display_name="My Node (weirdion)")
class MyNode(UtilityNode):
    """Brief description of what this node does."""

    @classmethod
    def get_input_spec(cls) -> InputSpec:
        return {
            "required": {
                "text": ("STRING", {"default": ""}),
                "count": ("INT", {"default": 1, "min": 1, "max": 10}),
            },
        }

    @classmethod
    def get_return_types(cls) -> tuple[ComfyType, ...]:
        return ("STRING",)

    def process(self, text: str, count: int) -> NodeOutput:
        result = text * count
        return (result,)
```

### Base Classes

- **`BaseNode`**: Abstract base for all nodes
- **`ProcessingNode`**: For image/latent processing (category: `weirdion/processing`)
- **`UtilityNode`**: For flow control/utilities (category: `weirdion/utility`)
- **`LoaderNode`**: For loading resources (category: `weirdion/loaders`)

### Testing Your Node

```python
# tests/unit/test_my_node.py
from weirdion.nodes.utilities import MyNode


def test_my_node_basic():
    node = MyNode()
    result = node.process(text="A", count=3)
    assert result == ("AAA",)
```

## Available Nodes

### Utilities

- **Text Combine (WDN_TextCombine)**: Combines two text inputs with a separator

## Contributing

This is a personal repository, but issues and PRs are welcome if they align with the project philosophy.

### Guidelines

1. Follow existing code style (enforced by ruff)
2. Add tests for new functionality
3. Update type hints
4. Keep it DRY and KISS

## License

See [LICENSE](LICENSE) file.
