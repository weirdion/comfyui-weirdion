"""Tests for ImageSaverSimpleNode."""

from __future__ import annotations

import sys
from types import SimpleNamespace

import numpy as np
from PIL import Image

from weirdion.nodes.utilities import ImageSaverSimpleNode


class _FakeImageBatch:
    """Minimal tensor-like image batch for node tests."""

    def __init__(self, array: np.ndarray) -> None:
        self._array = array

    def detach(self) -> _FakeImageBatch:
        return self

    def cpu(self) -> _FakeImageBatch:
        return self

    def numpy(self) -> np.ndarray:
        return self._array


def test_image_saver_simple_input_spec() -> None:
    """Input spec exposes required fields."""
    spec = ImageSaverSimpleNode.get_input_spec()

    assert "required" in spec
    assert "images" in spec["required"]
    assert "creator_name" in spec["required"]
    assert "filename" in spec["required"]
    assert "path" in spec["required"]
    assert "extension" in spec["required"]
    assert "lossless_webp" in spec["required"]
    assert "quality" in spec["required"]
    assert "optional" in spec
    assert "seed_value" in spec["optional"]


def test_image_saver_simple_return_types_and_names() -> None:
    """Node exposes expected return shape."""
    assert ImageSaverSimpleNode.get_return_types() == ("STRING",)
    assert ImageSaverSimpleNode.get_return_names() == ("filenames",)


def test_image_saver_simple_saves_png_with_creator_metadata(tmp_path, monkeypatch) -> None:
    """Save writes a PNG and embeds creator metadata."""
    monkeypatch.setitem(sys.modules, "folder_paths", SimpleNamespace(output_directory=str(tmp_path)))
    node = ImageSaverSimpleNode()

    # One 2x2 RGB image in [0,1] range.
    batch = _FakeImageBatch(np.ones((1, 2, 2, 3), dtype=np.float32) * 0.5)
    out = node.save(
        images=batch,
        creator_name="ankit",
        filename="sample",
        path="gallery",
        extension="png",
        lossless_webp=True,
        quality=95,
    )

    assert "ui" in out
    assert "result" in out
    assert out["result"][0] == "sample.png"
    assert out["ui"]["images"][0]["subfolder"] == "gallery"

    saved = tmp_path / "gallery" / "sample.png"
    assert saved.exists()

    with Image.open(saved) as image:
        assert image.info.get("Creator") == "ankit"


def test_image_saver_simple_process_delegates_to_save(tmp_path, monkeypatch) -> None:
    """process() returns tuple output for BaseNode compatibility."""
    monkeypatch.setitem(sys.modules, "folder_paths", SimpleNamespace(output_directory=str(tmp_path)))
    node = ImageSaverSimpleNode()
    batch = _FakeImageBatch(np.zeros((1, 1, 1, 3), dtype=np.float32))

    filenames = node.process(
        images=batch,
        creator_name="",
        filename="delegated",
        path="",
        extension="webp",
        lossless_webp=True,
        quality=90,
    )

    assert filenames == ("delegated.webp",)
    assert (tmp_path / "delegated.webp").exists()


def test_image_saver_simple_filename_tokens_expand(tmp_path, monkeypatch) -> None:
    """%time and %seed tokens are resolved before writing."""
    monkeypatch.setitem(sys.modules, "folder_paths", SimpleNamespace(output_directory=str(tmp_path)))
    node = ImageSaverSimpleNode()
    batch = _FakeImageBatch(np.zeros((1, 1, 1, 3), dtype=np.float32))

    out = node.save(
        images=batch,
        creator_name="",
        filename="%time_%seed",
        path="",
        extension="png",
        lossless_webp=True,
        quality=100,
        seed_value=12345,
    )
    saved_name = out["result"][0]
    assert "%time" not in saved_name
    assert "%seed" not in saved_name
    assert "_12345" in saved_name
