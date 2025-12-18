"""
Node registration system for ComfyUI.

Provides a clean API for registering nodes and generating the mappings
that ComfyUI expects.
"""

from typing import Any, TypeAlias

from .base import BaseNode

# ComfyUI expects these exact variable names
NodeClassMappings: TypeAlias = dict[str, type[BaseNode]]
NodeDisplayNameMappings: TypeAlias = dict[str, str]


class NodeRegistry:
    """
    Registry for ComfyUI custom nodes.

    Manages node registration and provides the mappings ComfyUI expects.
    """

    def __init__(self) -> None:
        """Initialize empty registry."""
        self._class_mappings: NodeClassMappings = {}
        self._display_name_mappings: NodeDisplayNameMappings = {}

    def register(
        self,
        node_class: type[BaseNode] | None = None,
        *,
        name: str | None = None,
        display_name: str | None = None,
    ) -> type[BaseNode] | Any:
        """
        Register a node class.

        Can be used as decorator with or without arguments.

        Args:
            node_class: The node class to register (when used without parens)
            name: Internal name (defaults to class name)
            display_name: UI display name (defaults to name)

        Returns:
            The node class (allows chaining)

        Example:
            @registry.register
            class MyNode(BaseNode):
                ...

            # Or with custom names:
            @registry.register(name="WDN_MyNode", display_name="My Node")
            class MyNode(BaseNode):
                ...
        """

        def _register(cls: type[BaseNode]) -> type[BaseNode]:
            internal_name = name or cls.__name__
            ui_name = display_name or internal_name

            if internal_name in self._class_mappings:
                raise ValueError(f"Node '{internal_name}' already registered")

            self._class_mappings[internal_name] = cls
            self._display_name_mappings[internal_name] = ui_name
            return cls

        # Called as @register (without parens)
        if node_class is not None:
            return _register(node_class)

        # Called as @register(...) (with parens)
        return _register

    def get_class_mappings(self) -> NodeClassMappings:
        """
        Get the NODE_CLASS_MAPPINGS dict for ComfyUI.

        Returns:
            Dictionary mapping node names to classes
        """
        return self._class_mappings.copy()

    def get_display_name_mappings(self) -> NodeDisplayNameMappings:
        """
        Get the NODE_DISPLAY_NAME_MAPPINGS dict for ComfyUI.

        Returns:
            Dictionary mapping node names to display names
        """
        return self._display_name_mappings.copy()

    def to_comfy_mappings(self) -> tuple[NodeClassMappings, NodeDisplayNameMappings]:
        """
        Get both mappings as a tuple for easy export.

        Returns:
            (NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS)
        """
        return (self.get_class_mappings(), self.get_display_name_mappings())


# Global registry instance
_global_registry = NodeRegistry()


def register_node(
    name: str | None = None,
    display_name: str | None = None,
) -> Any:
    """
    Decorator for registering nodes with the global registry.

    Args:
        name: Internal node name (defaults to class name)
        display_name: UI display name (defaults to name)

    Returns:
        Decorator function

    Example:
        @register_node(name="WDN_TextCombine", display_name="Text Combine")
        class TextCombineNode(UtilityNode):
            ...
    """

    def decorator(node_class: type[BaseNode]) -> type[BaseNode]:
        return _global_registry.register(node_class, name=name, display_name=display_name)

    return decorator


def get_node_mappings() -> tuple[NodeClassMappings, NodeDisplayNameMappings]:
    """
    Get the global node mappings for ComfyUI.

    Returns:
        (NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS)
    """
    return _global_registry.to_comfy_mappings()
