"""Tests for PromptWithEmbeddingNode."""

from weirdion.nodes.prompting import PromptWithEmbeddingNode


def test_prompt_with_embedding_initialization() -> None:
    """Test that node can be instantiated."""
    node = PromptWithEmbeddingNode()
    assert node is not None


def test_prompt_with_embedding_input_spec() -> None:
    """Test that input spec is correctly defined."""
    spec = PromptWithEmbeddingNode.get_input_spec()

    assert "required" in spec
    assert "prompt" in spec["required"]
    assert "embedding" in spec["required"]

    assert "optional" in spec
    assert "opt_clip" in spec["optional"]


def test_prompt_with_embedding_return_types() -> None:
    """Test that return types are correctly defined."""
    types = PromptWithEmbeddingNode.get_return_types()

    assert types == ("CONDITIONING", "STRING")


def test_prompt_with_embedding_return_names() -> None:
    """Test that return names are correctly defined."""
    names = PromptWithEmbeddingNode.get_return_names()

    assert names == ("conditioning", "prompt_text")


def test_prompt_with_embedding_category() -> None:
    """Test that node is in correct category."""
    assert PromptWithEmbeddingNode.CATEGORY == "weirdion/prompting"


def test_prompt_with_embedding_text_only_mode() -> None:
    """Test processing prompt without CLIP (text-only mode)."""
    node = PromptWithEmbeddingNode()
    prompt = "a girl, blonde hair"

    conditioning, text = node.process(
        prompt=prompt,
        embedding="Insert Embedding",
    )

    assert conditioning is None
    assert text == prompt


def test_prompt_with_embedding_preserves_tags() -> None:
    """Test that embedding tags are preserved in text output."""
    node = PromptWithEmbeddingNode()
    prompt = "a girl, embedding:my-embedding"

    conditioning, text = node.process(
        prompt=prompt,
        embedding="Insert Embedding",
    )

    assert text == prompt
    assert "embedding:my-embedding" in text
