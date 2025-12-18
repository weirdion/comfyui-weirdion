"""Tests for individual node implementations."""

from weirdion.nodes.utilities import TextCombineNode


def test_text_combine_basic() -> None:
    """Test basic text combination."""
    node = TextCombineNode()
    result = node.process(text1="Hello", text2="World", separator=" ")

    assert result == ("Hello World",)


def test_text_combine_custom_separator() -> None:
    """Test text combination with custom separator."""
    node = TextCombineNode()
    result = node.process(text1="A", text2="B", separator=", ")

    assert result == ("A, B",)


def test_text_combine_empty_strings() -> None:
    """Test text combination with empty strings."""
    node = TextCombineNode()
    result = node.process(text1="", text2="", separator=" ")

    assert result == (" ",)


def test_text_combine_multiline() -> None:
    """Test text combination with multiline text."""
    node = TextCombineNode()
    result = node.process(text1="Line 1\nLine 2", text2="Line 3\nLine 4", separator="\n")

    assert result == ("Line 1\nLine 2\nLine 3\nLine 4",)


def test_text_combine_input_spec() -> None:
    """Test that input spec is correctly defined."""
    spec = TextCombineNode.get_input_spec()

    assert "required" in spec
    assert "text1" in spec["required"]
    assert "text2" in spec["required"]
    assert "separator" in spec["required"]

    # Check types
    assert spec["required"]["text1"][0] == "STRING"
    assert spec["required"]["text2"][0] == "STRING"
    assert spec["required"]["separator"][0] == "STRING"


def test_text_combine_return_types() -> None:
    """Test that return types are correctly defined."""
    return_types = TextCombineNode.get_return_types()

    assert return_types == ("STRING",)


def test_text_combine_return_names() -> None:
    """Test that return names are correctly defined."""
    return_names = TextCombineNode.get_return_names()

    assert return_names == ("combined",)


def test_text_combine_category() -> None:
    """Test that node is in correct category."""
    assert TextCombineNode.CATEGORY == "weirdion/utility"
