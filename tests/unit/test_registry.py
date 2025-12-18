"""Tests for the node registry system."""

import pytest

from weirdion.core import NodeRegistry, UtilityNode
from weirdion.types import ComfyType, InputSpec, NodeOutput


class MockNode(UtilityNode):
    """Mock node for testing."""

    @classmethod
    def get_input_spec(cls) -> InputSpec:
        return {"required": {"text": ("STRING", {})}}

    @classmethod
    def get_return_types(cls) -> tuple[ComfyType, ...]:
        return ("STRING",)

    def process(self, text: str) -> NodeOutput:
        return (text,)


def test_registry_initialization() -> None:
    """Test that registry initializes empty."""
    registry = NodeRegistry()
    class_mappings, display_mappings = registry.to_comfy_mappings()

    assert len(class_mappings) == 0
    assert len(display_mappings) == 0


def test_registry_register_node() -> None:
    """Test registering a node."""
    registry = NodeRegistry()
    registry.register(MockNode, name="TestNode", display_name="Test Node")

    class_mappings, display_mappings = registry.to_comfy_mappings()

    assert "TestNode" in class_mappings
    assert class_mappings["TestNode"] is MockNode
    assert display_mappings["TestNode"] == "Test Node"


def test_registry_register_defaults_to_class_name() -> None:
    """Test that registration defaults to class name."""
    registry = NodeRegistry()
    registry.register(MockNode)

    class_mappings, display_mappings = registry.to_comfy_mappings()

    assert "MockNode" in class_mappings
    assert display_mappings["MockNode"] == "MockNode"


def test_registry_prevents_duplicate_names() -> None:
    """Test that duplicate names raise an error."""
    registry = NodeRegistry()
    registry.register(MockNode, name="Duplicate")

    with pytest.raises(ValueError, match="already registered"):
        registry.register(MockNode, name="Duplicate")


def test_registry_as_decorator() -> None:
    """Test using registry.register as a decorator."""
    registry = NodeRegistry()

    @registry.register(name="DecoratedNode", display_name="Decorated")
    class DecoratedNode(UtilityNode):
        @classmethod
        def get_input_spec(cls) -> InputSpec:
            return {"required": {}}

        @classmethod
        def get_return_types(cls) -> tuple[ComfyType, ...]:
            return ("STRING",)

        def process(self) -> NodeOutput:
            return ("test",)

    class_mappings, _ = registry.to_comfy_mappings()
    assert class_mappings["DecoratedNode"] is DecoratedNode
