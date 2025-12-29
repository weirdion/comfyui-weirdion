"""
Load Profile Input Parameters node.

Loads generation parameters from a named profile, keyed by checkpoint.
"""

from typing import Any

from ...core import LoaderNode, register_node
from ...types import ComfyReturnType, InputSpec, NodeOutput
from ...utils.profile_store import DEFAULT_PROFILE_NAME, load_default_profile, load_user_profiles, resolve_profile


@register_node(
    name="weirdion_LoadProfileInputParameters",
    display_name="Load Profile Input Parameters (weirdion)",
)
class LoadProfileInputParametersNode(LoaderNode):
    """Load generation parameters from a saved profile."""

    DESCRIPTION = "Load generation parameters from a profile."
    UNSAVED_SUFFIX = " (unsaved)"
    OUTPUT_TOOLTIPS = (
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
        """Define inputs: checkpoint name and profile selection."""
        profiles = cls._get_profile_names()
        sampler_types, scheduler_types = cls._get_sampler_scheduler_types()
        default_profile = cls._get_default_profile()

        return {
            "required": {
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
        }

    @classmethod
    def get_return_types(cls) -> tuple[ComfyReturnType, ...]:
        """Returns generation parameters."""
        sampler_types, scheduler_types = cls._get_sampler_scheduler_types()
        return (
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
        profile: str,
        steps: int,
        cfg: float,
        sampler: str,
        scheduler: str,
        denoise: float,
        clip_skip: int,
    ) -> NodeOutput:
        """Resolve and return parameters for the selected profile."""
        normalized_profile = self._normalize_profile_name(profile)
        resolve_profile(normalized_profile, allow_checkpoint_default=False)

        return (
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
