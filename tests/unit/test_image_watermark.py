"""Tests for ImageWatermarkNode."""

import torch

from weirdion.nodes.processors import ImageWatermarkNode


def test_image_watermark_input_spec() -> None:
    """Input spec includes required and optional fields."""
    spec = ImageWatermarkNode.get_input_spec()

    assert "required" in spec
    assert "image" in spec["required"]
    assert "watermark_image" in spec["required"]
    assert "position" in spec["required"]
    assert "scale_percent" in spec["required"]
    assert "angle_degrees" in spec["required"]
    assert "alpha" in spec["required"]
    assert "padding" in spec["required"]

    assert "optional" in spec
    assert "opt_watermark_mask" in spec["optional"]
    assert "opt_invert_mask" in spec["optional"]


def test_image_watermark_return_types_and_names() -> None:
    """Node return signature is IMAGE/image."""
    assert ImageWatermarkNode.get_return_types() == ("IMAGE",)
    assert ImageWatermarkNode.get_return_names() == ("image",)


def test_image_watermark_overlays_pixels_top_left() -> None:
    """Overlay modifies pixels at selected corner."""
    node = ImageWatermarkNode()
    base = torch.zeros((1, 10, 10, 3), dtype=torch.float32)
    watermark = torch.ones((1, 4, 4, 3), dtype=torch.float32)

    (out,) = node.process(
        image=base,
        watermark_image=watermark,
        position="top_left",
        scale_percent=40.0,  # 10 * 40% => 4px wide
        angle_degrees=0.0,
        alpha=1.0,
        padding=0,
    )

    assert out.shape == base.shape
    # Top-left should be affected by watermark.
    assert float(out[0, 0, 0, 0]) > 0.0
    # Bottom-right should remain black.
    assert float(out[0, 9, 9, 0]) == 0.0


def test_image_watermark_zero_alpha_is_noop() -> None:
    """Alpha 0 returns input unchanged."""
    node = ImageWatermarkNode()
    base = torch.rand((1, 8, 8, 3), dtype=torch.float32)
    watermark = torch.ones((1, 4, 4, 3), dtype=torch.float32)

    (out,) = node.process(
        image=base,
        watermark_image=watermark,
        position="bottom_right",
        scale_percent=25.0,
        angle_degrees=0.0,
        alpha=0.0,
        padding=0,
    )

    assert torch.allclose(out, base)
