"""
Load Profile Input Parameters node.

Loads generation parameters from a named profile, keyed by checkpoint.
"""

from typing import Any

from ...core import LoaderNode, register_node
from ...types import ComfyReturnType, InputSpec, NodeOutput
from ...utils.profile_store import DEFAULT_PROFILE_NAME, load_default_profile, load_user_profiles


@register_node(
    name="weirdion_LoadProfileInputParameters",
    display_name="Load Profile Input Parameters (weirdion)",
)
class LoadProfileInputParametersNode(LoaderNode):
    """Load generation parameters from a saved profile."""

    DESCRIPTION = "Load generation parameters from a profile based on checkpoint name."
    OUTPUT_TOOLTIPS = (
        "Checkpoint name",
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

        return {
            "required": {
                "checkpoint_name": ("STRING", {"default": "", "tooltip": "Checkpoint name to match profiles"}),
                "profile": (
                    profiles,
                    {"default": DEFAULT_PROFILE_NAME, "tooltip": "Profile to apply"},
                ),
            },
        }

    @classmethod
    def get_return_types(cls) -> tuple[ComfyReturnType, ...]:
        """Returns checkpoint name and generation parameters."""
        sampler_types, scheduler_types = cls._get_sampler_scheduler_types()
        return (
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
            "checkpoint_name",
            "steps",
            "cfg",
            "sampler",
            "sampler_name",
            "scheduler",
            "scheduler_name",
            "clip_skip",
            "denoise",
        )

    def process(self, checkpoint_name: str, profile: str) -> NodeOutput:
        """Resolve and return parameters for the selected profile."""
        if not checkpoint_name:
            raise ValueError("checkpoint_name is required")

        default_profile = load_default_profile()
        user_data = load_user_profiles()
        profiles: dict[str, Any] = user_data["profiles"]
        checkpoint_defaults: dict[str, str] = user_data["checkpoint_defaults"]

        resolved_name = profile
        if profile == DEFAULT_PROFILE_NAME:
            resolved_name = checkpoint_defaults.get(checkpoint_name, DEFAULT_PROFILE_NAME)

        if resolved_name == DEFAULT_PROFILE_NAME:
            profile_data = default_profile
        else:
            if resolved_name not in profiles:
                raise ValueError(f"Profile not found: '{resolved_name}'")
            profile_data = profiles[resolved_name]

        steps = int(profile_data["steps"])
        cfg = float(profile_data["cfg"])
        sampler = profile_data["sampler"]
        scheduler = profile_data["scheduler"]
        clip_skip = int(profile_data["clip_skip"])
        denoise = float(profile_data["denoise"])

        return (
            checkpoint_name,
            steps,
            cfg,
            sampler,
            sampler,
            scheduler,
            scheduler,
            clip_skip,
            denoise,
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
