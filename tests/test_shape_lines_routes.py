"""The two routes the page reaches shape_lines through."""

from __future__ import annotations

import base64
import io
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from PIL import Image, ImageDraw

from clayline import shape_lines
from clayline.webui import app as webui
from clayline.webui.app import SESSION_COOKIE, create_app

SVG_NS = "http://www.w3.org/2000/svg"
FILLED = (
    f'<svg xmlns="{SVG_NS}" width="100mm" height="100mm" viewBox="0 0 100 100">'
    '<rect x="10" y="46" width="80" height="8" fill="#000"/></svg>'
)
LINES = (
    f'<svg xmlns="{SVG_NS}" width="100mm" height="100mm" viewBox="0 0 100 100">'
    '<path d="M1 1 L50 50" fill="none" stroke="#000"/></svg>'
)


@pytest.fixture
def client() -> TestClient:
    return TestClient(create_app())


def painting(answer: dict) -> str:
    """The bar, on a clear canvas, the way the page will send it."""

    width, height = answer["canvas"]["width"], answer["canvas"]["height"]
    picture = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    ImageDraw.Draw(picture).rectangle(
        [width * 0.02, height * 0.3, width * 0.98, height * 0.7], fill=(0, 0, 0, 255)
    )
    out = io.BytesIO()
    picture.save(out, "PNG")
    return base64.b64encode(out.getvalue()).decode()


def test_examine_leaves_a_line_drawing(client: TestClient) -> None:
    response = client.post("/api/svg/examine", json={"svg": LINES})
    assert response.status_code == 200
    assert response.json() == {"verdict": "leave"}


def test_examine_hands_back_a_copy_to_paint(client: TestClient) -> None:
    response = client.post("/api/svg/examine", json={"svg": FILLED})
    assert response.status_code == 200
    answer = response.json()
    assert answer["verdict"] == "convert"
    assert answer["paint_svg"].startswith("<svg")
    assert max(answer["canvas"].values()) == 1000
    assert answer["kept_lines"] == 0


def test_examine_says_when_a_file_is_too_large(client: TestClient) -> None:
    big = LINES.replace("</svg>", f"<desc>{'x' * (8 * 1024 * 1024)}</desc></svg>")
    response = client.post("/api/svg/examine", json={"svg": big})
    assert response.status_code == 200
    assert response.json()["verdict"] == "too_large"


@pytest.mark.parametrize("body", [{}, {"svg": 3}, {"svg": None}])
def test_examine_refuses_a_request_with_no_text(client: TestClient, body: dict) -> None:
    response = client.post("/api/svg/examine", json=body)
    assert response.status_code == 422
    assert "svg" in response.json()["detail"]


def test_make_lines_round_trip(client: TestClient) -> None:
    answer = client.post("/api/svg/examine", json={"svg": FILLED}).json()
    response = client.post(
        "/api/svg/make-lines",
        json={
            "svg": FILLED,
            "png": painting(answer),
            "coil_width_mm": 5.0,
            "join": 0.2,
            "target_mm": 200.0,
            "bed_mm": [381, 381],
        },
    )
    assert response.status_code == 200
    made = response.json()
    assert made["verdict"] == "lines"
    assert made["size_basis"] == "typed"
    assert made["target_mm"] == 200.0
    assert 'id="from-shape-0"' in made["svg"]


def test_make_lines_takes_a_data_url_and_defaults_the_rest(client: TestClient) -> None:
    answer = client.post("/api/svg/examine", json={"svg": FILLED}).json()
    response = client.post(
        "/api/svg/make-lines",
        json={"svg": FILLED, "png": "data:image/png;base64," + painting(answer)},
    )
    assert response.status_code == 200
    assert response.json()["size_basis"] == "authored"


def test_make_lines_answers_for_a_file_that_stays_as_it_is(client: TestClient) -> None:
    response = client.post("/api/svg/make-lines", json={"svg": LINES, "png": ""})
    assert response.status_code == 200
    assert response.json()["verdict"] == "leave"


@pytest.mark.parametrize(
    ("change", "words"),
    [
        pytest.param({"png": None}, "base64", id="no-picture"),
        pytest.param({"png": "!!! not base64 !!!"}, "base64", id="bad-base64"),
        pytest.param(
            {"png": base64.b64encode(b"nope").decode()}, "could not be read", id="not-png"
        ),
        pytest.param({"coil_width_mm": 0}, "coil_width_mm", id="no-coil"),
        pytest.param({"coil_width_mm": "wide"}, "coil_width_mm", id="coil-not-a-number"),
        pytest.param({"join": 1.5}, "join", id="join-too-big"),
        pytest.param({"target_mm": -5}, "target_mm", id="negative-size"),
        pytest.param({"bed_mm": [100]}, "bed_mm", id="one-sided-bed"),
        pytest.param({"bed_mm": [0, 100]}, "bed_mm", id="flat-bed"),
        pytest.param({"bed_mm": [1e9, 1e9]}, "bed_mm", id="bed-past-any-bed"),
        pytest.param({"target_mm": 1_000_000}, "target_mm", id="size-past-any-bed"),
    ],
)
def test_make_lines_refuses_nonsense_clearly(client: TestClient, change: dict, words: str) -> None:
    answer = client.post("/api/svg/examine", json={"svg": FILLED}).json()
    response = client.post(
        "/api/svg/make-lines", json={"svg": FILLED, "png": painting(answer), **change}
    )
    assert response.status_code == 422
    assert words in str(response.json()["detail"])


def test_a_painting_of_the_wrong_size_is_refused_clearly(client: TestClient) -> None:
    out = io.BytesIO()
    Image.new("RGBA", (7, 7)).save(out, "PNG")
    response = client.post(
        "/api/svg/make-lines",
        json={"svg": FILLED, "png": base64.b64encode(out.getvalue()).decode()},
    )
    assert response.status_code == 422
    assert "(7, 7)" in response.json()["detail"]


@pytest.mark.parametrize("route", ["/api/svg/examine", "/api/svg/make-lines"])
def test_routes_ask_for_json(client: TestClient, route: str) -> None:
    response = client.post(route, content=FILLED, headers={"Content-Type": "image/svg+xml"})
    assert response.status_code == 415


@pytest.mark.parametrize("route", ["/api/svg/examine", "/api/svg/make-lines"])
def test_routes_need_the_desktop_session_and_origin(route: str) -> None:
    origin = "http://127.0.0.1:9999"
    client = TestClient(create_app(desktop_token="token", desktop_origin=origin))
    body = {"svg": LINES, "png": ""}
    assert client.post(route, json=body).status_code in {401, 403}
    client.cookies.set(SESSION_COOKIE, "token")
    assert client.post(route, json=body, headers={"Origin": "http://evil.test"}).status_code == 403
    assert client.post(route, json=body, headers={"Origin": origin}).status_code == 200


def test_the_work_holds_the_lock(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    seen: list[bool] = []
    real = shape_lines.examine

    def watched(text: str) -> dict:
        seen.append(webui._SHAPE_LINES_LOCK.locked())
        return real(text)

    monkeypatch.setattr(shape_lines, "examine", watched)
    with ThreadPoolExecutor(2) as pool:
        answers = list(
            pool.map(lambda _: client.post("/api/svg/examine", json={"svg": LINES}), range(4))
        )
    assert all(answer.status_code == 200 for answer in answers)
    assert seen == [True, True, True, True]
    assert not webui._SHAPE_LINES_LOCK.locked()


def test_only_the_routes_reach_shape_lines() -> None:
    src = Path(webui.__file__).resolve().parents[1]
    reaching = [
        path.relative_to(src).as_posix()
        for path in src.rglob("*.py")
        if "shape_lines" in path.read_text(encoding="utf-8")
    ]
    assert reaching == ["webui/app.py"]


@pytest.mark.parametrize("view", ["0 0 0 0", "0 0 0 100", "0 0 100 0"], ids=str)
@pytest.mark.parametrize(
    "body",
    ['<path d="M1 1L9 9" stroke="#000" fill="none"/>', '<rect width="9" height="9" fill="#000"/>'],
    ids=["lines", "filled"],
)
def test_a_view_with_no_size_is_an_answer_not_an_error(
    client: TestClient, view: str, body: str
) -> None:
    text = f'<svg xmlns="{SVG_NS}" viewBox="{view}">{body}</svg>'
    for route, extra in (("/api/svg/examine", {}), ("/api/svg/make-lines", {"png": ""})):
        response = client.post(route, json={"svg": text, **extra})
        assert response.status_code == 200
        assert response.json()["verdict"] == "leave"
        assert response.json()["sentence"] == "This file has nothing to draw."


@pytest.mark.parametrize(
    ("name", "route", "extra"),
    [
        ("_read_page", "/api/svg/examine", {}),
        ("_read_page", "/api/svg/make-lines", {"png": ""}),
        ("examine", "/api/svg/examine", {}),
        ("make_lines", "/api/svg/make-lines", {"png": ""}),
    ],
)
def test_a_failure_reaches_the_page_in_words_never_as_a_crash(
    client: TestClient, monkeypatch: pytest.MonkeyPatch, name: str, route: str, extra: dict
) -> None:
    def trip(*_: object, **__: object) -> None:
        raise ZeroDivisionError("float division by zero")

    monkeypatch.setattr(shape_lines, name, trip)
    response = client.post(route, json={"svg": FILLED, **extra})
    assert response.status_code == 422
    assert response.json()["detail"] == "Clayline couldn't make lines from this drawing."
    assert not webui._SHAPE_LINES_LOCK.locked()


@pytest.mark.parametrize(
    "settings",
    [
        pytest.param({}, id="plain"),
        pytest.param(
            {
                "draw_schema_version": 2,
                "scale": None,
                "page_mode": "stack",
                "joint_boost": 0.0,
                "reproducible": True,
            },
            id="pass-rows",
        ),
    ],
)
def test_a_slice_of_a_drawing_too_short_to_print_comes_back_in_words(
    client: TestClient, settings: dict
) -> None:
    text = (
        f'<svg xmlns="{SVG_NS}" width="13mm" height="11mm" viewBox="0 0 13 11">'
        '<path d="M5 5.2L8 5" fill="none" stroke="#000"/></svg>'
    )
    response = client.post(
        "/api/slice",
        json={"files": [{"name": "short.svg", "svg": text}], "layers": 1, **settings},
    )
    assert response.status_code == 422
    assert "too short to print" in response.json()["detail"]
