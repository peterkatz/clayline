"""Portable image relief and periodic surface coordinates for Mesh Images.

Images are sampled as scalar data. In particular a 16-bit catalogue PNG never
passes through an 8-bit display conversion before it shapes the printed wall.
"""

from __future__ import annotations

import base64
import binascii
import io
from dataclasses import dataclass, field, fields
from functools import lru_cache
from importlib.resources import files
from itertools import pairwise
from typing import TYPE_CHECKING, Any

import numpy as np
from numpy.typing import ArrayLike, NDArray

if TYPE_CHECKING:
    from clayline.weave_models import CurvePoint, WeaveSettings

MAX_IMAGES = 3
MAX_SOURCE_BYTES = 16 * 1024 * 1024
MAX_SOURCE_PIXELS = 16 * 1024 * 1024


def _flat_extrusion() -> tuple[CurvePoint, ...]:
    from clayline.weave_models import CurvePoint

    return (CurvePoint(0.0, 1.0), CurvePoint(0.5, 1.0))


@dataclass(frozen=True, slots=True)
class ImageEffect:
    """An independently placed, shaded, and layered Image on the exterior wall."""

    source_id: str | None = None
    data_base64: str | None = None
    name: str | None = None
    enabled: bool = True
    placement: str = "repeat"
    repeats: int = 8
    width_mm: float = 40.0
    height_mm: float = 40.0
    rotation_deg: float = 0.0
    offset_around_deg: float = 0.0
    offset_height_mm: float = 0.0
    flip_x: bool = False
    flip_y: bool = False
    invert: bool = False
    blend_edges: bool = False
    feather_mm: float = 0.0
    amplitude: float = 0.0
    follow_lobes: float = 1.0
    follow_coves: float = 1.0
    flow_lobes: float = 1.0
    flow_coves: float = 1.0
    extrusion: tuple[CurvePoint, ...] = field(default_factory=_flat_extrusion)
    extrusion_phase_offset: float = 0.0
    layer_skip_enabled: bool = False
    layer_skip_start: int = 0
    layer_skip_on: int = 2
    layer_skip_off: int = 2
    layer_skip_end: int = 0
    fade_in_layers: int = 0
    fade_out_layers: int = 0

    def __post_init__(self) -> None:
        from clayline.weave_models import CurvePoint

        for key in ("source_id", "data_base64", "name"):
            value = getattr(self, key)
            if value is not None and not isinstance(value, str):
                raise ValueError(f"Image {key} must be text or null")
        if self.source_id and self.data_base64:
            raise ValueError("An Image uses either a catalogue source or uploaded artwork")
        if self.source_id and self.source_id not in _catalogue_by_id():
            raise ValueError("Choose an Image from the catalogue or upload its artwork")
        if self.data_base64:
            _source_data(self.source_id, self.data_base64)
        for key in ("enabled", "flip_x", "flip_y", "invert", "blend_edges", "layer_skip_enabled"):
            if not isinstance(getattr(self, key), bool):
                raise ValueError(f"Image {key} must be a boolean")
        if self.placement not in {"repeat", "once"}:
            raise ValueError("Image placement must be repeat or once")
        for key in ("repeats", "layer_skip_start", "layer_skip_on", "layer_skip_off",
                    "layer_skip_end", "fade_in_layers", "fade_out_layers"):
            value = getattr(self, key)
            if isinstance(value, bool) or not isinstance(value, int):
                raise ValueError(f"Image {key} must be an integer")
            minimum = 1 if key in {"repeats", "layer_skip_on", "layer_skip_off"} else 0
            if value < minimum:
                raise ValueError(f"Image {key} must be at least {minimum}")
        if self.repeats > 4096:
            raise ValueError("Image repeat count must be at most 4096")
        numeric = ("width_mm", "height_mm", "rotation_deg", "offset_around_deg",
                   "offset_height_mm", "feather_mm", "amplitude", "follow_lobes", "follow_coves",
                   "flow_lobes", "flow_coves", "extrusion_phase_offset")
        for key in numeric:
            value = getattr(self, key)
            if isinstance(value, (bool, np.bool_)) or not isinstance(value, (int, float)):
                raise ValueError(f"Image {key} must be a finite number")
            if not np.isfinite(value):
                raise ValueError(f"Image {key} must be a finite number")
            object.__setattr__(self, key, float(value))
        if min(self.width_mm, self.height_mm) <= 0:
            raise ValueError("Image width and height must be positive")
        if min(self.feather_mm, self.amplitude, self.follow_lobes, self.follow_coves,
               self.flow_lobes, self.flow_coves) < 0:
            raise ValueError("Image depth, feather, and wall multipliers cannot be negative")
        try:
            extrusion = tuple(self.extrusion)
        except TypeError as exc:
            raise ValueError("Image extrusion must be a curve") from exc
        if len(extrusion) < 2 or any(not isinstance(p, CurvePoint) for p in extrusion):
            raise ValueError("Image extrusion must contain at least two curve points")
        if any(a.u >= b.u for a, b in pairwise(extrusion)):
            raise ValueError("Image extrusion curve points must increase along the track")
        if any(not 0.25 <= p.value <= 3 for p in extrusion):
            raise ValueError("Image extrusion values must stay in [0.25, 3]")
        object.__setattr__(self, "extrusion", extrusion)

    @property
    def settings(self) -> WeaveSettings:
        """The shared per-effect controls, with the same limits as a Weave."""
        from clayline.weave_models import WeaveSettings

        names = ("amplitude", "follow_lobes", "follow_coves", "flow_lobes", "flow_coves",
                 "extrusion_phase_offset", "layer_skip_enabled", "layer_skip_start",
                 "layer_skip_on", "layer_skip_off", "layer_skip_end", "fade_in_layers",
                 "fade_out_layers")
        # Older callers can load the source module before the wall engine is
        # upgraded; the current engine supplies these same fade fields.
        accepted = {item.name for item in fields(WeaveSettings)}
        return WeaveSettings(**{name: getattr(self, name) for name in names if name in accepted})


def image_from_payload(value: Any) -> ImageEffect:
    """Read a bounded portable Image payload without lossy source conversion."""
    from clayline.weave_models import CurvePoint

    if not isinstance(value, dict):
        raise ValueError("Each Image must be an object")
    known = {item.name for item in fields(ImageEffect)}
    unknown = value.keys() - known
    if unknown:
        raise ValueError(f"Unknown Image settings: {', '.join(sorted(unknown))}")
    kwargs = dict(value)
    if "extrusion" in kwargs:
        raw = kwargs["extrusion"]
        if not isinstance(raw, list) or len(raw) > 4096:
            raise ValueError("Image extrusion must be an array of curve points")
        points = []
        for point in raw:
            if not isinstance(point, dict) or set(point) != {"u", "value"}:
                raise ValueError("Image extrusion points need u and value")
            if any(isinstance(v, bool) or not isinstance(v, (float, int)) for v in point.values()):
                raise ValueError("Image extrusion curve coordinates must be numbers")
            points.append(CurvePoint(float(point["u"]), float(point["value"])))
        kwargs["extrusion"] = tuple(points)
    return ImageEffect(**kwargs)


def image_to_payload(effect: ImageEffect) -> dict[str, Any]:
    """Keep original uploaded bytes inside patterns and portable projects."""
    payload = {item.name: getattr(effect, item.name) for item in fields(effect)}
    payload["extrusion"] = [{"u": float(p.u), "value": float(p.value)} for p in effect.extrusion]
    return payload


@lru_cache(maxsize=1)
def image_catalogue() -> tuple[dict[str, Any], ...]:
    """The 80 original, 16-bit relief masters in a stable catalogue order."""
    root = files("clayline").joinpath("image_catalogue")
    return tuple(
        {"id": p.name.removesuffix(".png"),
         "name": p.name.removesuffix(".png").replace("-", " ").title(),
         "filename": p.name, "width": 1024, "height": 1024, "seamless": True}
        for p in sorted(root.iterdir(), key=lambda p: p.name) if p.name.endswith(".png")
    )


@lru_cache(maxsize=1)
def _catalogue_by_id() -> dict[str, dict[str, Any]]:
    return {item["id"]: item for item in image_catalogue()}


def image_bytes(effect: ImageEffect) -> bytes:
    if effect.source_id:
        metadata = _catalogue_by_id()[effect.source_id]
        return files("clayline").joinpath("image_catalogue", metadata["filename"]).read_bytes()
    if effect.data_base64:
        data = effect.data_base64
        if data.startswith("data:"):
            if ";base64," not in data:
                raise ValueError("Upload an image as base64 artwork")
            data = data.split(";base64,", 1)[1]
        if len(data) > (MAX_SOURCE_BYTES + 2) // 3 * 4:
            raise ValueError("Image artwork must be no larger than 16 MB")
        try:
            result = base64.b64decode(data, validate=True)
        except (ValueError, binascii.Error) as exc:
            raise ValueError("Image artwork could not be read; choose the image again") from exc
        if len(result) > MAX_SOURCE_BYTES:
            raise ValueError("Image artwork must be no larger than 16 MB")
        return result
    return b""


def _signed_scalar(values: NDArray[Any], maximum: float, neutral: float) -> NDArray[np.float64]:
    delta = np.asarray(values, dtype=np.float64) - neutral
    return np.where(delta >= 0, delta / (maximum - neutral), delta / neutral)


@lru_cache(maxsize=12)
def _source_data(source_id: str | None, data_base64: str | None) -> tuple[NDArray, NDArray]:
    from PIL import Image, ImageOps, UnidentifiedImageError

    try:
        from pi_heif import register_heif_opener

        register_heif_opener()
    except ImportError:
        pass

    # Constructing ImageEffect here would recurse through source validation.
    proxy = object.__new__(ImageEffect)
    object.__setattr__(proxy, "source_id", source_id)
    object.__setattr__(proxy, "data_base64", data_base64)
    raw = image_bytes(proxy)
    if not raw:
        return np.zeros((2, 2)), np.zeros((2, 2))
    try:
        with Image.open(io.BytesIO(raw)) as im:
            if im.width * im.height > MAX_SOURCE_PIXELS or min(im.size) < 1:
                raise ValueError("Choose an image with at most 16 million pixels")
            im.load()
            im = ImageOps.exif_transpose(im)
            if im.mode in {"I;16", "I;16B", "I;16L", "I"}:
                pixels = np.asarray(im, dtype=np.float64)
                # Pillow decodes 16-bit grayscale PNGs as I;16 or I depending
                # on version. The PNG header records the intended precision.
                bit16 = raw[:8] == b"\x89PNG\r\n\x1a\n" and raw[24] == 16
                if bit16 or im.mode.startswith("I;16"):
                    relief = _signed_scalar(pixels, 65535.0, 32768.0)
                else:
                    relief = _signed_scalar(np.clip(pixels, 0, 255), 255.0, 128.0)
                alpha = np.ones_like(relief)
            elif im.mode == "F":
                relief = np.clip(np.asarray(im, dtype=np.float64), 0, 1) * 2 - 1
                alpha = np.ones_like(relief)
            elif im.mode in {"1", "L"}:
                relief = _signed_scalar(np.asarray(im.convert("L")), 255.0, 128.0)
                alpha = np.ones_like(relief)
            else:
                rgba = np.asarray(im.convert("RGBA"), dtype=np.float64)
                # Keep the familiar color-to-gray lightness used by image
                # editors: middle gray RGB 128 remains exactly the wall.
                lightness = rgba[:, :, :3] @ np.array([0.2126, 0.7152, 0.0722])
                relief = _signed_scalar(lightness, 255.0, 128.0)
                alpha = rgba[:, :, 3] / 255.0
            relief = np.clip(relief, -1, 1).astype(np.float32)
            alpha = alpha.astype(np.float32)
            relief *= alpha
            if not np.isfinite(relief).all() or not np.isfinite(alpha).all():
                raise ValueError("Image artwork contains unreadable pixel values")
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as exc:
        raise ValueError("Image artwork could not be read; choose a PNG, JPEG, or WebP") from exc
    relief.setflags(write=False)
    alpha.setflags(write=False)
    return relief, alpha


def image_info(effect: ImageEffect) -> dict[str, Any]:
    relief, _ = _source_data(effect.source_id, effect.data_base64)
    dx = np.abs(relief[:, 0] - relief[:, -1])
    dy = np.abs(relief[0, :] - relief[-1, :])
    edge_error = float(max(np.mean(dx), np.mean(dy)))
    nearby = max((float(np.mean(np.abs(d))) for d in
                  (np.diff(relief[:, :8], axis=1), np.diff(relief[:8, :], axis=0))
                  if d.size), default=0.0)
    seamless = bool(effect.source_id) or edge_error <= max(0.025, nearby * 3)
    return {"width": relief.shape[1], "height": relief.shape[0],
            "seamless": seamless, "edge_error": edge_error}


def image_edge_mismatch(effect: ImageEffect) -> float:
    return float(image_info(effect)["edge_error"])


@lru_cache(maxsize=12)
def _blended_source(source_id: str | None, data_base64: str | None) -> tuple[NDArray, NDArray]:
    original, original_alpha = _source_data(source_id, data_base64)

    def blend(original: NDArray) -> NDArray:
        result = original.copy()
        for axis in (1, 0):
            a = np.moveaxis(result, axis, -1)
            band = min(a.shape[-1] // 2, max(2, round(a.shape[-1] * 0.12)))
            if band < 1:
                continue
            t = np.linspace(0, 1, band)
            weight = 1 - t * t * (3 - 2 * t)
            left = a[..., :band].copy()
            right = a[..., -band:][..., ::-1].copy()
            middle = (left + right) * 0.5
            a[..., :band] = left + (middle - left) * weight
            a[..., -band:] = (right + (middle - right) * weight)[..., ::-1]
        result.setflags(write=False)
        return result

    return blend(original), blend(original_alpha)


def _sample(data: NDArray, u: NDArray, v: NDArray, *, wrap: bool) -> NDArray:
    """Bilinear sampling with pixel centers and opposite-edge neighbors."""
    height, width = data.shape
    x = u * width - 0.5
    y = v * height - 0.5
    if wrap:
        # Reduce first so even very large (but finite) offsets stay safe when
        # floor indices become machine integers.
        x = np.remainder(x, width)
        y = np.remainder(y, height)
    else:
        x = np.clip(x, 0, width - 1)
        y = np.clip(y, 0, height - 1)
    ix, iy = np.floor(x).astype(np.int64), np.floor(y).astype(np.int64)
    fx, fy = x - ix, y - iy
    nx, ny = (ix + 1) % width, (iy + 1) % height
    if not wrap:
        nx, ny = np.minimum(ix + 1, width - 1), np.minimum(iy + 1, height - 1)
    return ((1 - fy) * ((1 - fx) * data[iy, ix] + fx * data[iy, nx])
            + fy * ((1 - fx) * data[ny, ix] + fx * data[ny, nx]))


@dataclass(frozen=True, slots=True)
class RepeatFit:
    """One periodic lattice held over every contour of a continuous exterior."""

    m: int
    n: int
    rotation_deg: float
    width_mm: float
    height_mm: float
    u_height_per_mm: float
    v_height_per_mm: float


def fit_repeat(effect: ImageEffect, reference_circumference_mm: float) -> RepeatFit:
    """Fit the whole rotated field to integer tile periods after one lap.

    The pair of integers is fitted once at the reference contour and retained
    through a taper. Moving a nozzle start never enters these coordinates.
    """
    circumference = max(float(reference_circumference_mm), 1e-6)
    width = circumference / effect.repeats
    height = effect.height_mm
    angle = np.deg2rad(effect.rotation_deg)
    desired_m = circumference * np.cos(angle) / width
    desired_n = -circumference * np.sin(angle) / height
    m, n = round(desired_m), round(desired_n)
    if m == 0 and n == 0:
        # For a tile taller than a tiny piece, the closest nonzero lattice
        # vector is still a usable repeat and is reported beside Rotate.
        candidates = ((1, 0), (-1, 0), (0, 1), (0, -1))
        m, n = min(candidates, key=lambda p: (p[0] - desired_m) ** 2 +
                   (p[1] - desired_n) ** 2)
    scale = np.hypot(m * width, n * height) / circumference
    fitted_angle = np.arctan2(-n * height, m * width)
    applied_width, applied_height = width / scale, height / scale
    return RepeatFit(m=m, n=n, rotation_deg=float(np.rad2deg(fitted_angle)),
                     width_mm=float(applied_width), height_mm=float(applied_height),
                     u_height_per_mm=float(np.sin(fitted_angle) / applied_width),
                     v_height_per_mm=float(np.cos(fitted_angle) / applied_height))


def evaluate_image(
    effect: ImageEffect,
    around: ArrayLike,
    surface_height_mm: ArrayLike,
    circumference_mm: ArrayLike,
    reference_circumference_mm: float,
    *,
    phase_offset: float = 0.0,
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Return signed relief and separate coverage on the original wall.

    ``around`` is the original contour's stable arclength fraction. Height is
    measured up the *surface*, including the continuous rise in Vase mode.
    ``phase_offset`` shifts a clay track while leaving relief coordinates alone.
    """
    around, vertical, circumference = np.broadcast_arrays(
        np.asarray(around, dtype=np.float64), np.asarray(surface_height_mm, dtype=np.float64),
        np.asarray(circumference_mm, dtype=np.float64),
    )
    if not effect.enabled or not (effect.source_id or effect.data_base64):
        return np.zeros_like(around), np.zeros_like(around)
    offset = effect.offset_around_deg / 360
    vertical = vertical - effect.offset_height_mm
    if effect.placement == "repeat":
        fit = fit_repeat(effect, reference_circumference_mm)
        s = around - offset - phase_offset / effect.repeats
        u = fit.m * s + fit.u_height_per_mm * vertical
        # Image rows increase downward; positive surface height reads upward.
        v = fit.n * s + fit.v_height_per_mm * vertical
        coverage = np.ones_like(u)
    else:
        # A stencil center may cross the artwork wrap freely. The shortest
        # arc is measured in millimeters on this original sliced contour.
        s = np.remainder(around - offset - phase_offset * effect.width_mm /
                         np.maximum(circumference, 1e-6) + 0.5, 1) - 0.5
        x = s * circumference
        c, sn = np.cos(np.deg2rad(effect.rotation_deg)), np.sin(np.deg2rad(effect.rotation_deg))
        u = (c * x + sn * vertical) / effect.width_mm + 0.5
        v = (-sn * x + c * vertical) / effect.height_mm + 0.5
        coverage = ((u >= 0) & (u <= 1) & (v >= 0) & (v <= 1)).astype(float)
        if effect.feather_mm > 0:
            edge = np.minimum(np.minimum(u, 1 - u) * effect.width_mm,
                              np.minimum(v, 1 - v) * effect.height_mm)
            t = np.clip(edge / effect.feather_mm, 0, 1)
            coverage *= t * t * (3 - 2 * t)
    if effect.flip_x:
        u = 1 - u
    # A source shown upright in the picker must also climb upright on the pot.
    if not effect.flip_y:
        v = 1 - v
    source = (_blended_source if effect.blend_edges and effect.placement == "repeat"
              else _source_data)
    relief_data, alpha_data = source(effect.source_id, effect.data_base64)
    wrap = effect.placement == "repeat"
    alpha = _sample(alpha_data, u, v, wrap=wrap) * coverage
    # Filter premultiplied relief so hidden colors in transparent pixels do
    # not make a ridge or groove around the edge of uploaded artwork.
    weighted = _sample(relief_data, u, v, wrap=wrap) * coverage
    relief = np.divide(weighted, alpha, out=np.zeros_like(weighted), where=alpha > 1e-12)
    if effect.invert:
        relief = -relief
    return relief, alpha


def image_preview_png(
    effect: ImageEffect, *, repeat: int = 2, blend: bool | None = None, size: int = 256,
) -> bytes:
    """Display-only preview: original relief data remains at full precision."""
    from PIL import Image

    use_blend = (effect.blend_edges and effect.placement == "repeat") if blend is None else blend
    source = _blended_source if use_blend else _source_data
    relief, alpha = source(effect.source_id, effect.data_base64)
    q = (np.arange(size) + 0.5) / size * max(1, repeat)
    u, v = np.meshgrid(q, q)
    if effect.flip_x:
        u = -u
    if effect.flip_y:
        v = -v
    weighted = _sample(relief, u, v, wrap=True)
    opacity = _sample(alpha, u, v, wrap=True)
    value = np.divide(weighted, opacity, out=np.zeros_like(weighted), where=opacity > 1e-12)
    if effect.invert:
        value = -value
    gray = np.rint(np.clip(128 + np.where(value < 0, value * 128, value * 127),
                          0, 255)).astype(np.uint8)
    rgba = np.stack((gray, gray, gray, np.rint(opacity * 255).astype(np.uint8)), axis=-1)
    stream = io.BytesIO()
    Image.fromarray(rgba).save(stream, format="PNG")
    return stream.getvalue()
