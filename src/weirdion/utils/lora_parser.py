"""
LoRA tag parsing utilities.

Handles parsing and extraction of <lora:name:strength> tags from prompt text.
"""

import re
from dataclasses import dataclass


@dataclass
class LoRATag:
    """Represents a parsed LoRA tag."""

    name: str
    strength: float
    original_text: str  # The full <lora:...> tag as it appeared


def parse_lora_tags(text: str) -> list[LoRATag]:
    """
    Parse all <lora:name:strength> tags from text.

    Supports formats:
    - <lora:name:strength>
    - <lora:name> (defaults to 1.0)

    Args:
        text: Input text containing LoRA tags

    Returns:
        List of parsed LoRATag objects

    Example:
        >>> parse_lora_tags("test <lora:style:0.8> prompt")
        [LoRATag(name='style', strength=0.8, original_text='<lora:style:0.8>')]
    """
    # Regex: <lora:NAME> or <lora:NAME:STRENGTH>
    pattern = r"<lora:([^>:]+)(?::([^>]+))?>"
    matches = re.finditer(pattern, text, re.IGNORECASE)

    tags = []
    for match in matches:
        name = match.group(1).strip()
        strength_str = match.group(2)

        # Parse strength, default to 1.0
        try:
            strength = float(strength_str) if strength_str else 1.0
        except ValueError:
            strength = 1.0

        tags.append(LoRATag(name=name, strength=strength, original_text=match.group(0)))

    return tags


def strip_lora_tags(text: str) -> str:
    """
    Remove all <lora:...> tags from text.

    Args:
        text: Input text containing LoRA tags

    Returns:
        Text with all LoRA tags removed

    Example:
        >>> strip_lora_tags("test <lora:style:0.8> prompt")
        'test  prompt'
    """
    pattern = r"<lora:[^>]+>"
    return re.sub(pattern, "", text, flags=re.IGNORECASE)
