"""Tests for LoadProfileInputParametersNode."""

from weirdion.nodes.loaders import LoadProfileInputParametersNode


def test_load_profile_input_parameters_input_spec() -> None:
    """Test that input spec is correctly defined."""
    spec = LoadProfileInputParametersNode.get_input_spec()

    assert "required" in spec
    required = spec["required"]
    assert "profile" in required
    assert "steps" in required
    assert "cfg" in required
    assert "sampler" in required
    assert "scheduler" in required
    assert "denoise" in required
    assert "clip_skip" in required


def test_load_profile_input_parameters_return_types() -> None:
    """Test that return types are correctly defined."""
    types = LoadProfileInputParametersNode.get_return_types()

    assert len(types) == 8
    assert types[0] == "INT"
    assert types[1] == "FLOAT"
    assert types[3] == "STRING"
    assert types[5] == "STRING"
    assert types[6] == "INT"
    assert types[7] == "FLOAT"


def test_load_profile_input_parameters_return_names() -> None:
    """Test that return names are correctly defined."""
    names = LoadProfileInputParametersNode.get_return_names()

    assert names == (
        "steps",
        "cfg",
        "sampler",
        "sampler_name",
        "scheduler",
        "scheduler_name",
        "clip_skip",
        "denoise",
    )


def test_load_profile_input_parameters_category() -> None:
    """Test that node is in correct category."""
    assert LoadProfileInputParametersNode.CATEGORY == "weirdion/loaders"
