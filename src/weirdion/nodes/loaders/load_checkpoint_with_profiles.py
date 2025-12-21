"""
Load Checkpoint with Profiles node.

Loads a checkpoint, applies CLIP skip, and outputs profile-driven parameters.
"""

from typing import Any

from ...core import LoaderNode, register_node
from ...types import ComfyReturnType, InputSpec, NodeOutput
from ...utils.checkpoint_loader import load_checkpoint_with_clip_skip
from ...utils.profile_store import DEFAULT_PROFILE_NAME, load_default_profile, load_user_profiles, resolve_profile


@register_node(
    name="weirdion_LoadCheckpointWithProfiles",
    display_name="Load Checkpoint w/ Profiles (weirdion)",
)
class LoadCheckpointWithProfilesNode(LoaderNode):
    """Load a checkpoint and profile-driven generation parameters."""

    DESCRIPTION = "Load a checkpoint and profile-driven generation parameters in one node."
    CHECKPOINT_PLACEHOLDER = "Select Checkpoint"
    UNSAVED_SUFFIX = " (unsaved)"
    OUTPUT_TOOLTIPS = (
        "U-Net model (denoising latents)",
        "CLIP (text encoder, after clip skip)",
        "VAE (latent/pixel conversion)",
        "Checkpoint name",
        "Clip skip value (string)",
        "Steps",
        "CFG",
        "Sampler (for KSampler)",
        "Sampler name (STRING)",
        "Scheduler (for KSampler)",
        "Scheduler name (STRING)",
        "Clip skip",
        "Denoise",
    )

    @classmethod
    def get_input_spec(cls) -> InputSpec:
        """Define inputs: checkpoint, profile, parameters, and optional overrides."""
        profiles = cls._get_profile_names()
        sampler_types, scheduler_types = cls._get_sampler_scheduler_types()
        default_profile = cls._get_default_profile()

        try:
            import folder_paths

            ckpt_list = folder_paths.get_filename_list("checkpoints")
            ckpt_choices = [cls.CHECKPOINT_PLACEHOLDER] + ckpt_list
        except Exception:
            ckpt_choices = [cls.CHECKPOINT_PLACEHOLDER]

        return {
            "required": {
                "checkpoint": (
                    ckpt_choices,
                    {"default": cls.CHECKPOINT_PLACEHOLDER, "tooltip": "Checkpoint to load"},
                ),
                "profile": (
                    profiles,
                    {"default": DEFAULT_PROFILE_NAME, "tooltip": "Profile to apply"},
                ),
                "steps": (
                    "INT",
                    {
                        "default": int(default_profile["steps"]),
                        "min": 1,
                        "max": 200,
                        "step": 1,
                        "tooltip": "Steps",
                    },
                ),
                "cfg": (
                    "FLOAT",
                    {
                        "default": float(default_profile["cfg"]),
                        "min": 0.0,
                        "max": 30.0,
                        "step": 0.1,
                        "tooltip": "CFG scale",
                    },
                ),
                "sampler": (
                    sampler_types,
                    {"default": default_profile["sampler"], "tooltip": "Sampler"},
                ),
                "scheduler": (
                    scheduler_types,
                    {"default": default_profile["scheduler"], "tooltip": "Scheduler"},
                ),
                "denoise": (
                    "FLOAT",
                    {
                        "default": float(default_profile["denoise"]),
                        "min": 0.0,
                        "max": 1.0,
                        "step": 0.01,
                        "tooltip": "Denoise strength",
                    },
                ),
                "clip_skip": (
                    "INT",
                    {
                        "default": int(default_profile["clip_skip"]),
                        "min": -24,
                        "max": -1,
                        "step": 1,
                        "tooltip": "Clip skip",
                    },
                ),
            },
            "optional": {
                "opt_clip": ("CLIP", {"tooltip": "Optional CLIP override"}),
                "opt_vae": ("VAE", {"tooltip": "Optional VAE override"}),
            },
        }

    @classmethod
    def get_return_types(cls) -> tuple[ComfyReturnType, ...]:
        """Returns checkpoint outputs plus generation parameters."""
        sampler_types, scheduler_types = cls._get_sampler_scheduler_types()
        return (
            "MODEL",
            "CLIP",
            "VAE",
            "STRING",
            "STRING",
            "INT",
            "FLOAT",
            sampler_types,
            "STRING",
            scheduler_types,
            "STRING",
            "INT",
            "FLOAT",
        )

    @classmethod
    def get_return_names(cls) -> tuple[str, ...]:
        """Name the outputs."""
        return (
            "model",
            "clip",
            "vae",
            "model_name",
            "clip_skip_value",
            "steps",
            "cfg",
            "sampler",
            "sampler_name",
            "scheduler",
            "scheduler_name",
            "clip_skip",
            "denoise",
        )

    def process(
        self,
        checkpoint: str,
        profile: str,
        steps: int,
        cfg: float,
        sampler: str,
        scheduler: str,
        denoise: float,
        clip_skip: int,
        opt_clip: Any | None = None,
        opt_vae: Any | None = None,
    ) -> NodeOutput:
        """Load checkpoint and return profile-driven parameters."""
        if not checkpoint or checkpoint == self.CHECKPOINT_PLACEHOLDER:
            raise ValueError("checkpoint is required")

        normalized_profile = self._normalize_profile_name(profile)
        resolve_profile(
            normalized_profile,
            checkpoint_name=checkpoint,
            allow_checkpoint_default=True,
        )

        model, clip, vae, model_name, clip_skip_value = load_checkpoint_with_clip_skip(
            checkpoint,
            int(clip_skip),
            opt_clip=opt_clip,
            opt_vae=opt_vae,
        )

        return (
            model,
            clip,
            vae,
            model_name,
            clip_skip_value,
            int(steps),
            float(cfg),
            sampler,
            sampler,
            scheduler,
            scheduler,
            int(clip_skip),
            float(denoise),
        )

    @staticmethod
    def _get_profile_names() -> list[str]:
        try:
            user_data = load_user_profiles()
            names = list(user_data["profiles"].keys())
        except Exception:
            names = []

        return [DEFAULT_PROFILE_NAME] + sorted(names)

    @staticmethod
    def _get_sampler_scheduler_types() -> tuple[list[str], list[str]]:
        try:
            import comfy.samplers

            return (comfy.samplers.KSampler.SAMPLERS, comfy.samplers.KSampler.SCHEDULERS)
        except Exception:
            return (["euler_ancestral"], ["karras"])

    @staticmethod
    def _get_default_profile() -> dict[str, Any]:
        try:
            return load_default_profile()
        except Exception:
            return {
                "steps": 30,
                "cfg": 5,
                "sampler": "euler_ancestral",
                "scheduler": "karras",
                "denoise": 1.0,
                "clip_skip": -2,
            }

    @classmethod
    def _normalize_profile_name(cls, profile: str) -> str:
        if profile.endswith(cls.UNSAVED_SUFFIX):
            return profile[: -len(cls.UNSAVED_SUFFIX)]
        return profile or DEFAULT_PROFILE_NAME
