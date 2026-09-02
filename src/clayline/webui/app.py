"""FastAPI shell for Clayline's immutable local workflow.

The server accepts SVG text only from the local browser, performs the complete
pipeline in a worker thread, and returns views derived from the exact prepared
trace that produced the audited G-code.  It intentionally has no configurable
bind address: paste-printer files and artwork stay on this machine.
"""

import asyncio
import hashlib
import hmac
import json
import math
import re
import tempfile
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from clayline import defaults as _defaults
from clayline.emit import DEFAULT_WET_DENSITY_G_CM3
from clayline.models import PageMode, PassModel, Point, Profile, ZMode

_STATIC = Path(__file__).with_name("static")
_REPO_EXAMPLES = Path(__file__).resolve().parents[3] / "examples"
_DEMO_FIXTURE_DIRS = ("gallery",)
_DEMO_FIXTURE_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]*")
_MAX_FILES = 32
_MAX_SVG_BYTES = 8 * 1024 * 1024
_MAX_TOTAL_BYTES = 24 * 1024 * 1024
_MAX_REQUEST_BYTES = 32 * 1024 * 1024
# The server is localhost-only, so these bounds exist to catch nonsense —
# never to refuse an artist's real file. Scanned meshes routinely run
# hundreds of MB as ASCII OBJ/PLY (Pete's 892k-triangle scans).
_MAX_MESH_BYTES = 1024 * 1024 * 1024
_MAX_GCODE_BYTES = 64 * 1024 * 1024
# A phone photo, not a scan — nowhere near the mesh bound above.
_MAX_IMAGE_BYTES = 64 * 1024 * 1024


def _limit_label(byte_count: int) -> str:
    """Render a byte bound for error copy — the text derives from the
    constant so the message can never drift from the enforced limit."""

    if byte_count % (1024**3) == 0:
        return f"{byte_count // 1024**3} GiB"
    return f"{byte_count // 1024**2} MiB"


_MAX_SOURCE_NAME_BYTES = 120
_MAX_ARTIFACT_STEM_CHARS = 80
_LOCAL_HOST = "127.0.0.1"
_UNSAFE_FILENAME_CHARS = re.compile(r"[^A-Za-z0-9._-]+")
SESSION_COOKIE = "clayline_session"
_MESH_SUFFIXES = {".3mf", ".obj", ".ply", ".stl"}


class UiRequestError(ValueError):
    """Raised when a browser request is invalid or unsafe to execute.

    F9.7: user-facing slice failures carry a structured detail — an artist
    sentence with the numbers and the ways out (``message``), a machine slug
    (``code``), and the raw numbers (``data``).  Programmer errors (malformed
    requests, wrong types) keep a plain-string detail.
    """

    def __init__(
        self,
        message: str,
        *,
        status_code: int = 422,
        code: str | None = None,
        data: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.data = data

    @property
    def detail(self) -> str | dict[str, Any]:
        if self.code is None:
            return str(self)
        return {"message": str(self), "code": self.code, "data": self.data or {}}


def create_app(
    *,
    desktop_token: str | None = None,
    desktop_origin: str | None = None,
) -> Any:
    """Create the optional local FastAPI application.

    FastAPI is imported lazily so importing :mod:`clayline` never requires the
    ``ui`` extra.  Desktop mode authenticates every route with a per-launch
    session cookie and requires an exact same-origin header on mutating calls.
    """

    if (desktop_token is None) != (desktop_origin is None):
        raise ValueError("desktop_token and desktop_origin must be provided together")

    try:
        from fastapi import FastAPI, HTTPException, Request
        from fastapi.middleware.trustedhost import TrustedHostMiddleware
        from fastapi.responses import FileResponse, JSONResponse, Response
        from fastapi.staticfiles import StaticFiles
    except ImportError as exc:  # pragma: no cover - exercised by clean-core smoke test
        raise RuntimeError("Clayline UI requires `pip install clayline[ui]`") from exc

    from clayline.webui.weave_session import WeaveSessionManager

    weave_sessions = WeaveSessionManager()

    def _resolve_weave_session(request: Any) -> tuple[Any, str, bool]:
        # A single-artist desktop app has exactly one session for the life of
        # the process — there is no second client to isolate. Pin every
        # request to the per-launch desktop token (already the unguessable
        # auth secret) so the mesh/slice/result caches survive regardless of
        # whether the WKWebView round-trips the separate weave cookie; an edit
        # can never land in a fresh empty session and see a phantom "expired"
        # error (Pete 2026-07-22: "it's a Mac app, why is it complaining about
        # web shit"). Browsers keep the opaque-minted cookie session.
        if desktop_token is not None:
            return weave_sessions.resolve_fixed(desktop_token)
        return weave_sessions.resolve(request.cookies.get(_weave_session_cookie()))

    @asynccontextmanager
    async def lifespan(_app: Any) -> Any:
        try:
            yield
        finally:
            weave_sessions.clear()

    app = FastAPI(
        title="Clayline — Ceramic Printing Toolpath Studio (local)",
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
        lifespan=lifespan,
    )
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["127.0.0.1", "localhost", "testserver"],
    )
    app.mount("/static", StaticFiles(directory=_STATIC), name="static")

    app.state.weave_sessions = weave_sessions

    def weave_session_http_error(exc: Any) -> Any:
        messages = {
            "slice": (
                "This session sat idle long enough that the sliced form was cleared. "
                "Slice the form again — your pattern is untouched."
            ),
            "mesh": (
                "This session sat idle long enough that the loaded form was cleared. "
                "Load the mesh again — your settings are untouched."
            ),
            "recipe": (
                "This session sat idle long enough that the restored settings were cleared. "
                "Load the saved G-code again."
            ),
            "prepared": (
                "This session sat idle long enough that the pending final-path check was cleared. "
                "Rebuild the final path."
            ),
            "result": (
                "This session sat idle long enough that the finished file was cleared. "
                "Rebuild the final path before downloading."
            ),
            "session": (
                "This studio session sat idle long enough that its working data was cleared. "
                "Continue from the loaded file."
            ),
        }
        kind = getattr(exc, "kind", "session")
        return HTTPException(
            status_code=404,
            detail={
                "message": messages.get(kind, messages["session"]),
                "code": f"weave_{kind}_expired",
                "data": {"kind": kind},
            },
        )

    @app.middleware("http")
    async def local_security_headers(request: Request, call_next: Any) -> Any:
        if desktop_token is not None:
            supplied = request.cookies.get(SESSION_COOKIE, "")
            if not hmac.compare_digest(supplied, desktop_token):
                response = JSONResponse(
                    {"detail": "desktop session authentication required"},
                    status_code=401,
                )
            else:
                response = await call_next(request)
        else:
            response = await call_next(request)
        response.headers["Cache-Control"] = "no-store"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        response.headers["Cross-Origin-Resource-Policy"] = "same-origin"
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=(), payment=(), usb=(), serial=()"
        )
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; img-src 'self' data: blob:; "
            "style-src 'self' 'unsafe-inline'; script-src 'self'; "
            "connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'"
        )
        return response

    @app.get("/", include_in_schema=False)
    async def index() -> Any:
        return FileResponse(_STATIC / "index.html")

    @app.get("/api/health", include_in_schema=False)
    async def health() -> dict[str, str]:
        return {"status": "ok", "scope": "localhost"}

    @app.get("/api/profiles", include_in_schema=False)
    async def profiles() -> dict[str, list[dict[str, Any]]]:
        from clayline.profiles import available_profiles, load_profile

        rows = []
        for name in available_profiles():
            profile = load_profile(name)
            rows.append(
                {
                    "name": profile.name,
                    "label": _profile_label(profile.name),
                    "facts": _profile_facts(profile.name),
                    "verified": profile.verified,
                    "extrusion_mode": profile.extrusion_mode.value,
                    "virtual_filament_diameter": profile.virtual_filament_diameter,
                    "work_bounds": {
                        "min_x": profile.work_bounds.min_x,
                        "max_x": profile.work_bounds.max_x,
                        "min_y": profile.work_bounds.min_y,
                        "max_y": profile.work_bounds.max_y,
                    },
                    "nozzle_diameters": profile.nozzle_diameters,
                    "default_nozzle_diameter": profile.default_nozzle_diameter,
                }
            )
        return {"profiles": rows}

    @app.get("/api/defaults", include_in_schema=False)
    async def defaults_table() -> dict[str, Any]:
        # F10.5: one shared defaults table; the front end must render these
        # instead of shipping its own numbers.
        return {"schema": "clayline.ui.defaults.v1", "defaults": _defaults.ui_defaults()}

    @app.get("/api/weave/textures", include_in_schema=False)
    async def weave_textures() -> dict[str, Any]:
        """Discover fitted pattern-only textures and their exact provenance."""

        from clayline.textures import load_texture_preset, texture_presets
        from clayline.webui.weave_payload import pattern_payload

        rows = []
        for item in texture_presets():
            rows.append(
                {
                    "slug": item.slug,
                    "label": item.label,
                    "description": item.description,
                    "provenance": item.provenance,
                    "reference_file": item.reference_file,
                    "evidence_path": item.evidence_path,
                    "follow_form_integrated": item.slug == "edge-boost",
                    "pattern": pattern_payload(load_texture_preset(item.slug)),
                }
            )
        return {"schema": "clayline.ui.weave-textures.v1", "presets": rows}

    # Localhost-only demo/verification hook (the server never binds anything
    # but 127.0.0.1): GET /api/demo-slice?fixture=<name> runs the NORMAL slice
    # worker path on examples/gallery/<name>.svg from
    # this repository checkout, with the current shared defaults, and returns
    # the identical /api/slice response.  It only reads the fixture SVG text —
    # no files are written.  In a bundled install without the examples tree it
    # answers 404.
    @app.get("/api/demo-slice", include_in_schema=False)
    async def demo_slice(fixture: str) -> Any:
        try:
            content = await asyncio.to_thread(_demo_slice_response_bytes, fixture)
            return Response(content=content, media_type="application/json")
        except UiRequestError as exc:
            raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc
        except (OSError, ValueError) as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @app.post("/api/slice", include_in_schema=False)
    async def slice_job(request: Request) -> Any:
        try:
            payload = await _read_json_request(request, required_origin=desktop_origin)
            if not isinstance(payload, dict):
                raise UiRequestError("request body must be a JSON object")
            content = await asyncio.to_thread(_slice_response_bytes, payload)
            return Response(content=content, media_type="application/json")
        except UiRequestError as exc:
            raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc
        except (OSError, ValueError) as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @app.post("/api/layout-check", include_in_schema=False)
    async def layout_check(request: Request) -> Any:
        # F9.7: live bed-fit check before slicing — ingest + bounding boxes
        # through the identical sizing/layout code the slice path uses; no
        # planning, no emission.
        try:
            payload = await _read_json_request(request, required_origin=desktop_origin)
            if not isinstance(payload, dict):
                raise UiRequestError("request body must be a JSON object")
            content = await asyncio.to_thread(_layout_check_response_bytes, payload)
            return Response(content=content, media_type="application/json")
        except UiRequestError as exc:
            raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc
        except (OSError, ValueError) as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @app.post("/api/convert-image", include_in_schema=False)
    async def convert_image(request: Request) -> Any:
        """Fallback for a reference photo the browser could not decode itself.

        The draw studio's reference lightbox always tries ``createImageBitmap``
        locally first — in the packaged app that decodes HEIC natively.  Only
        when that fails (typically HEIC in a non-Safari engine) does the photo
        come here to be re-encoded as JPEG with Pillow/pillow-heif. It never
        touches a pass or a slice request.
        """

        try:
            body = await _read_image_request(request, required_origin=desktop_origin)
            content = await asyncio.to_thread(_convert_image_to_jpeg, body)
            return Response(content=content, media_type="image/jpeg")
        except UiRequestError as exc:
            raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc
        except (OSError, ValueError) as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @app.post("/api/weave/mesh", include_in_schema=False)
    async def weave_mesh(request: Request) -> Any:
        """Load one bounded raw mesh without embedding megabytes in JSON."""

        from clayline.webui.weave_session import WeaveCacheLimitError, WeaveSessionError

        try:
            body = await _read_mesh_request(request, required_origin=desktop_origin)
            cache, token, created = _resolve_weave_session(request)
            restore_id = request.query_params.get("restore_id")
            restore_profile = None if not restore_id else cache.get("recipe", restore_id).profile
            started = time.perf_counter()
            mesh, payload = await asyncio.to_thread(
                _load_weave_mesh_payload,
                body,
                dict(request.query_params),
                restore_profile,
            )
            loaded = time.perf_counter()
            mesh_id = weave_sessions.put(token, "mesh", mesh)
            payload["mesh_id"] = mesh_id
            payload["timing_ms"] = {
                "engine": _milliseconds(loaded - started),
                "total": _milliseconds(time.perf_counter() - started),
            }
            response = _json_response(Response, payload)
            _set_weave_cookie(response, token, created=created)
            return response
        except UiRequestError as exc:
            raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc
        except WeaveSessionError as exc:
            raise weave_session_http_error(exc) from exc
        except WeaveCacheLimitError as exc:
            raise HTTPException(status_code=413, detail=str(exc)) from exc
        except (OSError, ValueError) as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @app.post("/api/weave/slice", include_in_schema=False)
    async def weave_slice(request: Request) -> Any:
        from clayline.webui.weave_session import WeaveCacheLimitError, WeaveSessionError

        try:
            payload = await _read_json_request(request, required_origin=desktop_origin)
            if not isinstance(payload, dict):
                raise UiRequestError("request body must be a JSON object")
            cache, token, created = _resolve_weave_session(request)
            mesh = cache.get("mesh", _required_id(payload, "mesh_id"))
            restore_id = payload.get("restore_id")
            restore_profile = (
                None
                if restore_id is None
                else cache.get("recipe", _required_id(payload, "restore_id")).profile
            )
            started = time.perf_counter()
            sliced, result = await asyncio.to_thread(
                _slice_weave_mesh_payload, mesh, payload, restore_profile
            )
            sliced_at = time.perf_counter()
            result["slice_id"] = weave_sessions.put(token, "slice", sliced)
            result["timing_ms"] = {
                "engine": _milliseconds(sliced_at - started),
                "total": _milliseconds(time.perf_counter() - started),
            }
            response = _json_response(Response, result)
            _set_weave_cookie(response, token, created=created)
            return response
        except UiRequestError as exc:
            raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc
        except WeaveSessionError as exc:
            raise weave_session_http_error(exc) from exc
        except WeaveCacheLimitError as exc:
            raise HTTPException(status_code=413, detail=str(exc)) from exc
        except (OSError, ValueError) as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @app.post("/api/weave/modulate", include_in_schema=False)
    async def weave_modulate(request: Request) -> Any:
        from clayline.weave_workflow import PreparedWeaveResult
        from clayline.webui.weave_session import WeaveCacheLimitError, WeaveSessionError

        try:
            payload = await _read_json_request(request, required_origin=desktop_origin)
            if not isinstance(payload, dict):
                raise UiRequestError("request body must be a JSON object")
            cache, token, created = _resolve_weave_session(request)
            slice_id = _required_id(payload, "slice_id")
            sliced = (
                cache.get_throttled("slice", slice_id)
                if payload.get("quality", "settle") == "settle"
                else cache.get("slice", slice_id, touch=False)
            )
            restore_id = payload.get("restore_id")
            restore_recipe = (
                None
                if restore_id is None
                else cache.get("recipe", _required_id(payload, "restore_id"))
            )
            result, response_payload = await asyncio.to_thread(
                _modulate_weave_payload,
                sliced,
                payload,
                None if restore_recipe is None else restore_recipe.profile,
                None if restore_recipe is None else restore_recipe.profile_prime_mm,
                None if restore_recipe is None else restore_recipe.profile_end_early_mm,
            )
            if isinstance(result, PreparedWeaveResult):
                prepared_id = weave_sessions.put(token, "prepared", result)
                response_payload["prepared_id"] = prepared_id
            elif result is not None:
                result_id = weave_sessions.put(token, "result", result)
                response_payload["result_id"] = result_id
                response_payload["gcode_url"] = f"/api/weave/result/{result_id}/gcode"
            response = _json_response(Response, response_payload)
            _set_weave_cookie(response, token, created=created)
            return response
        except UiRequestError as exc:
            raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc
        except WeaveSessionError as exc:
            raise weave_session_http_error(exc) from exc
        except WeaveCacheLimitError as exc:
            raise HTTPException(status_code=413, detail=str(exc)) from exc
        except (OSError, ValueError) as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @app.post("/api/weave/finalize", include_in_schema=False)
    async def weave_finalize(request: Request) -> Any:
        """Audit one exact prepared trace without rebuilding its geometry."""

        from clayline.webui.weave_session import WeaveCacheLimitError, WeaveSessionError

        try:
            payload = await _read_json_request(request, required_origin=desktop_origin)
            if not isinstance(payload, dict):
                raise UiRequestError("request body must be a JSON object")
            cache, token, created = _resolve_weave_session(request)
            prepared = cache.get("prepared", _required_id(payload, "prepared_id"))
            result, response_payload = await asyncio.to_thread(
                _finalize_weave_payload, prepared, payload
            )
            result_id = weave_sessions.put(token, "result", result)
            response_payload["result_id"] = result_id
            response_payload["gcode_url"] = f"/api/weave/result/{result_id}/gcode"
            response = _json_response(Response, response_payload)
            _set_weave_cookie(response, token, created=created)
            return response
        except UiRequestError as exc:
            raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc
        except WeaveSessionError as exc:
            raise weave_session_http_error(exc) from exc
        except WeaveCacheLimitError as exc:
            raise HTTPException(status_code=413, detail=str(exc)) from exc
        except (OSError, ValueError) as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @app.post("/api/weave/pattern", include_in_schema=False)
    async def weave_pattern(request: Request) -> Any:
        from clayline.webui.weave_payload import pattern_payload, resolve_pattern
        from clayline.webui.weave_session import WeaveSessionError

        try:
            payload = await _read_json_request(request, required_origin=desktop_origin)
            if not isinstance(payload, dict):
                raise UiRequestError("request body must be a JSON object")
            cache, token, created = _resolve_weave_session(request)
            sliced = None
            if payload.get("slice_id") is not None:
                sliced = cache.get_throttled("slice", _required_id(payload, "slice_id"))
                from clayline.weave_range import select_layer_range

                sliced = select_layer_range(sliced, payload.get("layer_range"))
            response = _json_response(
                Response,
                {
                    "schema": "clayline.ui.weave-pattern.v1",
                    "pattern": pattern_payload(resolve_pattern(payload), sliced),
                },
            )
            _set_weave_cookie(response, token, created=created)
            return response
        except UiRequestError as exc:
            raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc
        except WeaveSessionError as exc:
            raise weave_session_http_error(exc) from exc
        except (OSError, ValueError) as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @app.post("/api/weave/restore", include_in_schema=False)
    async def weave_restore(request: Request) -> Any:
        """Read one bounded G-code header and return its deterministic recipe."""

        from clayline.webui.weave_session import WeaveCacheLimitError, WeaveSessionError

        try:
            body = await _read_gcode_request(request, required_origin=desktop_origin)
            cache, token, created = _resolve_weave_session(request)
            mesh = None
            mesh_id = request.query_params.get("mesh_id")
            if mesh_id:
                mesh = cache.get("mesh", mesh_id)
            from clayline.weave_restore import parse_weave_gcode

            recipe = await asyncio.to_thread(parse_weave_gcode, body)
            payload = await asyncio.to_thread(_restore_weave_gcode_payload, body, mesh, recipe)
            payload["restore_id"] = weave_sessions.put(
                token,
                "recipe",
                recipe,
                size_bytes=_restore_recipe_cache_bytes(body, recipe),
            )
            response = _json_response(Response, payload)
            _set_weave_cookie(response, token, created=created)
            return response
        except UiRequestError as exc:
            raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc
        except WeaveSessionError as exc:
            raise weave_session_http_error(exc) from exc
        except WeaveCacheLimitError as exc:
            raise HTTPException(status_code=413, detail=str(exc)) from exc
        except (OSError, ValueError) as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @app.get("/api/weave/result/{result_id}/gcode", include_in_schema=False)
    async def weave_gcode(result_id: str, request: Request) -> Any:
        from clayline.webui.weave_session import WeaveSessionError

        try:
            cache, token, created = _resolve_weave_session(request)
            result = cache.get("result", result_id)
            filename = _artifact_stem(None, source_name=result.sliced.source_path.name) + ".gcode"
            response = Response(
                content=result.emission.gcode.encode("utf-8"),
                media_type="text/x-gcode; charset=utf-8",
                headers={"Content-Disposition": f'attachment; filename="{filename}"'},
            )
            _set_weave_cookie(response, token, created=created)
            return response
        except WeaveSessionError as exc:
            raise weave_session_http_error(exc) from exc

    @app.delete("/api/weave/session", include_in_schema=False)
    async def clear_weave_session(request: Request) -> Any:
        try:
            _require_local_origin(request, desktop_origin)
            _c, token, _cr = _resolve_weave_session(request)
            if token is not None:
                weave_sessions.clear(token)
            response = Response(status_code=204)
            response.delete_cookie(_weave_session_cookie(), path="/api/weave")
            return response
        except UiRequestError as exc:
            raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc

    return app


def run_ui(*, port: int = 8765, open_browser: bool = True) -> None:
    """Run the UI on the IPv4 loopback interface only."""

    if isinstance(port, bool) or not 1 <= port <= 65_535:
        raise UiRequestError("UI port must be between 1 and 65535")
    try:
        import uvicorn
    except ImportError as exc:  # pragma: no cover - depends on optional environment
        raise RuntimeError("Clayline UI requires `pip install clayline[ui]`") from exc

    if open_browser:
        import threading
        import webbrowser

        url = f"http://{_LOCAL_HOST}:{port}/"
        timer = threading.Timer(0.65, webbrowser.open, args=(url,))
        timer.daemon = True
        timer.start()
    uvicorn.run(create_app(), host=_LOCAL_HOST, port=port, log_level="warning")


def _slice_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Synchronously build one response; the route always calls this in a worker."""

    from clayline.preview import PreviewOptions, build_toolpath_figure, render_plan_svg
    from clayline.stack import LayoutError
    from clayline.workflow import PipelineRequest, _same_planned_path, build_pipeline

    draw_schema_version = _draw_schema_version(payload)
    explicit_passes = draw_schema_version == 2
    files = _validated_files(payload.get("files"), explicit_passes=explicit_passes)
    _require_total_bytes_within_limit(files)
    # Default export name is the first word of every included SVG joined
    # (Pete 2026-07-23), e.g. gothic-quatrefoil + pantile-wave-back ->
    # "gothic-pantile". An explicit typed filename still wins.
    artifact_stem = _artifact_stem(
        payload.get("filename"),
        source_name=_default_export_stem([file_[0] for file_ in files]),
    )
    page_mode = PageMode(_string(payload, "page_mode", _defaults.DEFAULT_PAGE_MODE))
    if explicit_passes and page_mode is not PageMode.STACK:
        raise UiRequestError("draw_schema_version 2 pass rows require page_mode='stack'")
    if explicit_passes and payload.get("scale") is not None:
        raise UiRequestError(
            "draw_schema_version 2 uses per-pass Size; global scale must be null or omitted"
        )
    split_pages = _boolean(payload, "split_pages", False)
    if page_mode is PageMode.STACK and split_pages:
        raise UiRequestError(
            "Stack mode prints all pages as one combined piece, so it cannot export "
            "per-page files. Turn off split-page export or switch Pages to Bed mode.",
            code="stack_split_conflict",
            data={"page_mode": "stack", "split_pages": True},
        )

    with tempfile.TemporaryDirectory(prefix="clayline-ui-") as directory:
        root = Path(directory)
        expanded_sources, nudges, transforms = _write_expanded_sources(files, root)

        # Passing the expanded ordered list preserves per-file copies and lets
        # the workflow ingest each unique path once while retaining page order.
        # Every fallback below comes from the one shared defaults table
        # (clayline.defaults, PRD F10.5); do not restate numbers here.
        page_pause_seconds = _optional_finite(
            payload,
            "page_pause_seconds",
            minimum=0.0,
        )
        if explicit_passes and page_pause_seconds == 0.0:
            page_pause_seconds = None
        raw_protection_model = payload.get("thread_protection_model")
        if raw_protection_model is not None and not isinstance(raw_protection_model, str):
            raise UiRequestError("thread_protection_model must be a string when provided")
        request = PipelineRequest(
            sources=tuple(expanded_sources),
            profile=_string(payload, "profile", "potterbot-xl"),
            # F1.3: an absent or null scale honors the document's declared size.
            scale=(
                1.0
                if explicit_passes
                else (
                    _defaults.resolved_scale(_defaults.DEFAULT_SCALE)
                    if payload.get("scale") is None
                    else _scale(payload["scale"])
                )
            ),
            flatten_tol=_finite(
                payload, "flatten_tol", _defaults.DEFAULT_FLATTEN_TOL_MM, minimum=0.001
            ),
            weld_tol=_finite(payload, "weld_tol", _defaults.DEFAULT_WELD_TOL_MM, minimum=0.0),
            nozzle_diameter=_finite(
                payload, "nozzle", _defaults.DEFAULT_NOZZLE_DIAMETER_MM, minimum=0.01
            ),
            bead_width=(
                _optional_finite(payload, "bead_width", minimum=0.01)
                if explicit_passes
                else _finite(payload, "bead_width", _defaults.DEFAULT_BEAD_WIDTH_MM, minimum=0.01)
            ),
            kiss=_boolean(payload, "kiss", _defaults.DEFAULT_KISS),
            kiss_tol=_optional_finite(payload, "kiss_tol", minimum=0.0),
            layers=_integer(payload, "layers", _defaults.DEFAULT_LAYERS, minimum=1, maximum=10_000),
            layer_height=_finite(
                payload, "layer_height", _defaults.DEFAULT_LAYER_HEIGHT_MM, minimum=0.001
            ),
            first_layer_height=_optional_finite(
                payload,
                "first_layer_height",
                minimum=0.001,
            ),
            alternate=_boolean(payload, "alternate", _defaults.DEFAULT_ALTERNATE),
            helical=_boolean(payload, "helical", False),
            z_mode=ZMode(_string(payload, "z_mode", _defaults.DEFAULT_Z_MODE)),
            standoff_z=_finite(payload, "standoff_z", _defaults.DEFAULT_STANDOFF_Z_MM, minimum=0.0),
            # F5.6: absent/null z-step follows layer_height downstream; 0 stays
            # a supported explicit choice.
            z_step_per_layer=_optional_finite(
                payload,
                "z_step_per_layer",
                minimum=0.0,
            ),
            flow_modulation=_finite(payload, "flow_modulation", 0.0, minimum=0.0),
            z_modulation=_finite(payload, "z_modulation", 0.0, minimum=0.0),
            modulation_wavelength=_finite(
                payload,
                "modulation_wavelength",
                _defaults.DEFAULT_MODULATION_WAVELENGTH_MM,
                minimum=0.001,
            ),
            joint_boost=_finite(payload, "joint_boost", 0.0, minimum=0.0, maximum=2.0),
            thread_protection_model=raw_protection_model,
            settle_valleys=_boolean(payload, "settle_valleys", False),
            flow_multiplier=_finite(
                payload, "flow_multiplier", _defaults.DEFAULT_FLOW_MULTIPLIER, minimum=0.001
            ),
            page_mode=page_mode,
            page_gap=_finite(payload, "page_gap", _defaults.DEFAULT_PAGE_GAP_MM, minimum=0.0),
            page_pause_seconds=page_pause_seconds,
            overlap_fraction=_finite(
                payload,
                "overlap_fraction",
                0.2,
                minimum=0.0,
                maximum=1.0,
            ),
            reproducible=_boolean(payload, "reproducible", False),
            page_nudges=nudges,
            page_transforms=transforms,
            artifact_stem=artifact_stem,
            draw_schema_version=draw_schema_version,
        )
        try:
            result = build_pipeline(request)
        except LayoutError as exc:
            # F9.7: turn the pipeline's bed-overflow refusal into an artist
            # sentence with the numbers, computed by the same layout math.
            raise _layout_overflow_error(expanded_sources, nudges, request) from exc

    options = PreviewOptions(
        width_px=1200,
        height_px=900,
        z_mode=request.z_mode,
    )
    plan_svg = render_plan_svg(
        result.emission.stream,
        result.profile,
        settings=result.emission.settings,
        prepared=result.emission.prepared,
        options=options,
    )
    figure = build_toolpath_figure(
        result.emission.stream,
        result.profile,
        settings=result.emission.settings,
        prepared=result.emission.prepared,
        options=options,
    )
    toolpath = json.loads(figure.to_json())
    report = result.job_report.to_dict()
    splits = []
    if split_pages:
        for split in result.emission.splits:
            split_payload: dict[str, Any] = {
                "filename": split.filename,
                "gcode": split.gcode,
            }
            if split.thread_protection_audit is not None:
                split_payload["thread_protection_audit"] = split.thread_protection_audit.to_dict()
            splits.append(split_payload)
    closed_source_counts = tuple(
        sum(polyline.closed for polyline in design.polylines) for design in result.designs
    )
    planned_stroke_count = sum(len(plan.strokes) for plan in result.plans)
    planned_travel_count = sum(len(plan.travels) for plan in result.plans)
    # F5.3 (amended): the engine spirals every stroke independently, so
    # seamless-spiral only needs every planned stroke, on every page, to be
    # closed — page count and per-page stroke count are no longer limits.
    helical_eligible = (
        planned_stroke_count > 0
        and all(stroke.closed for plan in result.plans for stroke in plan.strokes)
        and (
            not explicit_passes
            or (
                request.page_pause_seconds is None
                and all(
                    _same_planned_path(result.plans[0], candidate)
                    and request.page_nudges[index] == request.page_nudges[0]
                    for index, candidate in enumerate(result.plans[1:], start=1)
                )
            )
        )
    )
    pass_count = (
        len(result.emission.laid_out_job.pages) * result.emission.laid_out_job.settings.layers
        if explicit_passes
        else request.layers
    )
    trace = _trace_payload(result.emission)
    if explicit_passes:
        # A valid seamless spiral may collapse identical authored rows into
        # one internal page with multiple layers. Keep one user-facing source
        # name for every authored pass while retaining the exact move order.
        trace["meta"]["page_names"] = [file_[0] for file_ in files]
    response_warnings = [*report["warnings"], *report.get("diagnostics", [])]
    settle_outcome = report.get("settle_outcome")
    response = {
        "schema": "clayline.ui.slice.v1",
        "gcode": result.emission.gcode,
        "gcode_sha256": hashlib.sha256(result.emission.gcode.encode("utf-8")).hexdigest(),
        "filename": f"{artifact_stem}.gcode",
        "plan_svg": plan_svg,
        "toolpath": {
            "data": toolpath["data"],
            "layout": toolpath["layout"],
            "config": {"displaylogo": False, "responsive": True, "scrollZoom": True},
        },
        "report": report,
        # F9.4: plan-level and motion-level numbers are separate, never
        # conflated, and no computable stat is left null.
        "stats": {
            "plan_strokes": planned_stroke_count,
            "plan_travels": planned_travel_count,
            "passes": pass_count,
            "motion_strokes": result.job_report.totals.stroke_count,
            # For drape jobs (including z-step 0) the report already carries
            # the physical estimate passes x layer_height, never the nominal
            # Z range, so this is always a number.
            "stack_height_mm": report["totals"]["total_stack_height_mm"],
            "stack_height_estimated": request.z_mode is ZMode.DRAPE,
        },
        # F9.5/R2: the scrubber consumes the exact export trace.
        "trace": trace,
        "warnings": response_warnings,
        # F3.5: neutral construction facts (fuse points and laps), never
        # mixed into warnings; plan-mm coordinates for viewport toggles.
        "construction": report["construction"],
        "lint": result.emission.lint_report.format(),
        "splits": splits,
        "capabilities": {
            "planned_stroke_count": planned_stroke_count,
            "closed_source_count": sum(closed_source_counts),
            "kiss_eligible": any(count >= 2 for count in closed_source_counts),
            "helical_eligible": helical_eligible,
        },
    }
    if settle_outcome is not None:
        response["settle_outcome"] = settle_outcome
    if result.emission.thread_protection_audit is not None:
        response["thread_protection_audit"] = result.emission.thread_protection_audit.to_dict()
    return response


async def _read_json_request(request: Any, *, required_origin: str | None = None) -> Any:
    content_type = request.headers.get("content-type", "").partition(";")[0].strip().lower()
    if content_type != "application/json":
        raise UiRequestError(
            "slice requests require Content-Type: application/json",
            status_code=415,
        )
    origin = request.headers.get("origin")
    if required_origin is not None:
        if origin != required_origin:
            raise UiRequestError(
                "desktop slice requests require the exact local Origin",
                status_code=403,
            )
    elif origin is not None:
        parsed = urlsplit(origin)
        expected_host = request.headers.get("host", "")
        if (
            parsed.scheme.lower() != "http"
            or parsed.netloc.lower() != expected_host.lower()
            or parsed.path not in {"", "/"}
            or parsed.query
            or parsed.fragment
        ):
            raise UiRequestError(
                "cross-origin slice requests are not allowed",
                status_code=403,
            )
    content_length = request.headers.get("content-length")
    if content_length is not None:
        try:
            declared_length = int(content_length)
        except ValueError as exc:
            raise UiRequestError("invalid Content-Length header", status_code=400) from exc
        if declared_length < 0:
            raise UiRequestError("invalid Content-Length header", status_code=400)
        if declared_length > _MAX_REQUEST_BYTES:
            raise UiRequestError(
                f"slice request exceeds the {_limit_label(_MAX_REQUEST_BYTES)} request limit",
                status_code=413,
            )

    body = bytearray()
    async for chunk in request.stream():
        if len(chunk) > _MAX_REQUEST_BYTES - len(body):
            raise UiRequestError(
                f"slice request exceeds the {_limit_label(_MAX_REQUEST_BYTES)} request limit",
                status_code=413,
            )
        body.extend(chunk)
    try:
        return await asyncio.to_thread(json.loads, bytes(body))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise UiRequestError("slice request contains invalid JSON") from exc


async def _read_mesh_request(request: Any, *, required_origin: str | None = None) -> bytes:
    """Read a bounded raw mesh upload; multipart and JSON are intentionally absent."""

    content_type = request.headers.get("content-type", "").partition(";")[0].strip().lower()
    if content_type != "application/octet-stream":
        raise UiRequestError(
            "mesh uploads require Content-Type: application/octet-stream",
            status_code=415,
        )
    _require_local_origin(request, required_origin)
    content_length = request.headers.get("content-length")
    if content_length is not None:
        try:
            declared_length = int(content_length)
        except ValueError as exc:
            raise UiRequestError("invalid Content-Length header", status_code=400) from exc
        if declared_length < 0:
            raise UiRequestError("invalid Content-Length header", status_code=400)
        if declared_length > _MAX_MESH_BYTES:
            raise UiRequestError(
                f"mesh upload exceeds the {_limit_label(_MAX_MESH_BYTES)} request limit",
                status_code=413,
            )
    body = bytearray()
    async for chunk in request.stream():
        if len(chunk) > _MAX_MESH_BYTES - len(body):
            raise UiRequestError(
                f"mesh upload exceeds the {_limit_label(_MAX_MESH_BYTES)} request limit",
                status_code=413,
            )
        body.extend(chunk)
    if not body:
        raise UiRequestError("mesh upload is empty")
    return bytes(body)


async def _read_image_request(request: Any, *, required_origin: str | None = None) -> bytes:
    """Read a bounded raw photo upload for the HEIC-conversion fallback."""

    content_type = request.headers.get("content-type", "").partition(";")[0].strip().lower()
    if content_type != "application/octet-stream":
        raise UiRequestError(
            "photo uploads require Content-Type: application/octet-stream",
            status_code=415,
        )
    _require_local_origin(request, required_origin)
    content_length = request.headers.get("content-length")
    if content_length is not None:
        try:
            declared_length = int(content_length)
        except ValueError as exc:
            raise UiRequestError("invalid Content-Length header", status_code=400) from exc
        if declared_length < 0:
            raise UiRequestError("invalid Content-Length header", status_code=400)
        if declared_length > _MAX_IMAGE_BYTES:
            raise UiRequestError(
                f"photo exceeds the {_limit_label(_MAX_IMAGE_BYTES)} request limit",
                status_code=413,
            )
    body = bytearray()
    async for chunk in request.stream():
        if len(chunk) > _MAX_IMAGE_BYTES - len(body):
            raise UiRequestError(
                f"photo exceeds the {_limit_label(_MAX_IMAGE_BYTES)} request limit",
                status_code=413,
            )
        body.extend(chunk)
    if not body:
        raise UiRequestError("photo upload is empty")
    return bytes(body)


def _convert_image_to_jpeg(body: bytes) -> bytes:
    """Decode a photo (Pillow, plus pillow-heif for HEIC/HEIF) and re-encode
    it as JPEG. Synchronous — the route always calls this in a worker thread.
    """

    import io

    try:
        from PIL import Image, ImageOps
    except ImportError as exc:
        raise UiRequestError(
            "This build of Clayline was not packaged with photo support — "
            "resave the photo as PNG, JPEG, or WebP and try again.",
            status_code=501,
            code="reference-photo-support-missing",
        ) from exc
    try:
        import pillow_heif

        pillow_heif.register_heif_opener()
    except ImportError:
        pass  # A HEIC upload will fail the open below with an honest message.
    try:
        with Image.open(io.BytesIO(body)) as image:
            image.load()
            # A phone stores a portrait shot sideways and says so in EXIF; the
            # JPEG handed back carries no tags, so the turn is baked in here.
            upright = ImageOps.exif_transpose(image)
            rgb = upright.convert("RGB")
    except Exception as exc:
        raise UiRequestError(
            "That photo could not be read — Clayline reads PNG, JPEG, WebP, and HEIC.",
            status_code=422,
            code="reference-photo-unreadable",
        ) from exc
    buffer = io.BytesIO()
    rgb.save(buffer, format="JPEG", quality=90)
    return buffer.getvalue()


async def _read_gcode_request(request: Any, *, required_origin: str | None = None) -> bytes:
    """Read a bounded raw G-code artifact for header-only restore."""

    content_type = request.headers.get("content-type", "").partition(";")[0].strip().lower()
    if content_type not in {
        "application/octet-stream",
        "application/gcode",
        "text/plain",
        "text/x-gcode",
    }:
        raise UiRequestError(
            "G-code restore requires a raw text or octet-stream body",
            status_code=415,
        )
    _require_local_origin(request, required_origin)
    content_length = request.headers.get("content-length")
    if content_length is not None:
        try:
            declared_length = int(content_length)
        except ValueError as exc:
            raise UiRequestError("invalid Content-Length header", status_code=400) from exc
        if declared_length < 0:
            raise UiRequestError("invalid Content-Length header", status_code=400)
        if declared_length > _MAX_GCODE_BYTES:
            raise UiRequestError(
                f"G-code exceeds the {_limit_label(_MAX_GCODE_BYTES)} restore limit",
                status_code=413,
            )
    body = bytearray()
    async for chunk in request.stream():
        if len(chunk) > _MAX_GCODE_BYTES - len(body):
            raise UiRequestError(
                f"G-code exceeds the {_limit_label(_MAX_GCODE_BYTES)} restore limit",
                status_code=413,
            )
        body.extend(chunk)
    if not body:
        raise UiRequestError("G-code restore input is empty")
    return bytes(body)


def _require_local_origin(request: Any, required_origin: str | None) -> None:
    origin = request.headers.get("origin")
    if required_origin is not None:
        if origin != required_origin:
            raise UiRequestError("desktop requests require the exact local Origin", status_code=403)
        return
    if origin is None:
        return
    parsed = urlsplit(origin)
    expected_host = request.headers.get("host", "")
    if (
        parsed.scheme.lower() != "http"
        or parsed.netloc.lower() != expected_host.lower()
        or parsed.path not in {"", "/"}
        or parsed.query
        or parsed.fragment
    ):
        raise UiRequestError("cross-origin requests are not allowed", status_code=403)


def _load_weave_mesh_payload(
    body: bytes,
    query: dict[str, str],
    profile_override: Any | None = None,
) -> tuple[Any, dict[str, Any]]:
    from clayline.weave_api import load_mesh
    from clayline.webui.weave_payload import compact_mesh_payload

    filename = _mesh_basename(query.get("filename"))
    up = query.get("up", _defaults.DEFAULT_WEAVE_UP_AXIS)
    profile = (
        query.get("profile", _defaults.DEFAULT_WEAVE_PROFILE)
        if profile_override is None
        else profile_override
    )
    scale = _query_optional_float(query, "scale", _defaults.DEFAULT_WEAVE_SCALE)
    fit_height = _query_optional_float(query, "fit_height", _defaults.DEFAULT_WEAVE_FIT_HEIGHT_MM)
    offset_x = _query_float(query, "offset_x", _defaults.DEFAULT_WEAVE_XY_OFFSET_MM[0])
    offset_y = _query_float(query, "offset_y", _defaults.DEFAULT_WEAVE_XY_OFFSET_MM[1])
    rotation_deg = _query_float(query, "rotation_deg", _defaults.DEFAULT_WEAVE_ROTATION_DEG)
    rotation_x_deg = _query_float(query, "rotation_x_deg", _defaults.DEFAULT_WEAVE_ROTATION_X_DEG)
    rotation_y_deg = _query_float(query, "rotation_y_deg", _defaults.DEFAULT_WEAVE_ROTATION_Y_DEG)
    with tempfile.TemporaryDirectory(prefix="clayline-weave-upload-") as directory:
        path = Path(directory) / filename
        path.write_bytes(body)
        mesh = load_mesh(
            path,
            up=up,
            scale=scale,
            fit_height=fit_height,
            offset=Point(offset_x, offset_y),
            rotation_deg=rotation_deg,
            rotation_x_deg=rotation_x_deg,
            rotation_y_deg=rotation_y_deg,
            profile=profile,
        )
    honesty = mesh.honesty
    return mesh, {
        "schema": "clayline.ui.weave-mesh.v1",
        "filename": filename,
        "source_sha256": mesh.source_sha256,
        "profile_name": mesh.profile_name,
        "bounds_mm": _bounds_payload(mesh.bounds),
        "honesty": {
            "format": honesty.source_format,
            "assumed_units": honesty.assumed_units,
            "vertex_count_before_weld": honesty.vertex_count_before_weld,
            "vertex_count": honesty.vertex_count,
            "duplicate_vertices_welded": honesty.duplicate_vertices_welded,
            "triangle_count": honesty.triangle_count,
            "watertight": honesty.watertight,
            "hole_count": honesty.hole_count,
        },
        "warnings": [_form_warning_payload(warning) for warning in mesh.warnings],
        "preview": compact_mesh_payload(mesh),
    }


def _slice_weave_mesh_payload(
    mesh: Any,
    payload: dict[str, Any],
    profile_override: Any | None = None,
) -> tuple[Any, dict[str, Any]]:
    from clayline.weave_api import sliced_form_stats
    from clayline.weave_emergence import find_island_emergence
    from clayline.weave_models import SeamPolicy
    from clayline.weave_range import (
        layer_range_payload,
        select_layer_range,
        trim_leading_empty_layers,
    )
    from clayline.weave_zblend import zblend_disabled_hint
    from clayline.webui.weave_payload import compact_slice_payload

    # Nozzle-derived defaults (Pete 2026-07-18): null layer_height/bead_width
    # follow the nozzle through the ONE facade derivation so UI and CLI stay
    # byte-identical; the front end normally sends the numbers it displays.
    nozzle = (
        None
        if "nozzle" not in payload or payload["nozzle"] is None
        else _finite(payload, "nozzle", _defaults.DEFAULT_NOZZLE_DIAMETER_MM, minimum=0.01)
    )
    if nozzle is None and profile_override is not None:
        nozzle = profile_override.default_nozzle_diameter
    layer_height = (
        None
        if "layer_height" not in payload or payload["layer_height"] is None
        else _finite(payload, "layer_height", 1.0, minimum=0.001)
    )
    first_layer_height = (
        _defaults.DEFAULT_WEAVE_FIRST_LAYER_HEIGHT_MM
        if "first_layer_height" not in payload or payload["first_layer_height"] is None
        else _finite(payload, "first_layer_height", 1.0, minimum=0.001)
    )
    sample_spacing = (
        _defaults.DEFAULT_WEAVE_SAMPLE_SPACING_MM
        if "sample_spacing" not in payload or payload["sample_spacing"] is None
        else _finite(payload, "sample_spacing", 1.0, minimum=0.001)
    )
    bead_width = (
        None
        if "bead_width" not in payload or payload["bead_width"] is None
        else _finite(payload, "bead_width", 1.0, minimum=0.01)
    )
    sliced = mesh.slice(
        nozzle=nozzle,
        layer_height=layer_height,
        first_layer_height=first_layer_height,
        sample_spacing=sample_spacing,
        bead_width=bead_width,
    )
    requested_range = payload.get("layer_range")
    emergence = find_island_emergence(sliced)
    # Island handling is a studio proposal, never an engine-wide range rule:
    # command-line/API callers keep their full-form default, and an explicit
    # range from the artist always wins.  The full Stage-A slice stays cached
    # either way for later range changes and the Item 8 crown interlock.
    default_island_stop = requested_range is None and emergence is not None
    selected = select_layer_range(
        sliced,
        (1, emergence.layer_index) if default_island_stop else requested_range,
    )
    # Capabilities reflect what modulation will actually print: leading empty
    # layers are auto-trimmed there, so the vase-mode hint must look past them.
    try:
        hint_form = trim_leading_empty_layers(selected)
    except ValueError:
        hint_form = selected
    hint = zblend_disabled_hint(hint_form, SeamPolicy.CHAINED)
    # The first presentation of an automatic island stop deliberately retains
    # full mesh facts/warnings.  An artist needs to see that the form really
    # continues above the proposed print range, not a falsely truncated mesh.
    display = sliced if default_island_stop else selected
    island_emergence = None
    if emergence is not None:
        first = emergence.layer_number
        last = sliced.source_layer_total
        islands = emergence.outer_count
        range_includes_islands = selected.layer_range[1] >= first
        island_emergence = {
            "layer": first,
            "last_layer": last,
            "outer_count": islands,
            "base_outer_count": emergence.base_outer_count,
            "default_stop_to_layer": first - 1,
            "default_applied": default_island_stop,
            "message": (
                f"Layers {first}\N{EN DASH}{last} split into {islands} separate "
                "islands — the printer can't cut the thread between them, so "
                f"printing stops at layer {first - 1}. Raise 'To layer' to override."
            ),
            "override_message": (
                f"Layers {first}\N{EN DASH}{last} split into {islands} separate "
                "islands. This selected range includes them, so the thread will "
                "drag between islands."
                if range_includes_islands and not default_island_stop
                else None
            ),
        }
    return sliced, {
        "schema": "clayline.ui.weave-slice.v1",
        "stats": sliced_form_stats(display),
        "centerline": compact_slice_payload(display),
        "print_range": layer_range_payload(selected),
        "island_emergence": island_emergence,
        "capabilities": {
            "z_blend_eligible": hint is None,
            "z_blend_disabled_hint": hint,
        },
    }


def _crown_finish_payload(
    sliced: Any,
    zblend_path: Any | None,
    *,
    applied: bool | None = None,
    automatic: bool = False,
) -> dict[str, Any] | None:
    """Return server-owned truth for the island/crown range interlock."""

    from clayline.weave_emergence import find_island_emergence

    emergence = find_island_emergence(sliced)
    if emergence is None:
        return None
    if applied is None:
        applied = bool(zblend_path is not None and zblend_path.has_top_follow)
    first = sliced.source_layer_start + emergence.layer_index + 1
    last = sliced.source_layer_start + len(sliced.layers)
    result = {
        "applied": bool(applied),
        "automatic": automatic,
        "from_layer": first,
        "to_layer": last,
        "message": (
            f"Layers {first}\N{EN DASH}{last} shape the continuous wall's Z contour; "
            f"the terminal path follows the form's top without stacked crown passes."
        ),
    }
    if zblend_path is not None and zblend_path.top_follow is not None:
        requested = [point[2] for point in zblend_path.top_follow.requested]
        supported = zblend_path.top_follow.supported_z_offsets
        result["requested_relief_mm"] = round(max(requested) - min(requested), 6)
        result["reached_relief_mm"] = round(max(supported) - min(supported), 6)
        result["support_scale"] = round(zblend_path.top_follow.support_scale, 6)
        result["slope_clamped"] = zblend_path.top_follow.slope_clamped
        result["ghosted_unsupported"] = zblend_path.top_follow.omitted
    return result


def _attach_top_follow_ghost(trace: dict[str, Any], zblend_path: Any | None) -> None:
    """Add requested-but-unsupported contour as display-only trace metadata."""

    plan = None if zblend_path is None else zblend_path.top_follow
    if plan is None or not plan.ghost_segments:
        return
    trace["ghost_top"] = {
        "source": "requested_top_minus_reachable",
        "reason": "support_limit",
        "segments": [
            [[round(value, 6) for value in start], [round(value, 6) for value in end]]
            for start, end in plan.ghost_segments
        ],
    }


def _modulate_weave_payload(
    sliced: Any,
    payload: dict[str, Any],
    profile_override: Any | None = None,
    profile_prime_mm: float | None = None,
    profile_end_early_mm: float | None = None,
) -> tuple[Any | None, dict[str, Any]]:
    from clayline.weave_analysis import largest_pinch_free_amplitude
    from clayline.weave_emergence import find_island_emergence
    from clayline.weave_range import (
        bottom_disabled_hint,
        interior_disabled_hint,
        layer_range_payload,
        select_layer_range,
        trim_leading_empty_layers,
    )
    from clayline.weave_workflow import prepare_weave_result
    from clayline.weave_zblend import build_zblend_path, zblend_disabled_hint
    from clayline.webui.weave_payload import (
        drag_trace_payload,
        pattern_payload,
        resolve_pattern,
        stream_warning_payload,
    )

    quality = payload.get("quality", "settle")
    if quality not in {"drag", "settle"}:
        raise UiRequestError("quality must be 'drag' or 'settle'")
    pattern = resolve_pattern(payload)
    emergence = find_island_emergence(sliced)
    island_range_auto = _boolean(payload, "island_range_auto", False)
    # Top-follow uses the split suffix only as a target field. With it on, Z
    # relief grows through the continuous wall; with it off, the wall stops at
    # the last one-ring layer. The disconnected suffix is never threaded.
    auto_crown = (
        island_range_auto
        and emergence is not None
        and pattern.settings.z_blend
        and pattern.settings.follow_top_edge
        and not pattern.settings.level_rim
    )
    explicit_range = payload.get("layer_range")
    if auto_crown:
        requested_range = None
    elif explicit_range is not None:
        requested_range = explicit_range
    elif island_range_auto and emergence is not None:
        # Z-blend off (or ineligible): stop at the split instead of printing
        # islands with dragged threads between them.
        requested_range = (1, emergence.layer_index)
    else:
        requested_range = None
    selected = select_layer_range(sliced, requested_range)
    try:
        selected = trim_leading_empty_layers(selected)
    except ValueError as error:
        raise UiRequestError(str(error)) from error
    bottom_hint = bottom_disabled_hint(selected)
    if bottom_hint is not None and pattern.settings.bottom_layers:
        raise UiRequestError(f"Bottom cannot be enabled: {bottom_hint}")
    # Both gates are checked here, before the quality branch, so the drag
    # preview refuses in exactly the words and with exactly the status settle
    # will use.  Without this one the artist watched ribs appear on the slider
    # and only learned at settle that the range they chose cannot carry them —
    # ribs on a range that does not start at the form's own first layer would
    # be laid on air.
    interior_hint = interior_disabled_hint(selected)
    if interior_hint is not None and pattern.settings.interior != "hollow":
        raise UiRequestError(f"The interior cannot be filled: {interior_hint}")
    hint = zblend_disabled_hint(selected, pattern.settings.seam)
    if pattern.settings.z_blend and hint is not None:
        # F9.7 + Pete 2026-07-22 (restored-settings deadlock): a persisted
        # Vase mode toggle can refuse a freshly loaded, otherwise-fine form
        # before the only control that clears it (below the fold, hidden
        # until a slice succeeds) ever renders. The refusal itself must
        # carry the one-click way out — house pattern from the pinch
        # warning's inline "apply" action — so the artist is never stuck.
        raise UiRequestError(
            hint,
            code="z_blend_disabled",
            data={
                "recovery_action": {
                    "kind": "disable_z_blend",
                    "label": "Vase mode is on but this form can't use it "
                    "\N{EM DASH} turn off Vase mode and re-slice.",
                }
            },
        )
    started = time.perf_counter()
    if quality == "drag":
        zblend_path = build_zblend_path(selected, pattern) if pattern.settings.z_blend else None
        crown_finish = _crown_finish_payload(
            selected,
            zblend_path,
            automatic=auto_crown,
        )
        trace = drag_trace_payload(
            selected,
            pattern,
            max_points=_integer(
                payload,
                "display_point_budget",
                20_000,
                minimum=500,
                maximum=50_000,
            ),
            zblend_path=zblend_path,
        )
        _attach_top_follow_ghost(trace, zblend_path)
        engine_at = time.perf_counter()
        visuals = pattern_payload(pattern, selected, zblend_path=zblend_path)
        finished = time.perf_counter()
        return None, {
            "schema": "clayline.ui.weave-result.v1",
            "quality": "drag",
            "exportable": False,
            "trace": trace,
            "pattern": visuals,
            "print_range": layer_range_payload(selected),
            "crown_finish": crown_finish,
            "warnings": [],
            "warnings_settled": False,
            "capabilities": {
                "bottom_eligible": bottom_hint is None,
                "bottom_disabled_hint": bottom_hint,
                # The interior rides beside Bottom in the same shape so the
                # Interior control can gray itself out with the reason showing,
                # BEFORE the artist chooses a fill the range cannot carry.
                "interior_eligible": interior_hint is None,
                "interior_disabled_hint": interior_hint,
                "z_blend_eligible": hint is None,
                "z_blend_disabled_hint": hint,
            },
            "timing_ms": {
                "engine_and_decimation": _milliseconds(engine_at - started),
                "pattern_visuals": _milliseconds(finished - engine_at),
                "total": _milliseconds(finished - started),
            },
        }

    flow_value = payload.get(
        "flow_multiplier", payload.get("flow", _defaults.DEFAULT_FLOW_MULTIPLIER)
    )
    if isinstance(flow_value, bool) or not isinstance(flow_value, (int, float)):
        raise UiRequestError("flow_multiplier must be a number")
    flow = float(flow_value)
    if not math.isfinite(flow) or flow <= 0:
        raise UiRequestError("flow_multiplier must be finite and positive")
    prime_mm = _optional_finite(payload, "prime_mm", minimum=0.0)
    end_early_mm = _optional_finite(payload, "end_early_mm", minimum=0.0)
    reproducible = _boolean(payload, "reproducible", False)
    wet_density = (
        DEFAULT_WET_DENSITY_G_CM3
        if payload.get("wet_density_g_cm3") is None
        else _finite(
            payload,
            "wet_density_g_cm3",
            DEFAULT_WET_DENSITY_G_CM3,
            minimum=0.001,
        )
    )
    job_id = payload.get("job_id")
    if job_id is not None and (not isinstance(job_id, str) or not job_id.strip()):
        raise UiRequestError("job_id must be non-blank text when provided")
    prepared_result = prepare_weave_result(
        sliced,
        pattern,
        profile=profile_override,
        profile_prime_mm=profile_prime_mm,
        profile_end_early_mm=profile_end_early_mm,
        flow_multiplier=flow,
        wet_density_g_cm3=wet_density,
        prime_mm=prime_mm,
        end_early_mm=end_early_mm,
        reproducible=reproducible,
        job_id=job_id,
        layer_range=requested_range,
    )
    safe_amplitude = (
        largest_pinch_free_amplitude(
            prepared_result.sliced,
            pattern,
            zblend_path=prepared_result.zblend_path,
        )
        if any(warning.code.value == "pinch" for warning in prepared_result.warnings)
        else None
    )
    engine_at = time.perf_counter()
    trace = _weave_trace_payload(prepared_result)
    artifact_stem = _artifact_stem(payload.get("filename"), source_name=sliced.source_path.name)
    finished = time.perf_counter()
    top_follow_applied = bool(
        prepared_result.zblend_path is not None and prepared_result.zblend_path.has_top_follow
    )
    return prepared_result, {
        "schema": "clayline.ui.weave-result.v1",
        "quality": "settle",
        "geometry_exact": True,
        "finalizing": True,
        "exportable": False,
        "filename": f"{artifact_stem}.gcode",
        "trace": trace,
        "warnings": stream_warning_payload(
            prepared_result.warnings,
            safe_amplitude_mm=safe_amplitude,
        ),
        "warnings_settled": True,
        "lint": "PENDING — exact geometry is visible; export audit is running.",
        "pattern": pattern_payload(
            pattern,
            prepared_result.sliced,
            zblend_path=prepared_result.zblend_path,
        ),
        "print_range": layer_range_payload(prepared_result.sliced),
        "crown_finish": _crown_finish_payload(
            prepared_result.sliced,
            prepared_result.zblend_path,
            applied=top_follow_applied,
            automatic=auto_crown,
        ),
        "capabilities": {
            "bottom_eligible": bottom_hint is None,
            "bottom_disabled_hint": bottom_hint,
            "interior_eligible": interior_hint is None,
            "interior_disabled_hint": interior_hint,
            "z_blend_eligible": hint is None,
            "z_blend_disabled_hint": hint,
        },
        "timing_ms": {
            "exact_geometry": _milliseconds(engine_at - started),
            "serialize_views": _milliseconds(finished - engine_at),
            "total": _milliseconds(finished - started),
        },
    }


def _weave_settings_snapshot(prepared_result: Any, payload: dict[str, Any]) -> dict[str, Any]:
    """Serialize exactly what built ``prepared_result``, in the persisted shape.

    Mirrors ``weaveSettingsSnapshot()`` in weave.js / ``StudioSettingsStore``'s
    ``clayline-ui-state.v1`` (pattern_json + placement + slice + export) so a
    settings snapshot pulled from an error report and one restored from the
    studio's own persistence are the same document an artist (or an agent)
    can replay headlessly without guessing at any field.
    """

    from clayline.wave import pattern_to_json

    sliced = prepared_result.sliced
    settings = prepared_result.settings
    layer_from, layer_to = sliced.layer_range
    return {
        "schema": "clayline.weave-settings.v1",
        "pattern_json": pattern_to_json(prepared_result.pattern),
        "placement": {
            "up_axis": sliced.up_axis.value,
            "scale": sliced.scale,
            "offset_x": sliced.placement_offset.x,
            "offset_y": sliced.placement_offset.y,
            "rotation_deg": sliced.rotation_deg,
            "rotation_x_deg": sliced.rotation_x_deg,
            "rotation_y_deg": sliced.rotation_y_deg,
        },
        "slice": {
            "profile": prepared_result.profile.name,
            "layer_height": sliced.layer_height,
            "first_layer_height": sliced.first_layer_height,
            "sample_spacing": sliced.sample_spacing,
            "bead_width": settings.bead_width,
            "range_from": layer_from,
            "range_to": layer_to,
            "range_total": sliced.source_layer_total,
        },
        "export": {
            "flow_multiplier": settings.flow_multiplier,
            "wet_density_g_cm3": settings.wet_density_g_cm3,
            "reproducible": settings.reproducible,
            "prime_mm": settings.prime_mm,
            "end_early_mm": settings.end_early_mm,
            "filename": payload.get("filename"),
        },
        "source": {
            "filename": sliced.source_path.name,
            "source_sha256": sliced.source_sha256,
        },
    }


def _finalize_weave_payload(
    prepared_result: Any,
    payload: dict[str, Any],
) -> tuple[Any, dict[str, Any]]:
    """Finish artifacts from one exact prepared object, never rebuilt geometry."""

    from clayline.weave_analysis import largest_pinch_free_amplitude
    from clayline.weave_workflow import WeaveWorkflowError, finalize_weave_result
    from clayline.webui.weave_payload import warning_rows_with_safe_offer

    started = time.perf_counter()
    try:
        result = finalize_weave_result(prepared_result)
    except WeaveWorkflowError as exc:
        # 2026-07-22 (reopened): "Weave emission failed lint" reached Pete
        # on a fresh install with restored persisted settings — custom wave
        # points, seam policy, print range, none of which the reproduction
        # attempts that chased it carried. The artist-facing sentence stays
        # exactly what it was; the exact settings that produced it now ride
        # along in data, so the next occurrence is reproducible from the
        # error report alone instead of a fresh multi-hour investigation.
        if str(exc).startswith("Weave emission failed lint"):
            raise UiRequestError(
                str(exc),
                code="emission_lint_failed",
                data={"settings_snapshot": _weave_settings_snapshot(prepared_result, payload)},
            ) from exc
        raise
    finalized_at = time.perf_counter()
    if result.emission.stream is not prepared_result.stream:
        raise UiRequestError("finalized Weave result rebuilt the exact MoveStream")
    if result.emission.prepared is not prepared_result.prepared:
        raise UiRequestError("finalized Weave result rebuilt the exact prepared trace")
    report = result.job_report.to_dict()
    safe_amplitude = (
        largest_pinch_free_amplitude(
            prepared_result.sliced,
            prepared_result.pattern,
            zblend_path=prepared_result.zblend_path,
        )
        if any(warning.code.value == "pinch" for warning in prepared_result.warnings)
        else None
    )
    gcode_bytes = result.emission.gcode.encode("utf-8")
    artifact_stem = _artifact_stem(
        payload.get("filename"),
        source_name=prepared_result.sliced.source_path.name,
    )
    finished = time.perf_counter()
    return result, {
        "schema": "clayline.ui.weave-finalized.v1",
        "quality": "settle",
        "geometry_exact": True,
        "finalizing": False,
        "exportable": True,
        "gcode_sha256": hashlib.sha256(gcode_bytes).hexdigest(),
        # W17 sidecar: motion index -> 1-based line in the exact exported file.
        "gcode_line_map": list(result.emission.motion_line_numbers),
        "gcode_line_count": result.emission.gcode.count("\n"),
        "gcode_bytes": len(gcode_bytes),
        "filename": f"{artifact_stem}.gcode",
        "report": report,
        "warnings": warning_rows_with_safe_offer(
            report["warnings"],
            safe_amplitude_mm=safe_amplitude,
        ),
        "warnings_settled": True,
        "construction": report["construction"],
        "lint": result.emission.lint_report.format(),
        "timing_ms": {
            "artifact_finalize": _milliseconds(finalized_at - started),
            "serialize_views": _milliseconds(finished - finalized_at),
            "total": _milliseconds(finished - started),
        },
    }


def _restore_weave_gcode_payload(
    body: bytes,
    mesh: Any | None,
    recipe: Any | None = None,
) -> dict[str, Any]:
    """Expose one strict saved recipe and current mesh-content match state."""

    from clayline.weave_restore import mesh_restore_warning, parse_weave_gcode
    from clayline.webui.weave_payload import pattern_payload

    recipe = parse_weave_gcode(body) if recipe is None else recipe
    warning = None if mesh is None else mesh_restore_warning(recipe, mesh)
    return {
        "schema": "clayline.ui.weave-restore.v1",
        "needs_mesh": mesh is None,
        "source_mesh": {
            "filename": recipe.source_mesh_name,
            "sha256": recipe.source_mesh_sha256,
            "match": None if mesh is None else warning is None,
            "warning": warning,
        },
        "pattern": pattern_payload(recipe.pattern),
        "layer_range": {
            "from": recipe.layer_range[0],
            "to": recipe.layer_range[1],
            "total": recipe.source_layer_total,
            "semantics": "one_based_inclusive",
            "rebased_to_bed": True,
        },
        "settings": {
            "profile": recipe.profile_name,
            "up": recipe.up_axis.value,
            "scale": recipe.scale,
            "offset": [recipe.offset.x, recipe.offset.y],
            "rotation_deg": recipe.rotation_deg,
            "rotation_x_deg": recipe.rotation_x_deg,
            "rotation_y_deg": recipe.rotation_y_deg,
            "layer_height": recipe.layer_height,
            "first_layer_height": recipe.first_layer_height,
            "sample_spacing": recipe.sample_spacing,
            "bead_width": recipe.bead_width,
            "flow_multiplier": recipe.flow_multiplier,
            "wet_density_g_cm3": recipe.wet_density_g_cm3,
            "prime_mm": recipe.prime_mm,
            "end_early_mm": recipe.end_early_mm,
            "job_id": recipe.job_id,
            "reproducible": recipe.reproducible,
        },
    }


def _restore_recipe_cache_bytes(body: bytes, recipe: Any) -> int:
    """Charge at least the uploaded artifact and the decoded recipe estimate."""

    from clayline.webui.weave_session import estimate_cache_bytes

    return max(len(body), estimate_cache_bytes(recipe))


def _weave_trace_payload(result: Any) -> dict[str, Any]:
    passes = len(result.sliced.layers) + result.pattern.settings.bottom_layers
    prepared = result.emission.prepared if hasattr(result, "emission") else result.prepared
    trace = _prepared_trace_payload(
        prepared,
        passes=passes,
        layer_height=result.sliced.layer_height,
        bead_width=result.sliced.bead_width,
        pass_labels=None,
        page_names=[result.sliced.source_path.name],
        axis_labels={
            "progress": "Layer",
            "horizontal": "Centerline X/Y (mm)",
            "vertical": "Z (mm)",
        },
        layer_labels=_weave_layer_labels(result),
    )
    _attach_top_follow_ghost(trace, result.zblend_path)
    return trace


def _weave_layer_labels(result: Any) -> list[str]:
    """Name scrubber passes from the exact prepared Weave source moves."""

    from clayline.emit import EmissionMotion
    from clayline.models import MoveKind

    bottom_layers = result.pattern.settings.bottom_layers
    wall_layers = len(result.sliced.layers)
    labels = [
        (
            f"bottom {index + 1} of {bottom_layers}"
            if index < bottom_layers
            else f"wall {index - bottom_layers + 1} of {wall_layers}"
        )
        for index in range(bottom_layers + wall_layers)
    ]
    prepared = result.emission.prepared if hasattr(result, "emission") else result.prepared
    for event in prepared.events:
        if not isinstance(event, EmissionMotion) or event.kind is not MoveKind.PRINT:
            continue
        layer = event.layer
        raw_comment = event.source_move.comment
        comment = "" if raw_comment is None else raw_comment.strip()
        if not (0 <= layer < bottom_layers) or not comment.startswith("bottom "):
            continue
        # Multiple islands share one scrubber pass.  Preserve the common
        # physical bottom-layer label while leaving island detail on each move.
        labels[layer] = comment.partition(" · island ")[0]
    return labels


def _mesh_basename(value: Any) -> str:
    if not isinstance(value, str) or not value:
        raise UiRequestError("mesh filename query parameter is required")
    if "\x00" in value or "\r" in value or "\n" in value or Path(value).name != value:
        raise UiRequestError("mesh filename must be a plain basename")
    if len(value.encode("utf-8")) > _MAX_SOURCE_NAME_BYTES:
        raise UiRequestError("mesh filename is too long")
    if Path(value).suffix.lower() not in _MESH_SUFFIXES:
        raise UiRequestError("mesh filename must end in .obj, .stl, .ply, or .3mf")
    return value


def _query_optional_float(query: dict[str, str], key: str, default: float | None) -> float | None:
    value = query.get(key)
    if value is None or value == "":
        return default
    return _query_float(query, key, 0.0)


def _query_float(query: dict[str, str], key: str, default: float) -> float:
    value = query.get(key)
    if value is None or value == "":
        return float(default)
    try:
        resolved = float(value)
    except ValueError as exc:
        raise UiRequestError(f"{key} must be a number") from exc
    if not math.isfinite(resolved):
        raise UiRequestError(f"{key} must be finite")
    return resolved


def _required_id(payload: dict[str, Any], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value:
        raise UiRequestError(f"{key} must be a non-empty opaque id")
    return value


def _form_warning_payload(warning: Any) -> dict[str, Any]:
    return {
        "code": warning.code.value,
        "severity": warning.severity.value,
        "message": warning.message,
        "layer": None if warning.ring is None else warning.ring.layer_index,
        "island": None if warning.ring is None else warning.ring.island_index,
    }


def _bounds_payload(bounds: Any) -> dict[str, float]:
    return {
        "min_x": bounds.min_x,
        "max_x": bounds.max_x,
        "min_y": bounds.min_y,
        "max_y": bounds.max_y,
        "min_z": bounds.min_z,
        "max_z": bounds.max_z,
    }


def _json_response(response_type: Any, payload: dict[str, Any]) -> Any:
    return response_type(
        content=json.dumps(
            payload,
            allow_nan=False,
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8"),
        media_type="application/json",
    )


def _weave_session_cookie() -> str:
    from clayline.webui.weave_session import CACHE_SESSION_COOKIE

    return CACHE_SESSION_COOKIE


def _set_weave_cookie(response: Any, token: str, *, created: bool) -> None:
    from clayline.webui.weave_session import DEFAULT_TTL_SECONDS

    # Refreshing the bounded server-side TTL and cookie together keeps an
    # active console alive; `created` is retained for explicit call-site truth.
    del created
    response.set_cookie(
        _weave_session_cookie(),
        token,
        max_age=int(DEFAULT_TTL_SECONDS),
        httponly=True,
        samesite="strict",
        secure=False,
        path="/api/weave",
    )


def _milliseconds(seconds: float) -> float:
    return round(seconds * 1000.0, 3)


def _slice_response_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(
        _slice_payload(payload),
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")


def _demo_slice_response_bytes(fixture: str) -> bytes:
    """Run the normal slice worker on one bundled example SVG (read-only)."""

    if not isinstance(fixture, str) or not _DEMO_FIXTURE_NAME.fullmatch(fixture):
        raise UiRequestError("fixture must name a bundled example (letters, digits, - or _)")
    for directory in _DEMO_FIXTURE_DIRS:
        path = _REPO_EXAMPLES / directory / f"{fixture}.svg"
        if path.is_file():
            svg = path.read_text(encoding="utf-8")
            return _slice_response_bytes({"files": [{"name": path.name, "svg": svg}]})
    raise UiRequestError(
        f"no bundled example named {fixture!r} (looked in {', '.join(_DEMO_FIXTURE_DIRS)})",
        status_code=404,
    )


def _write_expanded_sources(
    files: tuple[tuple[str, str, int, Point, float, float], ...],
    root: Path,
) -> tuple[tuple[Path, ...], tuple[Point, ...], tuple[tuple[float, float], ...]]:
    """Write each uploaded SVG once and expand copies into ordered page lists."""

    expanded_sources: list[Path] = []
    nudges: list[Point] = []
    transforms: list[tuple[float, float]] = []
    for index, (name, svg, copies, nudge, rotation, page_scale) in enumerate(files):
        source_directory = root / f"source-{index + 1:02d}"
        source_directory.mkdir()
        path = source_directory / _svg_basename(name)
        path.write_text(svg, encoding="utf-8")
        expanded_sources.extend([path] * copies)
        nudges.extend([nudge] * copies)
        transforms.extend([(rotation, page_scale)] * copies)
    return tuple(expanded_sources), tuple(nudges), tuple(transforms)


def _require_total_bytes_within_limit(
    files: tuple[tuple[str, str, int, Point, float, float], ...],
) -> None:
    total_bytes = sum(len(file[1].encode("utf-8")) for file in files)
    if total_bytes > _MAX_TOTAL_BYTES:
        raise UiRequestError(
            f"These files add up to {total_bytes / 1_048_576:.1f} MB — the studio accepts "
            f"up to {_MAX_TOTAL_BYTES // 1_048_576} MB per job. Simplify the drawings or "
            "slice them in smaller groups.",
            code="input_too_large",
            data={"total_bytes": total_bytes, "limit_bytes": _MAX_TOTAL_BYTES},
        )


def _design_sizes(
    expanded_sources: tuple[Path, ...],
    *,
    scale: float | str,
    flatten_tol: float,
) -> tuple[tuple[float, float], ...]:
    """Ingest each unique SVG once (the pipeline's own loader) and measure it.

    This is ingest + bounding box only — no planning, no emission (F9.7's
    live check must be fast) — but the sizing comes from the identical
    ``load_svg`` call the slice path performs, never a re-implementation.
    """

    from clayline.api import load_svg

    sizes_by_path: dict[Path, tuple[float, float]] = {}
    for source in dict.fromkeys(expanded_sources):
        design = load_svg(source, scale=scale, flatten_tol=flatten_tol)
        xs = [point.x for polyline in design.polylines for point in polyline.points]
        ys = [point.y for polyline in design.polylines for point in polyline.points]
        if not xs:
            raise UiRequestError(f"{source.name!r} contains no drawable strokes")
        sizes_by_path[source] = (max(xs) - min(xs), max(ys) - min(ys))
    return tuple(sizes_by_path[source] for source in expanded_sources)


def _planned_source_sizes(
    expanded_sources: tuple[Path, ...],
    *,
    flatten_tol: float,
    nozzle_diameter: float,
    bead_width: float | None,
    weld_tol: float,
    kiss: bool,
    kiss_tol: float | None,
    overlap_fraction: float,
    layer_height: float,
    z_mode: ZMode,
) -> tuple[tuple[float, float], ...]:
    """Schema-2 source bounds from the same ingest/planning path as slicing."""

    from clayline.api import load_svg

    sizes_by_path: dict[Path, tuple[float, float]] = {}
    for source in dict.fromkeys(expanded_sources):
        design = load_svg(source, scale=1.0, flatten_tol=flatten_tol)
        plan = design.plan(
            nozzle=nozzle_diameter,
            bead_width=bead_width,
            weld_tol=weld_tol,
            kiss=kiss,
            kiss_tol=kiss_tol,
            overlap_fraction=overlap_fraction,
            layer_height=layer_height,
            auto_center=False,
            z_mode=z_mode,
        )
        width = plan.bounds.max_x - plan.bounds.min_x
        height = plan.bounds.max_y - plan.bounds.min_y
        if not math.isfinite(width) or not math.isfinite(height) or max(width, height) <= 0:
            raise UiRequestError(f"{source.name!r} contains no measurable planned centerline")
        sizes_by_path[source] = (width, height)
    return tuple(sizes_by_path[source] for source in expanded_sources)


def _layout_overflow_error(
    expanded_sources: tuple[Path, ...],
    nudges: tuple[Point, ...],
    request: Any,
) -> UiRequestError:
    """Build the F9.7 bed-overflow 422 with per-page numbers and ways out."""

    from clayline.profiles import load_profile
    from clayline.stack import check_layout

    profile = (
        request.profile if isinstance(request.profile, Profile) else load_profile(request.profile)
    )
    sizes = _design_sizes(
        expanded_sources,
        scale=request.scale,
        flatten_tol=request.flatten_tol,
    )
    check = check_layout(
        sizes,
        nudges,
        page_gap=request.page_gap,
        page_mode=request.page_mode,
        profile=profile,
    )
    data = {
        "needed_x_mm": _mm(check.needed_x_mm),
        "needed_y_mm": _mm(check.needed_y_mm),
        "bed_x_mm": _mm(check.bed_x_mm),
        "bed_y_mm": _mm(check.bed_y_mm),
        "page_count": len(expanded_sources),
        "page_gap_mm": _mm(request.page_gap),
        "page_mode": request.page_mode.value,
    }
    page_count = len(expanded_sources)
    if page_count > 1 and request.page_mode is PageMode.BED:
        if check.needed_x_mm > check.bed_x_mm + 1e-6:
            needed, bed = _mm(check.needed_x_mm), _mm(check.bed_x_mm)
        elif check.needed_y_mm > check.bed_y_mm + 1e-6:
            needed, bed = _mm(check.needed_y_mm), _mm(check.bed_y_mm)
        else:
            return UiRequestError(
                f"These {page_count} pages sit partly off the bed — the placement nudges "
                "push the layout outside. Reduce the nudges or re-center the pages.",
                code="bed_overflow",
                data=data,
            )
        return UiRequestError(
            f"These {page_count} pages don't fit side by side ({needed:g} mm needed, "
            f"bed is {bed:g} mm). Try the design's own size, a smaller gap, or Stack mode.",
            code="bed_overflow",
            data=data,
        )
    widest = max(check.placements, key=lambda item: item.width_mm * item.height_mm)
    if (
        widest.width_mm <= check.bed_x_mm + 1e-6
        and widest.height_mm <= check.bed_y_mm + 1e-6
        and all(
            placement.width_mm <= check.bed_x_mm + 1e-6
            and placement.height_mm <= check.bed_y_mm + 1e-6
            for placement in check.placements
        )
    ):
        return UiRequestError(
            "The design fits the bed, but its placement nudge pushes it outside. "
            "Reduce the nudge or re-center it.",
            code="out_of_bed",
            data=data,
        )
    return UiRequestError(
        f"This design doesn't fit the bed ({_mm(widest.width_mm):g} x "
        f"{_mm(widest.height_mm):g} mm; bed is {_mm(check.bed_x_mm):g} x "
        f"{_mm(check.bed_y_mm):g} mm). Try the design's own size or a smaller scale.",
        code="out_of_bed",
        data=data,
    )


def _mm(value: float) -> float:
    return round(float(value), 1)


def _layout_check_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """F9.7 pre-slice bed-fit check: ingest + bbox through the slice layout math."""

    from clayline.profiles import load_profile
    from clayline.stack import check_layout

    draw_schema_version = _draw_schema_version(payload)
    explicit_passes = draw_schema_version == 2
    files = _validated_files(payload.get("files"), explicit_passes=explicit_passes)
    _require_total_bytes_within_limit(files)
    page_mode = PageMode(_string(payload, "page_mode", _defaults.DEFAULT_PAGE_MODE))
    if explicit_passes and page_mode is not PageMode.STACK:
        raise UiRequestError("draw_schema_version 2 pass rows require page_mode='stack'")
    if explicit_passes and payload.get("scale") is not None:
        raise UiRequestError(
            "draw_schema_version 2 uses per-pass Size; global scale must be null or omitted"
        )
    page_gap = _finite(payload, "page_gap", _defaults.DEFAULT_PAGE_GAP_MM, minimum=0.0)
    profile = load_profile(_string(payload, "profile", "potterbot-xl"))
    scale = (
        1.0
        if explicit_passes
        else (
            _defaults.resolved_scale(_defaults.DEFAULT_SCALE)
            if payload.get("scale") is None
            else _scale(payload["scale"])
        )
    )
    flatten_tol = _finite(payload, "flatten_tol", _defaults.DEFAULT_FLATTEN_TOL_MM, minimum=0.001)

    with tempfile.TemporaryDirectory(prefix="clayline-ui-layout-") as directory:
        expanded_sources, nudges, transforms = _write_expanded_sources(files, Path(directory))
        if explicit_passes:
            source_sizes = _planned_source_sizes(
                expanded_sources,
                flatten_tol=flatten_tol,
                nozzle_diameter=_finite(
                    payload,
                    "nozzle",
                    _defaults.DEFAULT_NOZZLE_DIAMETER_MM,
                    minimum=0.01,
                ),
                bead_width=_optional_finite(payload, "bead_width", minimum=0.01),
                weld_tol=_finite(
                    payload,
                    "weld_tol",
                    _defaults.DEFAULT_WELD_TOL_MM,
                    minimum=0.0,
                ),
                kiss=_boolean(payload, "kiss", _defaults.DEFAULT_KISS),
                kiss_tol=_optional_finite(payload, "kiss_tol", minimum=0.0),
                overlap_fraction=_finite(
                    payload,
                    "overlap_fraction",
                    0.2,
                    minimum=0.0,
                    maximum=1.0,
                ),
                layer_height=_finite(
                    payload,
                    "layer_height",
                    _defaults.DEFAULT_LAYER_HEIGHT_MM,
                    minimum=0.001,
                ),
                z_mode=ZMode(_string(payload, "z_mode", _defaults.DEFAULT_Z_MODE)),
            )
        else:
            source_sizes = _design_sizes(
                expanded_sources,
                scale=scale,
                flatten_tol=flatten_tol,
            )
        sizes = tuple(
            _transformed_size(size, rotation, page_scale)
            for size, (rotation, page_scale) in zip(source_sizes, transforms, strict=True)
        )
        check = check_layout(
            sizes,
            nudges,
            page_gap=page_gap,
            page_mode=page_mode,
            profile=profile,
        )
    return {
        "fits": check.fits,
        "needed_x_mm": _round3(check.needed_x_mm),
        "needed_y_mm": _round3(check.needed_y_mm),
        "bed_x_mm": _round3(check.bed_x_mm),
        "bed_y_mm": _round3(check.bed_y_mm),
        "pages": [
            {
                "name": source.stem,
                "w_mm": _round3(placement.width_mm),
                "h_mm": _round3(placement.height_mm),
                "x0": _round3(placement.min_x),
                "y0": _round3(placement.min_y),
                "x1": _round3(placement.max_x),
                "y1": _round3(placement.max_y),
                "rotation_deg": _round3(transform[0]),
                "scale_factor": _round3(transform[1]),
                **(
                    {
                        "source_w_mm": source_size[0],
                        "source_h_mm": source_size[1],
                        "source_longest_mm": max(source_size),
                    }
                    if explicit_passes
                    else {}
                ),
            }
            for source, placement, transform, source_size in zip(
                expanded_sources,
                check.placements,
                transforms,
                source_sizes,
                strict=True,
            )
        ],
    }


def _transformed_size(
    size: tuple[float, float], rotation_deg: float, page_scale: float
) -> tuple[float, float]:
    """Axis-aligned bounding size of a rotated, scaled page (live bed-fit)."""

    import math as _math

    width, height = size
    angle = _math.radians(rotation_deg)
    cos_a = abs(_math.cos(angle))
    sin_a = abs(_math.sin(angle))
    return (
        page_scale * (width * cos_a + height * sin_a),
        page_scale * (width * sin_a + height * cos_a),
    )


def _round3(value: float) -> float:
    return round(float(value), 3)


def _layout_check_response_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(
        _layout_check_payload(payload),
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")


def _prepared_trace_payload(
    prepared: Any,
    *,
    passes: int,
    layer_height: float,
    bead_width: float | None = None,
    pass_labels: list[str] | None,
    page_names: list[str],
    axis_labels: dict[str, str] | None = None,
    layer_labels: list[str] | None = None,
    stroke_indices: dict[tuple[int, str], int] | None = None,
    stroke_elements: dict[tuple[int, str], str] | None = None,
    global_pass_order: bool = False,
) -> dict[str, Any]:
    """Mode-neutral serializer for one exact prepared emission trace."""

    from clayline.emit import EmissionMotion
    from clayline.models import MoveKind

    indices = {} if stroke_indices is None else dict(stroke_indices)
    elements = {} if stroke_elements is None else dict(stroke_elements)
    moves: list[list[Any]] = []
    for event in prepared.events:
        if not isinstance(event, EmissionMotion):
            continue
        kind = (
            (1 if event.extrude else 2)
            if event.kind
            in (
                MoveKind.PRINT,
                MoveKind.CARRY,
                MoveKind.THREAD_RELEASE,
            )
            else 0
        )
        pass_index = event.layer
        if global_pass_order:
            # Schema-2 jobs always carry one layer per page today.  Retain the
            # general page-major formula without multiplying by the total pass
            # count passed to this serializer.
            layers_per_page = max(1, passes // max(1, len(page_names)))
            pass_index = event.page * layers_per_page + event.layer
        key = None if event.stroke is None else (event.page, event.stroke)
        if key is not None and key not in indices:
            indices[key] = len(indices)
            metadata = dict(event.source_move.metadata)
            elements[key] = str(metadata.get("page_name", ""))
        moves.append(
            [
                round(event.point.x, 6),
                round(event.point.y, 6),
                round(event.point.z, 6),
                kind,
                pass_index,
                -1 if key is None else indices.get(key, -1),
                pass_index if global_pass_order else event.page,
                "" if key is None else elements.get(key, ""),
                # W16 (additive column): the flow multiplier the E math used,
                # so the preview can color by clay flow without recomputing.
                round(event.source_move.flow_multiplier, 4),
            ]
        )
    initial = prepared.initial_point
    meta: dict[str, Any] = {
        "passes": passes,
        "layer_height": layer_height,
    }
    if bead_width is not None:
        # Weave's pseudo-tube viewport consumes the exact sliced width.  Draw
        # keeps its historical trace meta shape and reads the same fact from
        # the finalized report parameters instead.
        meta["bead_width"] = bead_width
    # Tiles retains its historical `pass_labels` key and exact meta shape.
    # Weave supplies honest layer terminology through the mode-neutral keys.
    if pass_labels is not None:
        meta["pass_labels"] = pass_labels
    meta["page_names"] = page_names
    meta["start"] = (
        None if initial is None else [round(initial.x, 6), round(initial.y, 6), round(initial.z, 6)]
    )
    if axis_labels is not None:
        meta["axis_labels"] = axis_labels
    if layer_labels is not None:
        meta["layer_labels"] = layer_labels
    return {"moves": moves, "meta": meta}


def _trace_payload(emission: Any) -> dict[str, Any]:
    """Serialize the exact export trace for the F9.5 scrubber (rule R2).

    Every entry is one prepared :class:`~clayline.emit.EmissionMotion` — the
    same events, in the same order, that FullControl turns into the G-code
    body one line per motion (``stats.motion_count`` in the header counts the
    identical events).  There is no parallel display-geometry path.

    Move layout: ``[x, y, z, kind, pass_idx, stroke_idx, page_idx, elem]``
    with kind 0=travel, 1=extrude, 2=non-deposit tail; coordinates are plan mm
    (the same frame the plotly figure uses).  ``stroke_idx`` is the plan-level
    stroke index across pages (travels carry the stroke they approach);
    ``elem`` is the source SVG element provenance of that stroke.
    """

    job = emission.laid_out_job
    stroke_indices: dict[tuple[int, str], int] = {}
    stroke_elems: dict[tuple[int, str], str] = {}
    for page_index, page in enumerate(job.pages):
        for stroke in page.plan.strokes:
            key = (page_index, stroke.id)
            stroke_indices[key] = len(stroke_indices)
            stroke_elems[key] = _stroke_elem(stroke)
    global_pass_order = (
        job.pass_model is PassModel.EXPLICIT_PASSES and job.page_mode is PageMode.STACK
    )
    passes = len(job.pages) * job.settings.layers if global_pass_order else job.settings.layers
    return _prepared_trace_payload(
        emission.prepared,
        passes=passes,
        layer_height=job.settings.layer_height,
        pass_labels=[f"Pass {index + 1} of {passes}" for index in range(passes)],
        page_names=[page.name for page in job.pages],
        stroke_indices=stroke_indices,
        stroke_elements=stroke_elems,
        global_pass_order=global_pass_order,
    )


def _stroke_elem(stroke: Any) -> str:
    """One human-readable provenance label per plan stroke (F2.3)."""

    labels: list[str] = []
    for provenance in stroke.provenance:
        label = provenance.element_id or f"element[{provenance.element_index}]"
        if label not in labels:
            labels.append(label)
    if not labels:
        return ""
    if len(labels) == 1:
        return labels[0]
    return f"{labels[0]} (+{len(labels) - 1} more)"


def _validated_files(
    value: Any,
    *,
    explicit_passes: bool = False,
) -> tuple[tuple[str, str, int, Point, float, float], ...]:
    if not isinstance(value, list) or not value:
        raise UiRequestError("add at least one SVG file")
    if len(value) > _MAX_FILES:
        raise UiRequestError(f"local UI accepts at most {_MAX_FILES} source files per job")
    files: list[tuple[str, str, int, Point, float, float]] = []
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            raise UiRequestError(f"file {index + 1} must be an object")
        name = item.get("name")
        svg = item.get("svg")
        if not isinstance(name, str) or not name.strip():
            raise UiRequestError(f"file {index + 1} needs a name")
        if not isinstance(svg, str) or "<svg" not in svg[:4096].lower():
            raise UiRequestError(f"{name!r} is not recognizable SVG text")
        svg_bytes = len(svg.encode("utf-8"))
        if svg_bytes > _MAX_SVG_BYTES:
            raise UiRequestError(
                f"'{name}' is {svg_bytes / 1_048_576:.1f} MB — the studio accepts files up "
                f"to {_MAX_SVG_BYTES // 1_048_576} MB. Simplify the drawing (fewer points) "
                "and try again.",
                code="input_too_large",
                data={
                    "name": name,
                    "actual_bytes": svg_bytes,
                    "limit_bytes": _MAX_SVG_BYTES,
                },
            )
        if explicit_passes and "copies" in item:
            raise UiRequestError(
                "draw_schema_version 2 uses one row per pass; repeat the pass row instead of "
                "sending copies"
            )
        copies = item.get("copies", 1)
        if isinstance(copies, bool) or not isinstance(copies, int) or not 1 <= copies <= 100:
            raise UiRequestError(f"{name!r} copies must be an integer from 1 to 100")
        nudge = Point(
            _mapping_finite(item, "nudge_x", 0.0),
            _mapping_finite(item, "nudge_y", 0.0),
        )
        rotation = _mapping_finite(item, "rotation_deg", 0.0)
        page_scale = _mapping_finite(item, "scale_factor", 1.0, minimum=0.01, maximum=100.0)
        files.append((name, svg, copies, nudge, rotation, page_scale))
    if sum(file[2] for file in files) > 100:
        raise UiRequestError("expanded job accepts at most 100 pages")
    return tuple(files)


def _svg_basename(name: str) -> str:
    basename = Path(name.replace("\\", "/")).name
    if not basename.lower().endswith(".svg"):
        raise UiRequestError(f"{name!r} must have an .svg filename")
    if basename in {".svg", "..svg"} or any(ord(character) < 32 for character in basename):
        raise UiRequestError(f"{name!r} is not a safe SVG filename")
    if len(basename.encode("utf-8")) > _MAX_SOURCE_NAME_BYTES:
        raise UiRequestError(f"{name!r} exceeds the {_MAX_SOURCE_NAME_BYTES}-byte filename limit")
    return basename


def _artifact_stem(value: Any, *, source_name: str | None = None) -> str:
    """Resolve the export stem: explicit name, else the first page's SVG stem."""

    if not isinstance(value, str) or not value.strip():
        if source_name is not None:
            derived = _safe_stem_text(Path(source_name.replace("\\", "/")).stem)
            if derived:
                return derived
        return "clayline-job"
    basename = Path(value.replace("\\", "/")).name.strip()
    stem = Path(basename).stem if basename.lower().endswith(".gcode") else basename
    return _safe_stem_text(stem) or "clayline-job"


def _safe_stem_text(stem: str) -> str:
    safe = _UNSAFE_FILENAME_CHARS.sub("-", stem).strip("-._")
    return safe[:_MAX_ARTIFACT_STEM_CHARS].rstrip("-._")


def _svg_first_word(name: str) -> str:
    """First word of an SVG's name — the token before the first -, _ or space."""

    stem = Path(str(name).replace("\\", "/")).stem
    token = re.split(r"[-_\s]+", stem, maxsplit=1)[0]
    return _safe_stem_text(token)


def _default_export_stem(file_names: list[str]) -> str:
    """Default export name: the first word of every included SVG, joined.

    Pete 2026-07-23: name a multi-tile job after its parts, not just the
    first file. Duplicate first words collapse (two copies of one tile add
    one word), order is preserved, and the whole thing is length-capped.
    """

    words: list[str] = []
    for name in file_names:
        word = _svg_first_word(name)
        if word and word not in words:
            words.append(word)
    joined = "-".join(words)[:_MAX_ARTIFACT_STEM_CHARS].rstrip("-._")
    return joined or "clayline-job"


def _profile_label(name: str) -> str:
    return {
        "delta-wasp-2040-clay": "Delta WASP 2040 Clay",
        "eazao-matrix-m500": "Eazao Matrix M500",
        "eazao-zero": "Eazao Zero",
        "potterbot-10-micro": "PotterBot Micro 10",
        "potterbot-10-pro": "PotterBot 10 Pro",
        "potterbot-super-10": "PotterBot Super 10",
        "potterbot-xl": "PotterBot 10 XL",
        "wasp-40100-ldm": "Delta WASP 40100 Clay (40100 LDM)",
        "generic-reprap-paste": "Generic RepRap paste",
        "generic-marlin-paste": "Generic Marlin paste",
    }.get(name, name)


def _profile_facts(name: str) -> str | None:
    return {
        "delta-wasp-2040-clay": ("round 200 mm bed — using the safe centered 120 x 120 mm square"),
        "wasp-40100-ldm": ("round 400 mm bed — using the safe centered 240 x 240 mm square"),
    }.get(name)


def _draw_schema_version(payload: dict[str, Any]) -> int | None:
    if "draw_schema_version" not in payload:
        return None
    value = payload["draw_schema_version"]
    if isinstance(value, bool) or not isinstance(value, int) or value != 2:
        raise UiRequestError("draw_schema_version must be 2 when provided")
    return value


def _scale(value: Any) -> float | str:
    if isinstance(value, str) and value.startswith("fit:"):
        suffix = value.removeprefix("fit:")
        try:
            size = float(suffix)
        except ValueError as exc:
            raise UiRequestError("fit scale must end in millimetres") from exc
        if not math.isfinite(size) or size <= 0:
            raise UiRequestError("fit scale must be finite and positive")
        return f"fit:{size:g}"
    if isinstance(value, bool):
        raise UiRequestError("scale must be numeric or fit:<millimetres>")
    try:
        scale = float(value)
    except (TypeError, ValueError) as exc:
        raise UiRequestError("scale must be numeric or fit:<millimetres>") from exc
    if not math.isfinite(scale) or scale <= 0:
        raise UiRequestError("scale must be finite and positive")
    return scale


def _finite(
    payload: dict[str, Any],
    key: str,
    default: float,
    *,
    minimum: float | None = None,
    maximum: float | None = None,
) -> float:
    return _mapping_finite(payload, key, default, minimum=minimum, maximum=maximum)


def _optional_finite(
    payload: dict[str, Any],
    key: str,
    *,
    minimum: float | None = None,
    maximum: float | None = None,
) -> float | None:
    value = payload.get(key)
    if value is None:
        return None
    return _mapping_finite(payload, key, 0.0, minimum=minimum, maximum=maximum)


def _mapping_finite(
    payload: dict[str, Any],
    key: str,
    default: float,
    *,
    minimum: float | None = None,
    maximum: float | None = None,
) -> float:
    value = payload.get(key, default)
    if isinstance(value, bool):
        raise UiRequestError(f"{key} must be numeric")
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise UiRequestError(f"{key} must be numeric") from exc
    if not math.isfinite(number):
        raise UiRequestError(f"{key} must be finite")
    if minimum is not None and number < minimum:
        raise UiRequestError(f"{key} must be at least {minimum:g}")
    if maximum is not None and number > maximum:
        raise UiRequestError(f"{key} must be at most {maximum:g}")
    return number


def _integer(
    payload: dict[str, Any],
    key: str,
    default: int,
    *,
    minimum: int,
    maximum: int,
) -> int:
    value = payload.get(key, default)
    if isinstance(value, bool) or not isinstance(value, int):
        raise UiRequestError(f"{key} must be an integer")
    if not minimum <= value <= maximum:
        raise UiRequestError(f"{key} must be between {minimum} and {maximum}")
    return value


def _boolean(payload: dict[str, Any], key: str, default: bool) -> bool:
    value = payload.get(key, default)
    if not isinstance(value, bool):
        raise UiRequestError(f"{key} must be true or false")
    return value


def _string(payload: dict[str, Any], key: str, default: str) -> str:
    value = payload.get(key, default)
    if not isinstance(value, str) or not value.strip():
        raise UiRequestError(f"{key} must be a non-empty string")
    return value


__all__ = ["SESSION_COOKIE", "UiRequestError", "create_app", "run_ui"]
