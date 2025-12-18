"""Tests for LoRA parsing utilities."""

from weirdion.utils import parse_lora_tags, strip_lora_tags


def test_parse_single_lora() -> None:
    """Test parsing a single LoRA tag."""
    text = "a girl, <lora:style:0.8>, blonde hair"
    tags = parse_lora_tags(text)

    assert len(tags) == 1
    assert tags[0].name == "style"
    assert tags[0].strength == 0.8
    assert tags[0].original_text == "<lora:style:0.8>"


def test_parse_lora_default_strength() -> None:
    """Test parsing LoRA tag without strength (defaults to 1.0)."""
    text = "<lora:style>"
    tags = parse_lora_tags(text)

    assert len(tags) == 1
    assert tags[0].name == "style"
    assert tags[0].strength == 1.0


def test_parse_multiple_loras() -> None:
    """Test parsing multiple LoRA tags."""
    text = "<lora:style:0.8>, <lora:character:1.0>, <lora:lighting:0.5>"
    tags = parse_lora_tags(text)

    assert len(tags) == 3
    assert tags[0].name == "style"
    assert tags[0].strength == 0.8
    assert tags[1].name == "character"
    assert tags[1].strength == 1.0
    assert tags[2].name == "lighting"
    assert tags[2].strength == 0.5


def test_parse_lora_case_insensitive() -> None:
    """Test that parsing is case-insensitive."""
    text = "<LORA:style:0.8>"
    tags = parse_lora_tags(text)

    assert len(tags) == 1
    assert tags[0].name == "style"


def test_parse_lora_with_hyphens() -> None:
    """Test parsing LoRA names with hyphens and underscores."""
    text = "<lora:my-style_v2:0.7>"
    tags = parse_lora_tags(text)

    assert len(tags) == 1
    assert tags[0].name == "my-style_v2"
    assert tags[0].strength == 0.7


def test_parse_lora_invalid_strength() -> None:
    """Test that invalid strength defaults to 1.0."""
    text = "<lora:style:abc>"
    tags = parse_lora_tags(text)

    assert len(tags) == 1
    assert tags[0].strength == 1.0


def test_parse_no_loras() -> None:
    """Test parsing text without LoRA tags."""
    text = "a girl, blonde hair, blue eyes"
    tags = parse_lora_tags(text)

    assert len(tags) == 0


def test_strip_lora_tags_single() -> None:
    """Test stripping a single LoRA tag."""
    text = "a girl, <lora:style:0.8>, blonde hair"
    clean = strip_lora_tags(text)

    assert clean == "a girl, , blonde hair"
    assert "<lora" not in clean


def test_strip_lora_tags_multiple() -> None:
    """Test stripping multiple LoRA tags."""
    text = "<lora:style:0.8>, prompt text, <lora:character:1.0>"
    clean = strip_lora_tags(text)

    assert clean == ", prompt text, "
    assert "<lora" not in clean


def test_strip_lora_tags_none() -> None:
    """Test stripping from text without LoRA tags."""
    text = "a girl, blonde hair"
    clean = strip_lora_tags(text)

    assert clean == text


def test_parse_lora_high_strength() -> None:
    """Test parsing LoRA with strength > 1.0 (uncapped)."""
    text = "<lora:style:2.5>"
    tags = parse_lora_tags(text)

    assert len(tags) == 1
    assert tags[0].strength == 2.5


def test_parse_lora_negative_strength() -> None:
    """Test parsing LoRA with negative strength."""
    text = "<lora:style:-0.5>"
    tags = parse_lora_tags(text)

    assert len(tags) == 1
    assert tags[0].strength == -0.5
