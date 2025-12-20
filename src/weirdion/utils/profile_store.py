"""
Profile storage for checkpoint parameter presets.

Stores defaults in .config/profiles.default.json and user edits in
.config/profiles.user.json.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DEFAULT_PROFILE_NAME = "Default"

DEFAULT_PROFILE = {
    "name": DEFAULT_PROFILE_NAME,
    "steps": 30,
    "cfg": 5,
    "sampler": "euler_ancestral",
    "scheduler": "karras",
    "denoise": 1.0,
    "clip_skip": -2,
    "note": "",
}


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _config_dir() -> Path:
    return _repo_root() / ".config"


def _default_profile_path() -> Path:
    return _config_dir() / "profiles.default.json"


def _user_profile_path() -> Path:
    return _config_dir() / "profiles.user.json"


def ensure_default_profile_file() -> None:
    """Ensure the default profile file exists and is valid."""
    config_dir = _config_dir()
    config_dir.mkdir(parents=True, exist_ok=True)

    path = _default_profile_path()
    if not path.exists():
        _write_json(path, {"default_profile": DEFAULT_PROFILE})
        return

    try:
        data = _read_json(path)
        if not isinstance(data, dict) or "default_profile" not in data:
            raise ValueError("Missing default_profile")
        _validate_profile(data["default_profile"], DEFAULT_PROFILE_NAME)
    except Exception:
        _write_json(path, {"default_profile": DEFAULT_PROFILE})


def load_default_profile() -> dict[str, Any]:
    """Load the default profile, recreating it if missing."""
    ensure_default_profile_file()
    data = _read_json(_default_profile_path())
    return data["default_profile"]


def load_user_profiles() -> dict[str, Any]:
    """Load user profiles and checkpoint defaults."""
    path = _user_profile_path()
    if not path.exists():
        return {"profiles": {}, "checkpoint_defaults": {}}

    data = _read_json(path)
    if not isinstance(data, dict):
        raise ValueError("profiles.user.json must be an object")

    profiles = data.get("profiles", {})
    defaults = data.get("checkpoint_defaults", {})

    if not isinstance(profiles, dict):
        raise ValueError("profiles must be an object")
    if not isinstance(defaults, dict):
        raise ValueError("checkpoint_defaults must be an object")

    for name, profile in profiles.items():
        if name == DEFAULT_PROFILE_NAME:
            raise ValueError("profiles may not include 'Default'")
        _validate_profile(profile, name)

    for checkpoint, profile_name in defaults.items():
        if profile_name not in profiles:
            raise ValueError(f"checkpoint default '{checkpoint}' points to missing profile '{profile_name}'")

    return {"profiles": profiles, "checkpoint_defaults": defaults}


def save_user_profiles(data: dict[str, Any]) -> None:
    """Save user profiles to disk."""
    profiles = data.get("profiles", {})
    defaults = data.get("checkpoint_defaults", {})

    if not isinstance(profiles, dict):
        raise ValueError("profiles must be an object")
    if not isinstance(defaults, dict):
        raise ValueError("checkpoint_defaults must be an object")

    for name, profile in profiles.items():
        if name == DEFAULT_PROFILE_NAME:
            raise ValueError("profiles may not include 'Default'")
        _validate_profile(profile, name)

    for checkpoint, profile_name in defaults.items():
        if profile_name not in profiles:
            raise ValueError(f"checkpoint default '{checkpoint}' points to missing profile '{profile_name}'")

    _config_dir().mkdir(parents=True, exist_ok=True)
    _write_json(_user_profile_path(), {"profiles": profiles, "checkpoint_defaults": defaults})


def _validate_profile(profile: dict[str, Any], name: str) -> None:
    if not isinstance(profile, dict):
        raise ValueError(f"profile '{name}' must be an object")

    required = {
        "steps": int,
        "cfg": (int, float),
        "sampler": str,
        "scheduler": str,
        "denoise": (int, float),
        "clip_skip": int,
        "note": str,
    }

    for key, expected_type in required.items():
        if key not in profile:
            raise ValueError(f"profile '{name}' missing '{key}'")
        if not isinstance(profile[key], expected_type):
            raise ValueError(f"profile '{name}' field '{key}' has invalid type")

    checkpoints = profile.get("checkpoints", [])
    if not isinstance(checkpoints, list) or not all(isinstance(c, str) for c in checkpoints):
        raise ValueError(f"profile '{name}' field 'checkpoints' must be a list of strings")


def _read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("profile data must be a JSON object")
    return data


def _write_json(path: Path, data: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2)
