"""Upload image opens real images (docs/plan-mesh-mode-fixes.md, section 1).

Pete: "what files is the images feature in mesh mode supposed to open? Shouldn't
it be able to open png, jpg, tiff, and psd?"

Every picture here is made in the test. Pillow cannot write a Photoshop file, so
those are written out byte by byte from Adobe's published layout; the HEIC is
the committed sample, because the engine's HEIC library only reads.
"""

from __future__ import annotations

import asyncio
import base64
import io
import json
import struct
import zlib
from pathlib import Path

import httpx
import numpy as np
import pytest
import trimesh
from PIL import Image
from weave_page_rig import run_page

import clayline.webui.app as studio
from clayline.image_relief import (
    MAX_SOURCE_BYTES,
    PHOTOSHOP_UNREADABLE,
    PHOTOSHOP_WITHOUT_PICTURE,
    SOURCE_TOO_LARGE,
    SOURCE_TOO_MANY_PIXELS,
    SOURCE_UNREADABLE,
    ImageEffect,
    _source_data,
    image_info,
)

ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "src" / "clayline" / "webui" / "static"
PHOTOS = Path(__file__).parent / "fixtures" / "photo"
ORIGIN = {"origin": "http://testserver", "host": "testserver"}

_LEFT_LIGHT = np.zeros((8, 12), dtype=np.uint8)
_LEFT_LIGHT[:, :6] = 255


def _b64(raw: bytes) -> str:
    return base64.b64encode(raw).decode("ascii")


def _relief(raw: bytes) -> np.ndarray:
    relief, _alpha = _source_data(None, _b64(raw))
    return relief


def _saved(image: Image.Image, fmt: str, **options: object) -> bytes:
    stream = io.BytesIO()
    image.save(stream, format=fmt, **options)
    return stream.getvalue()


def _assert_left_pushes_out_right_pulls_in(relief: np.ndarray) -> None:
    assert relief.shape == (8, 12)
    assert relief[:, :4].mean() == pytest.approx(1.0, abs=0.05)
    assert relief[:, 8:].mean() == pytest.approx(-1.0, abs=0.05)


@pytest.mark.parametrize(
    ("fmt", "options"),
    [
        ("PNG", {}),
        ("JPEG", {"quality": 100, "subsampling": 0}),
        ("TIFF", {}),
        ("WEBP", {"lossless": True}),
        ("BMP", {}),
    ],
)
def test_each_format_pillow_can_write_shapes_the_wall_the_same_way(
    fmt: str, options: dict[str, object]
) -> None:
    picture = Image.fromarray(_LEFT_LIGHT).convert("RGB")
    _assert_left_pushes_out_right_pulls_in(_relief(_saved(picture, fmt, **options)))


def test_a_heic_photo_shapes_the_wall() -> None:
    pytest.importorskip("pi_heif")
    raw = (PHOTOS / "solid-64x48.heic").read_bytes()
    effect = ImageEffect(data_base64=_b64(raw), name="photo.heic")
    assert image_info(effect)["width"] == 64
    assert image_info(effect)["height"] == 48


# ---------------------------------------------------------------- TIFF
@pytest.mark.parametrize("dtype", ["<u2", ">u2"])
def test_a_16_bit_gray_tiff_keeps_its_full_range(dtype: str) -> None:
    values = np.array([[0, 32768, 65535, 49152]], dtype=dtype)
    relief = _relief(_saved(Image.fromarray(values), "TIFF"))
    assert relief[0, 0] == pytest.approx(-1.0)
    assert relief[0, 1] == pytest.approx(0.0)
    assert relief[0, 2] == pytest.approx(1.0)
    # 8 bits could not say this: halfway up the top half, exactly.
    assert relief[0, 3] == pytest.approx(16384 / 32767, abs=1e-4)


def _rgb16_tiff(pixels: np.ndarray) -> bytes:
    """A little-endian 16-bit-a-channel RGB TIFF, which is what Photoshop saves."""
    height, width, _channels = pixels.shape
    data = pixels.astype("<u2").tobytes()
    data_at = 8
    bits_at = data_at + len(data)
    ifd_at = bits_at + 6
    entries = [
        (256, 3, 1, width),
        (257, 3, 1, height),
        (258, 3, 3, bits_at),
        (259, 3, 1, 1),
        (262, 3, 1, 2),
        (273, 4, 1, data_at),
        (277, 3, 1, 3),
        (278, 3, 1, height),
        (279, 4, 1, len(data)),
        (284, 3, 1, 1),
    ]
    ifd = struct.pack("<H", len(entries))
    for tag, kind, count, value in entries:
        ifd += struct.pack("<HHII", tag, kind, count, value)
    ifd += struct.pack("<I", 0)
    return b"II*\0" + struct.pack("<I", ifd_at) + data + struct.pack("<3H", 16, 16, 16) + ifd


def test_a_16_bit_color_tiff_shapes_the_wall() -> None:
    pixels = np.zeros((8, 12, 3), dtype=np.uint16)
    pixels[:, :6] = 65535
    _assert_left_pushes_out_right_pulls_in(_relief(_rgb16_tiff(pixels)))


@pytest.mark.parametrize("fmt", ["TIFF", "JPEG"])
def test_a_cmyk_picture_shapes_the_wall(fmt: str) -> None:
    # In CMYK, no ink is white and full black ink is dark.
    pixels = np.zeros((8, 12, 4), dtype=np.uint8)
    pixels[:, 6:, 3] = 255
    picture = Image.fromarray(pixels, mode="CMYK")
    options = {"quality": 100, "subsampling": 0} if fmt == "JPEG" else {}
    relief = _relief(_saved(picture, fmt, **options))
    assert relief[:, :4].mean() > 0.9
    assert relief[:, 8:].mean() < -0.9


# ---------------------------------------------------------------- Photoshop
def _psd(
    pixels: np.ndarray,
    *,
    layers: int = 0,
    real_merged_data: bool | None = None,
    depth: int = 8,
    mode: int | None = None,
) -> bytes:
    """A Photoshop file: the flattened picture, plus layer records if asked.

    A negative layer count is Photoshop's mark that the fourth channel is the
    merged picture's transparency.
    """
    height, width = pixels.shape[:2]
    channels = 1 if pixels.ndim == 2 else pixels.shape[2]
    mode = mode if mode is not None else (1 if channels == 1 else 3)
    out = b"8BPS" + struct.pack(">H", 1) + b"\0" * 6
    out += struct.pack(">HIIHH", channels, height, width, depth, mode)
    out += struct.pack(">I", 0)  # no colour table

    resources = b""
    if real_merged_data is not None:
        version_info = struct.pack(">I", 1) + bytes([1 if real_merged_data else 0])
        version_info += struct.pack(">II", 0, 0) + struct.pack(">I", 1)
        if len(version_info) % 2:
            version_info += b"\0"
        resources = b"8BIM" + struct.pack(">H", 1057) + b"\0\0"
        resources += struct.pack(">I", len(version_info)) + version_info
    out += struct.pack(">I", len(resources)) + resources

    if layers:
        records = b""
        for index in range(abs(layers)):
            name = f"Layer {index}".encode("ascii")
            padded = bytes([len(name)]) + name
            padded += b"\0" * (-len(padded) % 4)
            extra = struct.pack(">I", 0) + struct.pack(">I", 0) + padded
            records += struct.pack(">iiii", 0, 0, height, width)
            records += struct.pack(">H", 1) + struct.pack(">hI", 0, 2 + width * height)
            records += b"8BIM" + b"norm" + bytes([255, 0, 0, 0])
            records += struct.pack(">I", len(extra)) + extra
        channel_data = b"".join(
            struct.pack(">H", 0) + bytes(width * height) for _index in range(abs(layers))
        )
        info = struct.pack(">h", layers) + records + channel_data
        if len(info) % 2:
            info += b"\0"
        section = struct.pack(">I", len(info)) + info
        out += struct.pack(">I", len(section)) + section
    else:
        out += struct.pack(">I", 0)

    out += struct.pack(">H", 0)  # raw, not packed
    planes = pixels if pixels.ndim == 3 else pixels[:, :, None]
    for channel in range(channels):
        out += planes[:, :, channel].astype(">u2" if depth == 16 else np.uint8).tobytes()
    return out


def _rgb(gray: np.ndarray) -> np.ndarray:
    return np.stack([gray, gray, gray], axis=2)


@pytest.mark.parametrize("real_merged_data", [None, True])
@pytest.mark.parametrize("layers", [0, 2])
def test_a_photoshop_file_gives_its_flattened_picture(
    layers: int, real_merged_data: bool | None
) -> None:
    raw = _psd(_rgb(_LEFT_LIGHT), layers=layers, real_merged_data=real_merged_data)
    assert Image.open(io.BytesIO(raw)).format == "PSD"
    _assert_left_pushes_out_right_pulls_in(_relief(raw))


def test_a_gray_photoshop_file_gives_its_flattened_picture() -> None:
    _assert_left_pushes_out_right_pulls_in(_relief(_psd(_LEFT_LIGHT)))


def test_a_layered_photoshop_file_with_a_blank_picture_says_how_to_save_it() -> None:
    blank = np.full((8, 12, 3), 255, dtype=np.uint8)
    with pytest.raises(ValueError) as refused:
        _relief(_psd(blank, layers=2))
    assert str(refused.value) == PHOTOSHOP_WITHOUT_PICTURE
    assert str(refused.value) == (
        "This Photoshop file was saved without its flattened picture. "
        "Save it again with Maximize Compatibility on."
    )


def test_a_layered_photoshop_file_that_says_its_picture_is_not_real_is_told_the_same() -> None:
    # Older Photoshop writes words into the placeholder, so it is not one colour.
    with pytest.raises(ValueError, match="Maximize Compatibility"):
        _relief(_psd(_rgb(_LEFT_LIGHT), layers=1, real_merged_data=False))


def test_a_layered_one_colour_file_that_says_its_picture_is_real_opens() -> None:
    # Re-saving could never answer a refusal here: the picture really is one colour.
    gray = np.full((8, 12, 3), 128, dtype=np.uint8)
    relief = _relief(_psd(gray, layers=1, real_merged_data=True))
    assert np.abs(relief).max() == pytest.approx(0.0)


def test_a_plain_one_colour_photoshop_file_with_no_layers_is_a_real_picture() -> None:
    relief = _relief(_psd(np.full((8, 12), 128, dtype=np.uint8)))
    assert np.abs(relief).max() == pytest.approx(0.0)


def _with_fourth_channel(gray: np.ndarray, fourth: np.ndarray) -> np.ndarray:
    return np.stack([gray, gray, gray, fourth], axis=2)


@pytest.mark.parametrize("layers", [0, 2])
def test_a_saved_selection_is_not_transparency(layers: int) -> None:
    # The fourth channel here says nothing is selected. Read as transparency it
    # would leave a blank wall and no message.
    raw = _psd(_with_fourth_channel(_LEFT_LIGHT, np.zeros((8, 12), np.uint8)), layers=layers)
    relief, alpha = _source_data(None, _b64(raw))
    _assert_left_pushes_out_right_pulls_in(relief)
    assert alpha.min() == 1.0


def test_a_negative_layer_count_makes_the_fourth_channel_transparency() -> None:
    fourth = np.zeros((8, 12), np.uint8)
    fourth[:, 3:] = 255
    relief, alpha = _source_data(
        None, _b64(_psd(_with_fourth_channel(_LEFT_LIGHT, fourth), layers=-2))
    )
    assert alpha[:, :3].max() == 0.0
    assert alpha[:, 3:].min() == 1.0
    # Where it is see-through, the wall is left alone.
    assert np.abs(relief[:, :3]).max() == 0.0
    assert relief[:, 3:6].min() == pytest.approx(1.0, abs=0.05)
    assert relief[:, 6:].max() == pytest.approx(-1.0, abs=0.05)


def test_a_saved_selection_does_not_hide_a_blank_placeholder() -> None:
    # A busy selection on a layered file's one-colour placeholder is still that placeholder.
    busy = np.zeros((8, 12), np.uint8)
    busy[:, 6:] = 255
    blank = np.full((8, 12), 255, dtype=np.uint8)
    with pytest.raises(ValueError) as refused:
        _relief(_psd(_with_fourth_channel(blank, busy), layers=2))
    assert str(refused.value) == PHOTOSHOP_WITHOUT_PICTURE


def test_real_transparency_on_one_colour_is_a_picture() -> None:
    busy = np.zeros((8, 12), np.uint8)
    busy[:, 6:] = 255
    blank = np.full((8, 12), 255, dtype=np.uint8)
    relief = _relief(_psd(_with_fourth_channel(blank, busy), layers=-2))
    assert relief[:, 6:].min() == pytest.approx(1.0, abs=0.05)
    assert np.abs(relief[:, :6]).max() == 0.0


def test_a_16_bit_photoshop_file_is_refused_in_plain_words() -> None:
    pixels = np.full((8, 12), 1000, dtype=np.uint16)
    with pytest.raises(ValueError) as refused:
        _relief(_psd(pixels, depth=16))
    assert str(refused.value) == PHOTOSHOP_UNREADABLE


# ---------------------------------------------------------------- limits
def _png_header_only(width: int, height: int) -> bytes:
    ihdr = b"IHDR" + struct.pack(">IIBBBBB", width, height, 8, 0, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + struct.pack(">I", 13)
        + ihdr
        + struct.pack(">I", zlib.crc32(ihdr))
        + struct.pack(">I", 0)
        + b"IDAT"
        + struct.pack(">I", zlib.crc32(b"IDAT"))
    )


@pytest.mark.parametrize("size", [(4097, 4096), (20000, 20000)])
def test_too_many_pixels_keeps_its_existing_words_however_many(size: tuple[int, int]) -> None:
    with pytest.raises(ValueError) as refused:
        _relief(_png_header_only(*size))
    assert str(refused.value) == SOURCE_TOO_MANY_PIXELS
    assert str(refused.value) == "Choose an image with at most 16 million pixels"


def test_too_many_bytes_keeps_its_existing_words() -> None:
    with pytest.raises(ValueError) as refused:
        ImageEffect(data_base64=_b64(bytes(MAX_SOURCE_BYTES + 1)))
    assert str(refused.value) == SOURCE_TOO_LARGE
    assert str(refused.value) == "Image artwork must be no larger than 17 MB"
    assert MAX_SOURCE_BYTES == 17 * 1024 * 1024


@pytest.mark.parametrize(
    "raw",
    [
        b"this is no picture at all",
        _saved(Image.fromarray(_LEFT_LIGHT), "TIFF")[:40],
        _saved(Image.fromarray(_LEFT_LIGHT), "PNG")[:30],
    ],
)
def test_a_file_that_is_no_picture_names_what_the_panel_offers(raw: bytes) -> None:
    with pytest.raises(ValueError) as refused:
        _relief(raw)
    assert str(refused.value) == SOURCE_UNREADABLE
    for name in ("PNG", "JPEG", "TIFF", "WebP", "BMP", "HEIC", "Photoshop"):
        assert name in str(refused.value)


@pytest.mark.parametrize("keep", [4, 10, 24, 30, 60, 200, -1])
def test_a_cut_short_photoshop_file_gets_the_unreadable_sentence(keep: int) -> None:
    # Saving at 8 bits is no advice for a file that is already 8 bits and damaged.
    raw = _psd(_rgb(_LEFT_LIGHT))
    with pytest.raises(ValueError) as refused:
        _relief(raw[:keep])
    assert str(refused.value) == SOURCE_UNREADABLE


def test_a_cut_short_16_bit_photoshop_file_still_gets_the_8_bit_sentence() -> None:
    raw = _psd(np.full((8, 12), 1000, dtype=np.uint16), depth=16)
    with pytest.raises(ValueError) as refused:
        _relief(raw[:60])
    assert str(refused.value) == PHOTOSHOP_UNREADABLE


# ---------------------------------------------------------------- the route
def _post(body: bytes) -> httpx.Response:
    async def exercise() -> httpx.Response:
        transport = httpx.ASGITransport(app=studio.create_app())
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            return await client.post(
                "/api/images/upload",
                content=body,
                headers={**ORIGIN, "content-type": "application/json"},
            )

    return asyncio.run(exercise())


def _upload(raw: bytes, name: str) -> httpx.Response:
    return _post(json.dumps({"name": name, "data_base64": _b64(raw)}).encode("utf-8"))


def test_the_route_takes_a_photoshop_file_and_keeps_its_bytes() -> None:
    raw = _psd(_rgb(_LEFT_LIGHT), layers=1, real_merged_data=True)
    response = _upload(raw, "relief.psd")
    assert response.status_code == 200, response.text
    assert base64.b64decode(response.json()["image"]["data_base64"]) == raw
    assert response.json()["image"]["name"] == "relief.psd"
    assert response.json()["info"]["width"] == 12


def test_the_route_says_the_maximize_compatibility_line() -> None:
    response = _upload(_psd(np.full((8, 12, 3), 255, dtype=np.uint8), layers=2), "blank.psd")
    assert response.status_code == 422
    assert response.json()["detail"] == PHOTOSHOP_WITHOUT_PICTURE


def _refused_as_unreadable(response: httpx.Response) -> None:
    assert response.status_code == 422
    assert response.json()["detail"] == SOURCE_UNREADABLE


def test_a_zero_byte_file_is_refused_not_opened_blank() -> None:
    _refused_as_unreadable(_upload(b"", "empty.png"))
    # The page sends no data at all for a file its reader finds empty.
    _refused_as_unreadable(_post(json.dumps({"name": "empty.png"}).encode("utf-8")))


def test_a_lab_photoshop_file_is_refused_not_opened_blank() -> None:
    gray = np.full((8, 12), 128, dtype=np.uint8)
    lab = _psd(np.stack([_LEFT_LIGHT, gray, gray], axis=2), mode=9)
    assert Image.open(io.BytesIO(lab)).mode == "LAB"
    _refused_as_unreadable(_upload(lab, "lab.psd"))


def test_a_picture_all_see_through_is_refused_not_opened_blank() -> None:
    clear = Image.new("RGBA", (12, 8), (255, 255, 255, 0))
    _refused_as_unreadable(_upload(_saved(clear, "PNG"), "clear.png"))
    # A saved pattern that holds one still opens, as it always did.
    assert image_info(ImageEffect(data_base64=_b64(_saved(clear, "PNG"))))["width"] == 12


def test_a_real_one_colour_picture_is_not_blank() -> None:
    gray = Image.new("L", (12, 8), 128)
    assert _upload(_saved(gray, "PNG"), "plain.png").status_code == 200
    assert _upload(_psd(np.full((8, 12), 128, dtype=np.uint8)), "plain.psd").status_code == 200


def _photoshop_file_of(size: int) -> bytes:
    """A small picture in a file of exactly this many bytes, the rest unused."""
    picture = _psd(_rgb(_LEFT_LIGHT))
    padding = size - len(picture) - 4
    assert padding >= 0 and padding % 2 == 0
    # Where an empty layer section's length sits: after the header and two empty lengths.
    at = 26 + 4 + 4
    section = struct.pack(">I", 4 + padding) + struct.pack(">I", 0) + bytes(padding)
    return picture[:at] + section + picture[at + 4 :]


@pytest.mark.parametrize(
    "size",
    [
        # The size of the real file that was turned down.
        17_025_188,
        MAX_SOURCE_BYTES - (MAX_SOURCE_BYTES % 2),
    ],
)
def test_a_photoshop_file_of_ordinary_size_opens(size: int) -> None:
    raw = _photoshop_file_of(size)
    assert len(raw) == size
    response = _upload(raw, "relief.psd")
    assert response.status_code == 200, response.text[:200]
    assert response.json()["info"]["width"] == 12
    assert base64.b64decode(response.json()["image"]["data_base64"]) == raw


def test_a_file_just_over_the_limit_gets_the_plain_message() -> None:
    # It still fits the request limit, so it is the file limit that answers.
    response = _upload(_photoshop_file_of(MAX_SOURCE_BYTES + 2), "huge.psd")
    assert response.status_code == 422
    assert response.json()["detail"] == "Image artwork must be no larger than 17 MB"


def _base64_size(size: int) -> int:
    return (size + 2) // 3 * 4


def test_three_files_at_the_limit_fit_a_request_and_a_saved_project() -> None:
    # Over these, the page's headline is the request limit's own line and a saved
    # project will not open again.
    three = 3 * _base64_size(MAX_SOURCE_BYTES)
    project_file = (STATIC / "project-file.js").read_text(encoding="utf-8")
    assert "const MAX_MANIFEST_BYTES = 72 * 1024 * 1024;" in project_file
    # Nothing else was raised to fit them.
    assert studio._MAX_REQUEST_BYTES == 72 * 1024 * 1024
    assert three < studio._MAX_REQUEST_BYTES
    # A megabyte more each fills the limit with no room for what goes along with them.
    assert 3 * _base64_size(MAX_SOURCE_BYTES + 1024 * 1024) >= studio._MAX_REQUEST_BYTES


def test_what_travels_with_three_pictures_leaves_them_room_at_the_limit() -> None:
    # Three small pictures, one copy each, in everything the page sends or saves:
    # what goes along with them is measured, and three at the limit still fit.
    picture = _b64(_psd(_rgb(_LEFT_LIGHT)))
    box = _b64(trimesh.creation.box((40, 40, 20)).export(file_type="obj").encode("utf-8"))
    result = run_page(
        f"const PICTURE = {json.dumps(picture)};\nconst BOX = {json.dumps(box)};\n"
        + _ADD_AND_STUB_READER
        + r"""
  for (let i = 0; i < 3; i += 1) {
    if (i) { click("#weaveAddImage"); await settle(1000); }
    await pick({ name: `relief${i}.psd`, size: 10, base64: PICTURE });
  }
  weaveMode.importMesh({ name: "box.obj", base64: BOX });
  await settle(1000);
  click("#weaveSettleButton");
  await settle(5000);
  const measure = (text) => ({
    copies: text.split(PICTURE).length - 1,
    rest: text.length - (text.split(PICTURE).length - 1) * PICTURE.length,
  });
  out.requests = {};
  for (const path of ["/api/weave/slice", "/api/weave/modulate", "/api/weave/pattern"]) {
    const sent = requests.filter((request) => request.url.split("?")[0] === path);
    out.requests[path] = measure(sent[sent.length - 1].body);
  }
  const blob = await codec.write({
    mode: "weave", settings: page.weaveSettingsSnapshot(), state: { sliced: true }, sources: [],
  });
  const archive = await codec.zip.read(new Uint8Array(await blob.arrayBuffer()));
  out.project = measure(new TextDecoder().decode(await archive.bytes("project.json")));
"""
    )
    assert result["project"]["copies"] == 3
    assert result["requests"]["/api/weave/modulate"]["copies"] == 3
    measured = [*result["requests"].values(), result["project"]]
    for seen in measured:
        assert seen["copies"] <= 3
        at_the_limit = seen["copies"] * _base64_size(MAX_SOURCE_BYTES) + seen["rest"]
        assert at_the_limit < studio._MAX_REQUEST_BYTES


def test_the_page_tooltip_and_guide_say_the_engines_number() -> None:
    weave = (STATIC / "weave.js").read_text(encoding="utf-8")
    assert "const IMAGE_UPLOAD_MAX_BYTES = 17 * 1024 * 1024;" in weave
    assert f'const IMAGE_TOO_LARGE = "{SOURCE_TOO_LARGE}";' in weave
    assert "up to 17 MB and 16 million pixels" in (STATIC / "index.html").read_text("utf-8")
    assert "to 17 MB and 16 million pixels" in (ROOT / "guide" / "weave.md").read_text("utf-8")


def test_a_request_over_the_limit_gets_a_plain_message(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(studio, "_MAX_REQUEST_BYTES", 1024)
    response = _post(b'{"data_base64": "' + b"A" * 4096 + b'"}')
    assert response.status_code == 413
    assert response.json()["detail"] == SOURCE_TOO_LARGE
    assert "request" not in response.json()["detail"]


# ---------------------------------------------------------------- the page
_ADD_AND_STUB_READER = r"""
  globalThis.Image = class { set src(_value) { queueMicrotask(() => this.onload?.()); } };
  click("#weaveAddImage"); await settle(1000);
  globalThis.FileReader = class {
    readAsDataURL(file) {
      this.result = `data:application/octet-stream;base64,${file.base64 || ""}`;
      queueMicrotask(() => this.onload?.());
    }
  };
  const pick = async (file) => {
    const input = $("#weaveImageFile");
    input.files = [file];
    input.dispatchEvent(new Event("change", { bubbles: true }));
    await settle(1000);
    return $("#weaveImageSourceHint").textContent;
  };
  const uploads = () => requests.filter((request) => request.url.includes("/api/images/upload"));
"""


def test_upload_image_stamps_its_own_picker_kind_right_before_the_click() -> None:
    result = run_page(
        _ADD_AND_STUB_READER
        + r"""
  let stamped = null;
  $("#weaveImageFile").click = () => { stamped = document.body.dataset.claylineFileRequest; };
  click("#weaveImageUpload");
  out.stamped = stamped;
"""
    )
    assert result["stamped"] == "image"


def test_the_browser_accept_list_and_the_tooltip_name_the_same_formats() -> None:
    html = (STATIC / "index.html").read_text(encoding="utf-8")
    start = html.index('id="weaveImageFile"')
    accept = html[start : html.index(">", start)]
    for token in (
        "image/png",
        "image/jpeg",
        "image/tiff",
        "image/webp",
        "image/bmp",
        "image/heic",
        "image/heif",
        "image/vnd.adobe.photoshop",
        ".psd",
        ".tif",
        ".tiff",
        ".heic",
    ):
        assert token in accept
    start = html.index('id="weaveImageUpload"')
    tooltip = html[start : html.index(">", start)]
    for name in ("PNG", "JPEG", "TIFF", "WebP", "BMP", "HEIC", "Photoshop"):
        assert name in tooltip


def test_a_file_over_the_limit_is_turned_down_before_it_is_read_or_sent() -> None:
    result = run_page(
        _ADD_AND_STUB_READER
        + r"""
  let read = 0;
  const reader = globalThis.FileReader;
  globalThis.FileReader = class extends reader {
    readAsDataURL(file) { read += 1; super.readAsDataURL(file); }
  };
  out.hint = await pick({ name: "huge.psd", size: 17 * 1024 * 1024 + 1, base64: "" });
  out.read = read;
  out.sent = uploads().length;
"""
    )
    assert result["hint"] == SOURCE_TOO_LARGE
    assert result["read"] == 0
    assert result["sent"] == 0


def test_a_zero_byte_file_is_told_it_could_not_be_read_on_the_page() -> None:
    result = run_page(
        _ADD_AND_STUB_READER
        + r"""
  out.hint = await pick({ name: "empty.png", size: 0, base64: "" });
  out.image = page.patternObject().images[0].data_base64;
  out.sent = uploads().length;
"""
    )
    assert result["hint"] == SOURCE_UNREADABLE
    assert result["image"] is None
    assert result["sent"] == 1


def test_the_engines_refusals_reach_the_potter_as_written() -> None:
    blank = _psd(np.full((8, 12, 3), 255, dtype=np.uint8), layers=2)
    good = _psd(_rgb(_LEFT_LIGHT), layers=1)
    head = f"const BLANK = {json.dumps(_b64(blank))};\nconst GOOD = {json.dumps(_b64(good))};\n"
    result = run_page(
        head
        + _ADD_AND_STUB_READER
        + r"""
  out.blank = await pick({ name: "blank.psd", size: 10, base64: BLANK });
  out.blankImage = page.patternObject().images[0].data_base64;
  out.good = await pick({ name: "relief.psd", size: 10, base64: GOOD });
  out.goodName = page.patternObject().images[0].name;
  out.goodImage = page.patternObject().images[0].data_base64 === GOOD;
"""
    )
    assert result["blank"] == PHOTOSHOP_WITHOUT_PICTURE
    assert result["blankImage"] is None
    assert result["goodName"] == "relief.psd"
    assert result["goodImage"] is True
    assert result["good"] != PHOTOSHOP_WITHOUT_PICTURE
