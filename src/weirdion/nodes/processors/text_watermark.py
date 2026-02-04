"""Text watermark node."""

from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import torch

from ...core.base import ProcessingNode
from ...core.registry import register_node
from ...types import InputSpec, NodeOutput


def _parse_color(value: str, alpha: float) -> tuple[int, int, int, int]:
    raw = (value or "").strip()
    if raw.startswith("#"):
        hex_color = raw.lstrip("#")
        if len(hex_color) == 3:
            hex_color = "".join(ch * 2 for ch in hex_color)
        if len(hex_color) == 6:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            return (r, g, b, int(alpha * 255))
    if "," in raw:
        parts = [p.strip() for p in raw.split(",") if p.strip()]
        if len(parts) >= 3:
            r, g, b = (int(p) for p in parts[:3])
            return (r, g, b, int(alpha * 255))
    return (255, 255, 255, int(alpha * 255))


def _load_font(font_name: str, font_size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    if not font_name:
        return ImageFont.load_default()
    try:
        return ImageFont.truetype(font_name, font_size)
    except OSError:
        return ImageFont.load_default()


def _text_bbox(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> tuple[int, int]:
    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        return (bbox[2] - bbox[0], bbox[3] - bbox[1])
    except Exception:
        return draw.textsize(text, font=font)


@register_node(name="WDN_TextWatermark", display_name="Text Watermark")
class TextWatermarkNode(ProcessingNode):
    """Overlay a single-line watermark on an image."""

    @classmethod
    def get_input_spec(cls) -> InputSpec:
        return {
            "required": {
                "image": ("IMAGE",),
                "text": ("STRING", {"default": ""}),
                "position": (
                    [
                        "bottom_right",
                        "bottom_left",
                        "top_right",
                        "top_left",
                    ],
                ),
                "font_name": ("STRING", {"default": "DejaVuSans.ttf"}),
                "font_size": ("INT", {"default": 32, "min": 4, "max": 512}),
                "color": ("STRING", {"default": "#FFFFFF"}),
                "alpha": ("FLOAT", {"default": 0.6, "min": 0.0, "max": 1.0, "step": 0.01}),
                "padding": ("INT", {"default": 16, "min": 0, "max": 200}),
                "stroke_size": ("INT", {"default": 0, "min": 0, "max": 20}),
                "stroke_color": ("STRING", {"default": "#000000"}),
            }
        }

    @classmethod
    def get_return_types(cls) -> tuple[str, ...]:
        return ("IMAGE",)

    def process(
        self,
        image: Any,
        text: str,
        position: str,
        font_name: str,
        font_size: int,
        color: str,
        alpha: float,
        padding: int,
        stroke_size: int,
        stroke_color: str,
    ) -> NodeOutput:
        if not text or not text.strip():
            return (image,)

        batch = image
        device = batch.device
        np_batch = batch.detach().cpu().numpy()
        outputs = []

        for idx in range(np_batch.shape[0]):
            frame = np_batch[idx]
            frame = np.clip(frame, 0, 1)
            frame = (frame * 255).astype(np.uint8)
            base = Image.fromarray(frame)
            base_rgba = base.convert("RGBA")

            overlay = Image.new("RGBA", base_rgba.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)
            font = _load_font(font_name, int(font_size))
            text_w, text_h = _text_bbox(draw, text, font)

            width, height = base_rgba.size
            x = padding
            y = padding
            if position == "top_right":
                x = width - text_w - padding
                y = padding
            elif position == "bottom_left":
                x = padding
                y = height - text_h - padding
            elif position == "bottom_right":
                x = width - text_w - padding
                y = height - text_h - padding

            x = max(0, x)
            y = max(0, y)

            fill = _parse_color(color, alpha)
            stroke_fill = _parse_color(stroke_color, alpha)
            draw.text(
                (x, y),
                text,
                font=font,
                fill=fill,
                stroke_width=int(stroke_size),
                stroke_fill=stroke_fill,
            )

            combined = Image.alpha_composite(base_rgba, overlay).convert("RGB")
            out = np.asarray(combined).astype(np.float32) / 255.0
            outputs.append(out)

        out_batch = torch.from_numpy(np.stack(outputs, axis=0)).to(device)
        return (out_batch,)
