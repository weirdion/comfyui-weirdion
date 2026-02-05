"""Image watermark node."""

from typing import Any

import numpy as np
from PIL import Image
import torch

from ...core.base import ProcessingNode
from ...core.registry import register_node
from ...types import ComfyType, InputSpec, NodeOutput


@register_node(name="weirdion_ImageWatermark", display_name="Image Watermark (weirdion)")
class ImageWatermarkNode(ProcessingNode):
    """Overlay an image watermark on top of an image batch."""

    DESCRIPTION = "Overlay a watermark image with configurable position, scale, and alpha."
    OUTPUT_TOOLTIPS = ("Image batch with watermark overlay",)

    @classmethod
    def get_input_spec(cls) -> InputSpec:
        """Define image watermark inputs."""
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "Base image batch"}),
                "watermark_image": ("IMAGE", {"tooltip": "Watermark image batch"}),
                "position": (
                    ["bottom_right", "bottom_left", "top_right", "top_left", "center"],
                    {"tooltip": "Watermark anchor position"},
                ),
                "scale_percent": (
                    "FLOAT",
                    {"default": 20.0, "min": 1.0, "max": 100.0, "step": 0.5, "tooltip": "Watermark width as % of base"},
                ),
                "angle_degrees": (
                    "FLOAT",
                    {"default": 0.0, "min": -180.0, "max": 180.0, "step": 0.5, "tooltip": "Rotate watermark angle"},
                ),
                "alpha": ("FLOAT", {"default": 0.6, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "Opacity"}),
                "padding": ("INT", {"default": 16, "min": 0, "max": 200, "tooltip": "Inset from image edges"}),
            },
            "optional": {
                "opt_watermark_mask": ("MASK", {"tooltip": "Optional alpha mask for watermark image"}),
                "opt_invert_mask": ("BOOLEAN", {"default": False, "tooltip": "Invert watermark mask values"}),
            },
        }

    @classmethod
    def get_return_types(cls) -> tuple[ComfyType, ...]:
        """Return output types."""
        return ("IMAGE",)

    @classmethod
    def get_return_names(cls) -> tuple[str, ...]:
        """Return output names."""
        return ("image",)

    def process(
        self,
        image: Any,
        watermark_image: Any,
        position: str,
        scale_percent: float,
        angle_degrees: float,
        alpha: float,
        padding: int,
        opt_watermark_mask: Any | None = None,
        opt_invert_mask: bool = False,
    ) -> NodeOutput:
        """Apply watermark image to each frame in the batch."""
        if watermark_image is None or float(alpha) <= 0:
            return (image,)

        base_batch = image
        device = base_batch.device
        base_np = base_batch.detach().cpu().numpy()
        wm_np = watermark_image.detach().cpu().numpy()
        if wm_np.shape[0] == 0:
            return (image,)

        mask_np = opt_watermark_mask.detach().cpu().numpy() if opt_watermark_mask is not None else None

        outputs: list[np.ndarray] = []
        for idx in range(base_np.shape[0]):
            frame = np.clip(base_np[idx], 0, 1)
            base_u8 = (frame * 255).astype(np.uint8)
            base_rgba = Image.fromarray(base_u8).convert("RGBA")
            base_w, base_h = base_rgba.size

            wm_idx = min(idx, wm_np.shape[0] - 1)
            wm_frame = np.clip(wm_np[wm_idx], 0, 1)
            wm_u8 = (wm_frame * 255).astype(np.uint8)
            wm_img = Image.fromarray(wm_u8).convert("RGBA")

            target_w = max(1, int(base_w * (float(scale_percent) / 100.0)))
            ratio = target_w / max(1, wm_img.size[0])
            target_h = max(1, int(wm_img.size[1] * ratio))
            wm_img = wm_img.resize((target_w, target_h), Image.Resampling.LANCZOS)

            wm_alpha = wm_img.getchannel("A")
            if mask_np is not None and mask_np.shape[0] > 0:
                mask_idx = min(idx, mask_np.shape[0] - 1)
                mask = np.clip(mask_np[mask_idx], 0, 1)
                if opt_invert_mask:
                    mask = 1.0 - mask
                mask_u8 = (mask * 255).astype(np.uint8)
                mask_img = Image.fromarray(mask_u8).resize((target_w, target_h), Image.Resampling.LANCZOS)
                wm_alpha = Image.fromarray(
                    (np.asarray(mask_img).astype(np.float32) * float(alpha)).clip(0, 255).astype(np.uint8),
                    mode="L",
                )
            else:
                wm_alpha = Image.fromarray(
                    (np.asarray(wm_alpha).astype(np.float32) * float(alpha)).clip(0, 255).astype(np.uint8),
                    mode="L",
                )
            wm_img.putalpha(wm_alpha)
            if float(angle_degrees) != 0.0:
                wm_img = wm_img.rotate(float(angle_degrees), resample=Image.Resampling.BICUBIC, expand=True)

            x, y = self._compute_position(position, base_w, base_h, wm_img.size[0], wm_img.size[1], int(padding))
            overlay = Image.new("RGBA", base_rgba.size, (0, 0, 0, 0))
            overlay.paste(wm_img, (x, y), wm_img)

            merged = Image.alpha_composite(base_rgba, overlay).convert("RGB")
            out = np.asarray(merged).astype(np.float32) / 255.0
            outputs.append(out)

        out_batch = torch.from_numpy(np.stack(outputs, axis=0)).to(device)
        return (out_batch,)

    @staticmethod
    def _compute_position(
        position: str,
        base_w: int,
        base_h: int,
        wm_w: int,
        wm_h: int,
        padding: int,
    ) -> tuple[int, int]:
        x = padding
        y = padding

        if position == "top_right":
            x = base_w - wm_w - padding
            y = padding
        elif position == "bottom_left":
            x = padding
            y = base_h - wm_h - padding
        elif position == "bottom_right":
            x = base_w - wm_w - padding
            y = base_h - wm_h - padding
        elif position == "center":
            x = (base_w - wm_w) // 2
            y = (base_h - wm_h) // 2

        return (max(0, x), max(0, y))
