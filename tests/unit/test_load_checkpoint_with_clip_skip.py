"""Tests for LoadCheckpointWithClipSkipNode."""

from weirdion.nodes.loaders import LoadCheckpointWithClipSkipNode


def test_load_checkpoint_with_clip_skip_input_spec() -> None:
    """Test that input spec is correctly defined."""
    spec = LoadCheckpointWithClipSkipNode.get_input_spec()

    assert "required" in spec
    assert "checkpoint" in spec["required"]
    assert "clip_skip" in spec["required"]

    assert "optional" in spec
    assert "opt_clip" in spec["optional"]
    assert "opt_vae" in spec["optional"]


def test_load_checkpoint_with_clip_skip_return_types() -> None:
    """Test that return types are correctly defined."""
    types = LoadCheckpointWithClipSkipNode.get_return_types()

    assert types == ("MODEL", "CLIP", "VAE", "STRING", "STRING")


def test_load_checkpoint_with_clip_skip_return_names() -> None:
    """Test that return names are correctly defined."""
    names = LoadCheckpointWithClipSkipNode.get_return_names()

    assert names == ("model", "clip", "vae", "model_name", "clip_skip_value")


def test_load_checkpoint_with_clip_skip_category() -> None:
    """Test that node is in correct category."""
    assert LoadCheckpointWithClipSkipNode.CATEGORY == "weirdion/loaders"
