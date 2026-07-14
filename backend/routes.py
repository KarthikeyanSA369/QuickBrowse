"""HTTP API routes exposed to the frontend.

Endpoints
---------
GET  /api/profiles        -> list discovered profiles (empty until granted)
POST /api/launch          -> launch a browser profile
POST /api/open-folder     -> open a profile's folder in the OS file explorer
GET  /api/permission      -> current permission decision
POST /api/permission      -> record the user's permission decision
GET  /api/version         -> app name/version metadata
GET  /api/avatar/<b>/<p>  -> the cached avatar image for a profile, if any
"""
from __future__ import annotations

from flask import Blueprint, abort, jsonify, request, send_file

import config
from services.launcher_service import LauncherService
from services.permission_service import PermissionService
from services.profile_service import profile_service
from utils.logger import get_logger

logger = get_logger(__name__)

api_bp = Blueprint("api", __name__, url_prefix="/api")

launcher_service = LauncherService(profile_service)
permission_service = PermissionService()


def _error_response(message: str, status: int = 400):
    logger.warning("API error (%s): %s", status, message)
    return jsonify({"error": message}), status


@api_bp.get("/version")
def get_version():
    return jsonify({"name": config.APP_NAME, "version": config.APP_VERSION})


@api_bp.get("/permission")
def get_permission():
    state = permission_service.get_state()
    return jsonify(state.to_dict())


@api_bp.post("/permission")
def set_permission():
    payload = request.get_json(silent=True) or {}
    if "granted" not in payload:
        return _error_response("Missing 'granted' field.")
    granted = bool(payload["granted"])
    state = permission_service.set_granted(granted)
    return jsonify(state.to_dict())


@api_bp.get("/profiles")
def get_profiles():
    try:
        state = permission_service.get_state()
        if not state.granted:
            return jsonify({"profiles": [], "permissionGranted": False})

        profiles = profile_service.get_all_profiles()
        return jsonify(
            {
                "profiles": [profile.to_dict() for profile in profiles],
                "permissionGranted": True,
                "installedBrowsers": profile_service.get_installed_browsers(),
            }
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception("Failed to list profiles")
        return _error_response(f"Failed to list profiles: {exc}", 500)


@api_bp.post("/launch")
def launch_profile():
    payload = request.get_json(silent=True) or {}
    profile_id = payload.get("profileId")
    if not profile_id:
        return _error_response("Missing 'profileId' field.")

    result = launcher_service.launch(profile_id)
    if not result.success:
        return _error_response(result.message, 500)
    return jsonify({"success": True, "message": result.message})


@api_bp.post("/open-folder")
def open_folder():
    payload = request.get_json(silent=True) or {}
    profile_id = payload.get("profileId")
    if not profile_id:
        return _error_response("Missing 'profileId' field.")

    result = launcher_service.open_folder(profile_id)
    if not result.success:
        return _error_response(result.message, 500)
    return jsonify({"success": True, "message": result.message})


@api_bp.get("/avatar/<browser_id>/<path:profile_dir>")
def get_avatar(browser_id: str, profile_dir: str):
    service = profile_service.get_service(browser_id)
    if not service:
        abort(404)

    avatar_file = service.get_avatar_path(profile_dir)
    if not avatar_file:
        abort(404)

    return send_file(avatar_file)


@api_bp.errorhandler(404)
def handle_not_found(_exc):
    return jsonify({"error": "Not found"}), 404


@api_bp.errorhandler(500)
def handle_server_error(_exc):
    return jsonify({"error": "Internal server error"}), 500
