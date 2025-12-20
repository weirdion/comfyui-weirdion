"""Tests for LoadCheckpointNode."""

from weirdion.nodes.loaders import LoadCheckpointNode


def test_load_checkpoint_input_spec() -> None:
    """Test that input spec is correctly defined."""
    spec = LoadCheckpointNode.get_input_spec()

    assert "required" in spec
    assert "checkpoint" in spec["required"]

    assert "optional" in spec
    assert "opt_clip" in spec["optional"]
    assert "opt_vae" in spec["optional"]


def test_load_checkpoint_return_types() -> None:
    """Test that return types are correctly defined."""
    types = LoadCheckpointNode.get_return_types()

    assert types == ("MODEL", "CLIP", "VAE", "STRING")


def test_load_checkpoint_return_names() -> None:
    """Test that return names are correctly defined."""
    names = LoadCheckpointNode.get_return_names()

    assert names == ("model", "clip", "vae", "model_name")


def test_load_checkpoint_category() -> None:
    """Test that node is in correct category."""
    assert LoadCheckpointNode.CATEGORY == "weirdion/loaders"
