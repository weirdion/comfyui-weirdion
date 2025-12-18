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
    assert "lora_strength" in spec["required"]

    assert "optional" in spec
    assert "model" in spec["optional"]
    assert "clip" in spec["optional"]
    assert "insert_lora" in spec["optional"]


def test_prompt_with_lora_return_types() -> None:
    """Test that return types are correctly defined."""
    types = PromptWithLoraNode.get_return_types()

    assert types == ("MODEL", "CONDITIONING", "CLIP", "STRING")


def test_prompt_with_lora_return_names() -> None:
    """Test that return names are correctly defined."""
    names = PromptWithLoraNode.get_return_names()

    assert names == ("model", "conditioning", "clip", "text")


def test_prompt_with_lora_category() -> None:
    """Test that node is in correct category."""
    assert PromptWithLoraNode.CATEGORY == "weirdion/prompting"


def test_prompt_with_lora_text_only_mode() -> None:
    """Test processing prompt without MODEL/CLIP (text-only mode)."""
    node = PromptWithLoraNode()
    prompt = "a girl, blonde hair"

    model, conditioning, clip, text = node.process(prompt=prompt, lora_strength=1.0)

    assert model is None
    assert conditioning is None
    assert clip is None
    assert text == prompt


def test_prompt_with_lora_preserves_tags() -> None:
    """Test that LoRA tags are preserved in text output."""
    node = PromptWithLoraNode()
    prompt = "a girl, <lora:style:0.8>"

    model, conditioning, clip, text = node.process(prompt=prompt, lora_strength=1.0)

    assert text == prompt
    assert "<lora:style:0.8>" in text


def test_prompt_with_lora_dropdown_insertion() -> None:
    """Test LoRA insertion from dropdown."""
    node = PromptWithLoraNode()
    prompt = "a girl"

    model, conditioning, clip, text = node.process(prompt=prompt, lora_strength=0.8, insert_lora="my-style")

    assert text == "a girl, <lora:my-style:0.8>"


def test_prompt_with_lora_dropdown_skip_choose() -> None:
    """Test that 'CHOOSE' in dropdown is skipped."""
    node = PromptWithLoraNode()
    prompt = "a girl"

    model, conditioning, clip, text = node.process(prompt=prompt, lora_strength=1.0, insert_lora="CHOOSE")

    assert text == prompt  # Should not append anything


def test_prompt_with_lora_empty_prompt_with_insertion() -> None:
    """Test inserting LoRA into empty prompt."""
    node = PromptWithLoraNode()
    prompt = ""

    model, conditioning, clip, text = node.process(prompt=prompt, lora_strength=1.2, insert_lora="style")

    assert text == "<lora:style:1.2>"


def test_prompt_with_lora_multiple_tags() -> None:
    """Test handling multiple LoRA tags in prompt."""
    node = PromptWithLoraNode()
    prompt = "<lora:style:0.8>, a girl, <lora:lighting:0.5>"

    model, conditioning, clip, text = node.process(prompt=prompt, lora_strength=1.0)

    assert text == prompt
    assert "<lora:style:0.8>" in text
    assert "<lora:lighting:0.5>" in text


def test_prompt_with_lora_high_strength() -> None:
    """Test uncapped LoRA strength."""
    node = PromptWithLoraNode()
    prompt = "a girl"

    model, conditioning, clip, text = node.process(prompt=prompt, lora_strength=2.5, insert_lora="style")

    assert text == "a girl, <lora:style:2.5>"


def test_prompt_with_lora_negative_strength() -> None:
    """Test negative LoRA strength (allowed, uncapped)."""
    node = PromptWithLoraNode()
    prompt = "a girl"

    model, conditioning, clip, text = node.process(prompt=prompt, lora_strength=-0.5, insert_lora="style")

    assert text == "a girl, <lora:style:-0.5>"
