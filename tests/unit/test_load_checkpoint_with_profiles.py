"""Tests for LoadCheckpointWithProfilesNode."""

from weirdion.nodes.loaders import LoadCheckpointWithProfilesNode


def test_load_checkpoint_with_profiles_input_spec() -> None:
    """Test that input spec is correctly defined."""
    spec = LoadCheckpointWithProfilesNode.get_input_spec()

    assert "required" in spec
    required = spec["required"]
    assert "checkpoint" in required
    assert "profile" in required
    assert "steps" in required
    assert "cfg" in required
    assert "sampler" in required
    assert "scheduler" in required
    assert "denoise" in required
    assert "clip_skip" in required

    assert "optional" in spec
    optional = spec["optional"]
    assert "opt_clip" in optional
    assert "opt_vae" in optional


def test_load_checkpoint_with_profiles_return_types() -> None:
    """Test that return types are correctly defined."""
    types = LoadCheckpointWithProfilesNode.get_return_types()

    assert len(types) == 12
    assert types[0] == "MODEL"
    assert types[1] == "CLIP"
    assert types[2] == "VAE"
    assert types[3] == "STRING"
    assert types[4] == "INT"
    assert types[5] == "FLOAT"
    assert types[7] == "STRING"
    assert types[9] == "STRING"
    assert types[10] == "INT"
    assert types[11] == "FLOAT"


def test_load_checkpoint_with_profiles_return_names() -> None:
    """Test that return names are correctly defined."""
    names = LoadCheckpointWithProfilesNode.get_return_names()

    assert names == (
        "model",
        "clip",
        "vae",
        "model_name",
        "steps",
        "cfg",
        "sampler",
        "sampler_name",
        "scheduler",
        "scheduler_name",
        "clip_skip",
        "denoise",
    )


def test_load_checkpoint_with_profiles_category() -> None:
    """Test that node is in correct category."""
    assert LoadCheckpointWithProfilesNode.CATEGORY == "weirdion/loaders"
