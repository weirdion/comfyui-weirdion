"""
Pytest configuration and fixtures for ComfyUI weirdion tests.
"""

import pytest


@pytest.fixture
def sample_text() -> str:
    """Sample text for testing."""
    return "Hello, World!"


@pytest.fixture
def sample_multiline_text() -> str:
    """Sample multiline text for testing."""
    return """Line 1
Line 2
Line 3"""
