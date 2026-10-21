"""Keep the same number of waves, saved: step 4 of docs/plan-steady-wave-count.md.

Each weave's switch is an optional key in that weave's own settings, written
only when on and read as true or false, absent meaning off, so every pattern,
print file and project with the switch off keeps the bytes it had.  The
studio's controls carry Weave 1's switch.  A job where any weave holds its
count is the second settings version in all three writers (the page, the
project file and the server), so Clayline 0.8.3 refuses it as newer instead
of half-opening it, and 0.8.3's own reader refuses a held pattern outright.
"""

from __future__ import annotations

import io
import json
import os
import subprocess
import sys
import tarfile
from dataclasses import replace
from pathlib import Path
from typing import Any

import pytest
from test_steady_wave_count import _extra, _wave

import clayline as cl
from clayline.wave import pattern_from_json, pattern_to_json
from clayline.weave_models import Pattern
from clayline.weave_restore import parse_weave_gcode
from clayline.webui.app import (
    _modulate_weave_payload,
    _weave_settings_snapshot,
    weave_settings_schema,
)
from clayline.webui.weave_payload import resolve_pattern

ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "src" / "clayline" / "webui" / "static"
MESH = ROOT / "tests" / "fixtures" / "mesh"
V1 = "clayline.weave-settings.v1"
V2 = "clayline.weave-settings.v2"
HELD = '"hold_wave_count":true'
# The commit that is 0.8.3, the Clayline in /Applications today.
RELEASE_0_8_3 = "26a9e03"
QUIET = {"reproducible": True, "prime_mm": 0.0, "end_early_mm": 0.0}


def _settings_keys(text: str) -> list[set[str]]:
    """Every weave's settings keys, Weave 1 first."""

    payload = json.loads(text)
    return [
        set(payload["settings"]),
        *(set(extra["settings"]) for extra in payload.get("extra_weaves", [])),
    ]


def _without_hold(pattern: Pattern) -> Pattern:
    return replace(
        pattern,
        settings=replace(pattern.settings, hold_wave_count=False),
        extra_weaves=tuple(replace(extra, hold_wave_count=False) for extra in pattern.extra_weaves),
    )


# --- the pattern file -----------------------------------------------------------


def test_off_writes_no_key_and_on_adds_only_its_own() -> None:
    for held in (
        _wave(hold=True),
        _wave(extras=(_extra(hold=True),)),
        _wave(hold=True, extras=(_extra(), _extra(hold=True, wavelength=7.0))),
    ):
        off = pattern_to_json(_without_hold(held))
        assert "hold_wave_count" not in off
        text = pattern_to_json(held)
        # Each held weave adds exactly its switch, and nothing else moves.
        assert text.replace(HELD + ",", "").replace("," + HELD, "") == off
        holding = [held.settings.hold_wave_count, *(e.hold_wave_count for e in held.extra_weaves)]
        assert text.count(HELD) == sum(holding)


def test_each_weaves_switch_round_trips_on_its_own() -> None:
    for one, two, three in (
        (True, False, False),
        (False, True, False),
        (False, False, True),
        (True, True, True),
    ):
        pattern = _wave(
            hold=one, extras=(_extra(hold=two), _extra(hold=three, wavelength=7.0, twist=0.25))
        )
        text = pattern_to_json(pattern)
        assert pattern_from_json(text) == pattern
        assert [("hold_wave_count" in keys) for keys in _settings_keys(text)] == [one, two, three]
        # Written back, the same bytes.
        assert pattern_to_json(pattern_from_json(text)) == text


def test_absent_reads_off_and_only_true_or_false_is_read() -> None:
    assert pattern_from_json(pattern_to_json(_wave())).settings.hold_wave_count is False
    assert pattern_from_json(pattern_to_json(_wave(extras=(_extra(),)))).extra_weaves[0] == (
        _extra()
    )
    for bad in (1, 0, "true", None, [True]):
        one = json.loads(pattern_to_json(_wave()))
        one["settings"]["hold_wave_count"] = bad
        with pytest.raises(ValueError, match=r"^settings\.hold_wave_count must be true or false$"):
            pattern_from_json(json.dumps(one))
        two = json.loads(pattern_to_json(_wave(extras=(_extra(),))))
        two["extra_weaves"][0]["settings"]["hold_wave_count"] = bad
        with pytest.raises(
            ValueError,
            match=r"^extra_weaves\[0\]\.settings\.hold_wave_count must be true or false$",
        ):
            pattern_from_json(json.dumps(two))


def test_a_print_file_carries_each_weaves_switch_back() -> None:
    sliced = cl.load_mesh(MESH / "cylinder.obj").slice(
        layer_height=2.0, sample_spacing=1.0, bead_width=5.0
    )
    for pattern in (
        _wave(wavelength=40.0, hold=True),
        _wave(wavelength=40.0, extras=(_extra(hold=True, wavelength=30.0),)),
    ):
        gcode = sliced.modulate(pattern, reproducible=True).emission.gcode
        assert parse_weave_gcode(gcode).pattern == pattern
    plain = sliced.modulate(_wave(wavelength=40.0), reproducible=True).emission.gcode
    assert "hold_wave_count" not in plain


# --- the studio's controls ---------------------------------------------------------


def test_the_studio_reads_weave_ones_switch_and_leaves_the_others_alone() -> None:
    assert resolve_pattern({"wave": "sine"}).settings.hold_wave_count is False
    assert resolve_pattern({"wave": "sine", "hold_wave_count": None}).settings.hold_wave_count is (
        False
    )
    assert resolve_pattern({"wave": "sine", "hold_wave_count": True}).settings.hold_wave_count
    for bad in (1, "yes"):
        with pytest.raises(ValueError, match=r"^hold_wave_count must be a boolean$"):
            resolve_pattern({"wave": "sine", "hold_wave_count": bad})

    extras = (_extra(hold=True), _extra(wavelength=7.0))
    source = _wave(extras=extras)
    text = pattern_to_json(source)
    held = resolve_pattern({"pattern_json": text, "hold_wave_count": True})
    assert held == replace(source, settings=replace(source.settings, hold_wave_count=True))
    assert held.version == source.version
    # Turning Weave 1's off never turns Weave 2's off.
    back = resolve_pattern({"pattern_json": pattern_to_json(held), "hold_wave_count": False})
    assert back == source and back.extra_weaves == extras


# --- the settings version, in all three writers ----------------------------------


def test_the_server_writes_v2_when_any_weave_holds() -> None:
    assert weave_settings_schema(_wave()) == V1
    assert weave_settings_schema(_wave(hold=True)) == V2
    assert weave_settings_schema(_wave(extras=(_extra(hold=True),))) == V2
    assert weave_settings_schema(_wave(extras=(_extra(),))) == V2

    sliced = cl.load_mesh(MESH / "cylinder.obj").slice(
        layer_height=2.0, sample_spacing=1.0, bead_width=5.0
    )
    for pattern, schema in ((_wave(wavelength=40.0), V1), (_wave(wavelength=40.0, hold=True), V2)):
        request = {"quality": "settle", "pattern_json": pattern_to_json(pattern), **QUIET}
        prepared, _settle = _modulate_weave_payload(sliced, request)
        snapshot = _weave_settings_snapshot(prepared, request)
        assert snapshot["schema"] == schema
        assert pattern_from_json(snapshot["pattern_json"]) == pattern


def _node(script: str, *args: str) -> Any:
    completed = subprocess.run(
        ["node", "-e", script, *args], cwd=ROOT, capture_output=True, text=True, check=False
    )
    if completed.returncode != 0:
        raise AssertionError(f"node refused the script:\n{completed.stderr.strip()}")
    return json.loads(completed.stdout)


def test_the_page_writes_v2_when_any_weave_holds() -> None:
    source = (STATIC / "weave.js").read_text(encoding="utf-8")
    start = source.index('  const WEAVE_SETTINGS_SCHEMA = "clayline.weave-settings.v1";')
    end = source.index("  function weaveSettingsSnapshot() {")
    rule = source[start:end]
    patterns = [
        pattern_to_json(_wave()),
        pattern_to_json(_wave(hold=True)),
        pattern_to_json(_wave(extras=(_extra(hold=True),))),
        pattern_to_json(_wave(extras=(_extra(),))),
    ]
    answers = _node(
        rule
        + """
        const patterns = JSON.parse(process.argv[1]);
        console.log(JSON.stringify(patterns.map(weaveSettingsSchemaFor)));
        """,
        json.dumps(patterns),
    )
    assert answers == [V1, V2, V2, V2]


def test_the_project_file_writes_a_held_job_as_v2_only() -> None:
    held = pattern_to_json(_wave(hold=True))
    one = pattern_to_json(_wave())
    out = _node(
        """
        const codec = require(process.argv[1]);
        const [held, one] = JSON.parse(process.argv[2]);
        const settings = (schema, pattern_json) => ({
          schema, pattern_json, placement: {}, slice: {}, export: {},
        });
        const written = (value) => codec.write({ mode: "weave", settings: value, sources: [] })
          .then(async (blob) => {
            const project = await codec.read(new Uint8Array(await blob.arrayBuffer()));
            return project.settings.schema;
          }, () => "refused");
        (async () => {
          console.log(JSON.stringify([
            await written(settings("clayline.weave-settings.v2", held)),
            await written(settings("clayline.weave-settings.v1", held)),
            await written(settings("clayline.weave-settings.v1", one)),
            await written(settings("clayline.weave-settings.v2", one)),
          ]));
        })();
        """,
        str(STATIC / "project-file.js"),
        json.dumps([held, one]),
    )
    assert out == [V2, "refused", V1, "refused"]


# --- what Clayline 0.8.3 does with a held job ----------------------------------------


@pytest.fixture(scope="module")
def release_0_8_3(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """0.8.3's own source, exported from its commit, or a skip where history is absent."""

    present = subprocess.run(
        ["git", "-C", str(ROOT), "cat-file", "-e", f"{RELEASE_0_8_3}^{{commit}}"],
        capture_output=True,
        check=False,
    )
    if present.returncode != 0:
        pytest.skip(f"this checkout does not hold 0.8.3's commit {RELEASE_0_8_3}")
    archive = subprocess.run(
        ["git", "-C", str(ROOT), "archive", "--format=tar", RELEASE_0_8_3, "src/clayline"],
        capture_output=True,
        check=True,
    ).stdout
    tree = tmp_path_factory.mktemp("clayline-0.8.3")
    with tarfile.open(fileobj=io.BytesIO(archive)) as exported:
        exported.extractall(tree, filter="data")
    return tree


def _run_0_8_3(tree: Path, script: str, *args: str) -> Any:
    completed = subprocess.run(
        [sys.executable, "-c", script, *args],
        cwd=tree,
        env={**os.environ, "PYTHONPATH": str(tree / "src")},
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise AssertionError(f"0.8.3 failed to run:\n{completed.stderr.strip()}")
    return json.loads(completed.stdout)


_READ_WITH_0_8_3 = """
import json, sys
import clayline
from clayline.wave import pattern_from_json
from clayline.weave_restore import parse_weave_gcode
answers = {"source": clayline.__file__}
def answer(read, value):
    try:
        read(value)
        return "opened"
    except ValueError as error:
        return str(error)
answers["patterns"] = [answer(pattern_from_json, text) for text in json.loads(sys.argv[1])]
answers["gcode"] = [
    answer(parse_weave_gcode, open(path, "rb").read()) for path in json.loads(sys.argv[2])
]
print(json.dumps(answers))
"""


def test_0_8_3_refuses_a_held_pattern_and_print_file(release_0_8_3: Path, tmp_path: Path) -> None:
    plain = _wave(wavelength=40.0)
    held = _wave(wavelength=40.0, hold=True)
    sliced = cl.load_mesh(MESH / "cylinder.obj").slice(
        layer_height=2.0, sample_spacing=1.0, bead_width=5.0
    )
    files = []
    for name, pattern in (("plain", plain), ("held", held)):
        path = tmp_path / f"{name}.gcode"
        path.write_bytes(sliced.modulate(pattern, reproducible=True).emission.gcode.encode())
        files.append(str(path))

    out = _run_0_8_3(
        release_0_8_3,
        _READ_WITH_0_8_3,
        json.dumps([pattern_to_json(plain), pattern_to_json(held)]),
        json.dumps(files),
    )
    assert Path(out["source"]).is_relative_to(release_0_8_3)
    refusal = "settings schema mismatch: unknown hold_wave_count"
    assert out["patterns"] == ["opened", refusal]
    assert out["gcode"][0] == "opened"
    assert refusal in out["gcode"][1]


def test_0_8_3s_project_file_answers_a_held_job_as_newer(release_0_8_3: Path) -> None:
    old = release_0_8_3 / "src" / "clayline" / "webui" / "static" / "project-file.js"
    out = _node(
        """
        const now = require(process.argv[1]);
        const old = require(process.argv[2]);
        const [held, one] = JSON.parse(process.argv[3]);
        const settings = (pattern_json) => {
          const value = { pattern_json, placement: {}, slice: {}, export: {} };
          value.schema = pattern_json === held
            ? "clayline.weave-settings.v2" : "clayline.weave-settings.v1";
          return value;
        };
        const opened = async (pattern_json) => {
          const blob = await now.write({ mode: "weave", settings: settings(pattern_json) });
          return old.read(new Uint8Array(await blob.arrayBuffer()))
            .then(() => "opened", (error) => [error.code, error.message]);
        };
        (async () => console.log(JSON.stringify([await opened(one), await opened(held)])))();
        """,
        str(STATIC / "project-file.js"),
        str(old),
        json.dumps([pattern_to_json(_wave(hold=True)), pattern_to_json(_wave())]),
    )
    assert out == [
        "opened",
        [
            "newer-version",
            "This project was saved by a newer Clayline. Update Clayline to open it.",
        ],
    ]
