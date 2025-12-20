"""Tests for PromptWithLoraNode."""

from weirdion.nodes.prompting import PromptWithLoraNode


def test_prompt_with_lora_initialization() -> None:
    """Test that node can be instantiated."""
    node = PromptWithLoraNode()
    assert node is not None


def test_prompt_with_lora_input_spec() -> None:
    """Test that input spec is correctly defined."""
    spec = PromptWithLoraNode.get_input_spec()

    assert "required" in spec
    assert "prompt" in spec["required"]
    assert "insert_lora" in spec["required"]
    assert "insert_embedding" in spec["required"]

    assert "optional" in spec
    assert "model" in spec["optional"]
    assert "clip" in spec["optional"]


def test_prompt_with_lora_return_types() -> None:
    """Test that return types are correctly defined."""
    types = PromptWithLoraNode.get_return_types()

    assert types == ("MODEL", "CLIP", "CONDITIONING", "STRING")


def test_prompt_with_lora_return_names() -> None:
    """Test that return names are correctly defined."""
    names = PromptWithLoraNode.get_return_names()

    assert names == ("model", "clip", "conditioning", "prompt_text")


def test_prompt_with_lora_category() -> None:
    """Test that node is in correct category."""
    assert PromptWithLoraNode.CATEGORY == "weirdion/prompting"


def test_prompt_with_lora_text_only_mode() -> None:
    """Test processing prompt without MODEL/CLIP (text-only mode)."""
    node = PromptWithLoraNode()
    prompt = "a girl, blonde hair"

    model, clip, conditioning, text = node.process(
        prompt=prompt,
        insert_lora="CHOOSE",
        insert_embedding="CHOOSE",
    )

    assert model is None
    assert clip is None
    assert conditioning is None
    assert text == prompt


def test_prompt_with_lora_preserves_tags() -> None:
    """Test that LoRA tags are preserved in text output."""
    node = PromptWithLoraNode()
    prompt = "a girl, <lora:style:0.8>"

    model, clip, conditioning, text = node.process(
        prompt=prompt,
        insert_lora="CHOOSE",
        insert_embedding="CHOOSE",
    )

    assert text == prompt
    assert "<lora:style:0.8>" in text


def test_prompt_with_lora_dropdown_insertion() -> None:
    """Test LoRA insertion from dropdown with default strength 1.0."""
    node = PromptWithLoraNode()
    prompt = "a girl"

    model, clip, conditioning, text = node.process(
        prompt=prompt,
        insert_lora="my-style",
        insert_embedding="CHOOSE",
    )

    assert text == "a girl, <lora:my-style:1.0>"


def test_prompt_with_lora_embedding_insertion() -> None:
    """Test embedding insertion from dropdown."""
    node = PromptWithLoraNode()
    prompt = "a girl"

    model, clip, conditioning, text = node.process(
        prompt=prompt,
        insert_lora="CHOOSE",
        insert_embedding="my-embedding",
    )

    assert text == "a girl, embedding:my-embedding"


def test_prompt_with_lora_lora_and_embedding_insertion() -> None:
    """Test inserting both LoRA and embedding."""
    node = PromptWithLoraNode()
    prompt = "a girl"

    model, clip, conditioning, text = node.process(
        prompt=prompt,
        insert_lora="my-style",
        insert_embedding="my-embedding",
    )

    assert text == "a girl, <lora:my-style:1.0>, embedding:my-embedding"


def test_prompt_with_lora_multiple_tags() -> None:
    """Test handling multiple LoRA tags in prompt."""
    node = PromptWithLoraNode()
    prompt = "<lora:style:0.8>, a girl, <lora:lighting:0.5>"

    model, clip, conditioning, text = node.process(
        prompt=prompt,
        insert_lora="CHOOSE",
        insert_embedding="CHOOSE",
    )

    assert text == prompt
    assert "<lora:style:0.8>" in text
    assert "<lora:lighting:0.5>" in text


def test_prompt_with_lora_high_strength() -> None:
    """Test uncapped LoRA strength (high values)."""
    node = PromptWithLoraNode()
    prompt = "a girl, <lora:style:2.5>"

    model, clip, conditioning, text = node.process(
        prompt=prompt,
        insert_lora="CHOOSE",
        insert_embedding="CHOOSE",
    )

    assert text == prompt
    assert "<lora:style:2.5>" in text


def test_prompt_with_lora_negative_strength() -> None:
    """Test negative LoRA strength (allowed, uncapped)."""
    node = PromptWithLoraNode()
    prompt = "a girl, <lora:style:-0.5>"

    model, clip, conditioning, text = node.process(
        prompt=prompt,
        insert_lora="CHOOSE",
        insert_embedding="CHOOSE",
    )

    assert text == prompt
    assert "<lora:style:-0.5>" in text
