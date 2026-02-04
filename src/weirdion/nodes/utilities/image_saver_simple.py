"""Simple image saver node with creator metadata support."""

from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, PngImagePlugin

from ...core.base import UtilityNode
from ...core.registry import register_node
from ...types import ComfyType, InputSpec, NodeOutput


@register_node(name="weirdion_ImageSaverSimple", display_name="Image Saver Simple (weirdion)")
class ImageSaverSimpleNode(UtilityNode):
    """Save images to disk with basic format controls and creator metadata."""

    OUTPUT_NODE = True
    FUNCTION = "save"
    CATEGORY = "weirdion/output"
    DESCRIPTION = "Save images with simple filename/path controls and optional creator metadata."
    OUTPUT_TOOLTIPS = ("Comma-separated saved filenames",)

    @classmethod
    def get_input_spec(cls) -> InputSpec:
        """Define saver inputs."""
        return {
            "required": {
                "images": ("IMAGE", {"tooltip": "Images batch to save"}),
                "creator_name": (
                    "STRING",
                    {"default": "", "multiline": False, "tooltip": "Optional creator name stored in metadata"},
                ),
                "filename": (
                    "STRING",
                    {"default": "%time_%seed", "multiline": False, "tooltip": "Base filename without extension"},
                ),
                "path": (
                    "STRING",
                    {"default": "", "multiline": False, "tooltip": "Optional output subfolder under ComfyUI output"},
                ),
                "extension": (
                    ["png", "jpeg", "jpg", "webp"],
                    {"tooltip": "Output image format"},
                ),
                "lossless_webp": ("BOOLEAN", {"default": True, "tooltip": "Use lossless mode for WEBP output"}),
                "quality": ("INT", {"default": 100, "min": 1, "max": 100, "tooltip": "JPEG/WEBP quality"}),
            }
        }

    @classmethod
    def get_return_types(cls) -> tuple[ComfyType, ...]:
        """Return output types."""
        return ("STRING",)

    @classmethod
    def get_return_names(cls) -> tuple[str, ...]:
        """Return output names."""
        return ("filenames",)

    def save(
        self,
        images: Any,
        creator_name: str,
        filename: str,
        path: str,
        extension: str,
        lossless_webp: bool,
        quality: int,
    ) -> dict[str, Any]:
        """Save images and return ComfyUI UI/result payload."""
        try:
            import folder_paths
        except Exception as e:  # pragma: no cover - ComfyUI runtime only
            raise RuntimeError("ComfyUI runtime dependencies not available") from e

        base_output = Path(folder_paths.output_directory)
        clean_path = self._normalize_subfolder(path, base_output)
        output_dir = base_output / clean_path if clean_path else base_output
        output_dir.mkdir(parents=True, exist_ok=True)

        saved_files: list[str] = []
        ui_images: list[dict[str, str]] = []

        np_batch = images.detach().cpu().numpy()
        for idx in range(np_batch.shape[0]):
            frame = np.clip(np_batch[idx], 0, 1)
            frame_u8 = (frame * 255).astype(np.uint8)
            image = Image.fromarray(frame_u8)

            target_name = self._next_filename(output_dir, filename.strip() or "image", extension, idx)
            target_path = output_dir / target_name
            self._save_image(
                image=image,
                path=target_path,
                extension=extension,
                creator_name=(creator_name or "").strip(),
                quality=quality,
                lossless_webp=lossless_webp,
            )

            saved_files.append(target_name)
            ui_images.append(
                {
                    "filename": target_name,
                    "subfolder": clean_path.replace("\\", "/"),
                    "type": "output",
                }
            )

        return {
            "ui": {"images": ui_images},
            "result": (",".join(saved_files),),
        }

    @staticmethod
    def _normalize_subfolder(path: str, base_output: Path) -> str:
        """Convert user path input into a safe subfolder under ComfyUI output."""
        raw = (path or "").strip()
        if not raw:
            return ""

        # If caller passed an absolute path inside output/, keep only the relative tail.
        raw_path = Path(raw)
        if raw_path.is_absolute():
            try:
                return raw_path.relative_to(base_output).as_posix().strip("/\\")
            except ValueError:
                # Absolute path outside output/: keep only final folder name to avoid nested /Users/... trees.
                return raw_path.name.strip("/\\")

        return raw.strip("/\\")

    def process(
        self,
        images: Any,
        creator_name: str,
        filename: str,
        path: str,
        extension: str,
        lossless_webp: bool,
        quality: int,
    ) -> NodeOutput:
        """BaseNode compatibility: delegate to save()."""
        out = self.save(
            images=images,
            creator_name=creator_name,
            filename=filename,
            path=path,
            extension=extension,
            lossless_webp=lossless_webp,
            quality=quality,
        )
        return out["result"]

    @staticmethod
    def _next_filename(output_dir: Path, filename: str, extension: str, batch_index: int) -> str:
        base = filename
        if batch_index > 0:
            base = f"{base}_{batch_index + 1:02d}"
        candidate = f"{base}.{extension}"
        counter = 1
        while (output_dir / candidate).exists():
            candidate = f"{base}_{counter:04d}.{extension}"
            counter += 1
        return candidate

    @staticmethod
    def _save_image(
        image: Image.Image,
        path: Path,
        extension: str,
        creator_name: str,
        quality: int,
        lossless_webp: bool,
    ) -> None:
        ext = extension.lower()
        if ext == "png":
            pnginfo = PngImagePlugin.PngInfo()
            if creator_name:
                pnginfo.add_text("Creator", creator_name)
            image.save(path, pnginfo=pnginfo, optimize=True)
            return

        if ext in {"jpeg", "jpg"}:
            image.convert("RGB").save(path, quality=int(quality), optimize=True)
            return

        if ext == "webp":
            image.save(path, quality=int(quality), lossless=bool(lossless_webp), method=6)
            return

        image.save(path)
