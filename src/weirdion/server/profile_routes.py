"""Profile manager API routes."""

from ..utils.profile_store import (
    load_default_profile,
    load_user_profiles,
    save_user_profiles,
)


def register_profile_routes() -> None:
    """Register profile manager routes with the ComfyUI server."""
    try:
        from aiohttp import web
        from server import PromptServer
    except ModuleNotFoundError:
        return

    if not hasattr(PromptServer, "instance"):
        return

    routes = PromptServer.instance.routes

    @routes.get("/weirdion/profiles")
    async def get_profiles(request) -> web.Response:
        try:
            default_profile = load_default_profile()
            user_data = load_user_profiles()
            checkpoints = _get_checkpoints()
            payload = {
                "default_profile": default_profile,
                "profiles": user_data["profiles"],
                "checkpoint_defaults": user_data["checkpoint_defaults"],
                "checkpoints": checkpoints,
            }
            return web.json_response(payload)
        except Exception as exc:
            return web.json_response({"error": str(exc)}, status=400)

    @routes.post("/weirdion/profiles")
    async def save_profiles(request) -> web.Response:
        try:
            data = await request.json()
            if not isinstance(data, dict):
                raise ValueError("payload must be a JSON object")

            save_user_profiles(
                {
                    "profiles": data.get("profiles", {}),
                    "checkpoint_defaults": data.get("checkpoint_defaults", {}),
                }
            )
            return web.json_response({"status": "ok"})
        except Exception as exc:
            return web.json_response({"error": str(exc)}, status=400)


def _get_checkpoints() -> list[str]:
    try:
        import folder_paths

        return folder_paths.get_filename_list("checkpoints")
    except Exception:
        return []
