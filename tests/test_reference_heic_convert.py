"""M3: HEIC support for the reference lightbox (Pete's iPhone photos).

The drawing surface's reference photo tries local decode first (Safari's
WKWebView opens HEIC natively); this route is the fallback for engines that
can't, converting with Pillow + pillow-heif into an ordinary JPEG. It never
touches a pass or a slice request -- it only ever hands bytes back.
"""

from __future__ import annotations

import asyncio
import io
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import httpx
import pytest

from clayline.webui.app import (
    _MAX_IMAGE_BYTES,
    UiRequestError,
    _convert_image_to_jpeg,
    _limit_label,
    _read_image_request,
    create_app,
)

ORIGIN = {"origin": "http://testserver", "host": "testserver"}


@asynccontextmanager
async def _client(app: object) -> AsyncIterator[httpx.AsyncClient]:
    transport = httpx.ASGITransport(app=app)  # type: ignore[arg-type]
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


def _heic_bytes(
    size: tuple[int, int] = (64, 48), color: tuple[int, int, int] = (180, 90, 30)
) -> bytes:
    pillow_heif = pytest.importorskip("pillow_heif")
    from PIL import Image

    pillow_heif.register_heif_opener()
    image = Image.new("RGB", size, color)
    buffer = io.BytesIO()
    image.save(buffer, format="HEIF", quality=80)
    return buffer.getvalue()


def test_a_heic_photo_comes_back_as_a_decodable_jpeg() -> None:
    pytest.importorskip("pillow_heif")
    from PIL import Image

    async def exercise() -> httpx.Response:
        async with _client(create_app()) as client:
            return await client.post(
                "/api/convert-image",
                content=_heic_bytes(),
                headers={**ORIGIN, "content-type": "application/octet-stream"},
            )

    response = asyncio.run(exercise())
    assert response.status_code == 200, response.text
    assert response.headers["content-type"] == "image/jpeg"
    decoded = Image.open(io.BytesIO(response.content))
    decoded.load()
    assert decoded.format == "JPEG"
    assert decoded.size == (64, 48)


def test_a_sideways_phone_photo_comes_back_upright() -> None:
    # A phone holds a portrait shot as landscape pixels plus an EXIF turn; the
    # JPEG handed back carries no tags, so the turn must be baked into the
    # pixels or the photo lies on its side under the drawing.
    pillow_heif = pytest.importorskip("pillow_heif")
    from PIL import Image

    pillow_heif.register_heif_opener()
    image = Image.new("RGB", (64, 48), (180, 90, 30))
    exif = Image.Exif()
    exif[274] = 6  # orientation: turn 90° clockwise to stand upright
    buffer = io.BytesIO()
    image.save(buffer, format="HEIF", quality=80, exif=exif.tobytes())

    jpeg_bytes = _convert_image_to_jpeg(buffer.getvalue())
    decoded = Image.open(io.BytesIO(jpeg_bytes))
    decoded.load()
    assert decoded.size == (48, 64)


def test_a_photo_that_is_not_a_photo_gets_the_honest_error() -> None:
    async def exercise() -> httpx.Response:
        async with _client(create_app()) as client:
            return await client.post(
                "/api/convert-image",
                content=b"this is not a photo at all",
                headers={**ORIGIN, "content-type": "application/octet-stream"},
            )

    response = asyncio.run(exercise())
    assert response.status_code == 422
    detail = response.json()["detail"]
    message = detail["message"] if isinstance(detail, dict) else detail
    assert "PNG, JPEG, WebP, and HEIC" in message


def test_convert_route_requires_the_octet_stream_content_type() -> None:
    async def exercise() -> httpx.Response:
        async with _client(create_app()) as client:
            return await client.post(
                "/api/convert-image",
                content=b"whatever",
                headers={**ORIGIN, "content-type": "text/plain"},
            )

    response = asyncio.run(exercise())
    assert response.status_code == 415


def test_oversized_declaration_refuses_before_reading_the_body() -> None:
    class _StubRequest:
        def __init__(self) -> None:
            self.headers = {
                "content-type": "application/octet-stream",
                "content-length": str(_MAX_IMAGE_BYTES + 1),
                "origin": "http://testserver",
                "host": "testserver",
            }

    async def exercise() -> None:
        try:
            await _read_image_request(_StubRequest())
        except UiRequestError as error:
            assert error.status_code == 413
            assert _limit_label(_MAX_IMAGE_BYTES) in str(error)
        else:
            raise AssertionError("oversized declaration must refuse with 413")

    asyncio.run(exercise())


def test_convert_image_to_jpeg_round_trips_a_plain_png_too() -> None:
    from PIL import Image

    source = Image.new("RGB", (10, 10), (10, 200, 30))
    buffer = io.BytesIO()
    source.save(buffer, format="PNG")

    jpeg_bytes = _convert_image_to_jpeg(buffer.getvalue())
    decoded = Image.open(io.BytesIO(jpeg_bytes))
    decoded.load()
    assert decoded.format == "JPEG"
    assert decoded.size == (10, 10)
