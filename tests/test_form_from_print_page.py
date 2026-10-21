"""A print file brings back its form: the studio page (Round 1).

docs/plan-form-from-print-file.md, "Studio page" and "What the potter reads".
A print file Clayline saved, dropped with no model on the table, brings every
setting back at once and then its form: the printed surface itself, placed
where it printed, with every weave off. The model it names can be chosen in
its place and goes where the file printed it, weaves back on.

The page runs whole under node against the studio app (tests/weave_page_rig.py);
every print here is made by the real pipeline from a repo fixture.
"""

from __future__ import annotations

import base64
import json
from dataclasses import replace
from functools import cache
from pathlib import Path
from typing import Any

from weave_page_rig import run_page

import clayline as cl
from clayline.weave_models import ExtraWeave

MESH = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "mesh"

LINE = "Form is {}'s printed surface, pattern and all."
HINT = (
    "Weaves are off: this form already carries the pattern. "
    "Choose cylinder.obj under 01 Form and they come back on."
)
HINT_TIP = "Switching a weave on here lays it over the pattern already in the surface."
# Detail only: the line under the name says what the form is.
NAME_TIP = "Made at the size and angle it printed; it holds only the layers that printed."


def _three_weaves() -> cl.Pattern:
    # Weave 3 switched off, as on TacoTrayD: the swap puts it back off.
    return replace(
        cl.preset_pattern("sine"),
        extra_weaves=(
            ExtraWeave(amplitude=1.0, wavelength=12.0, twist=0.1),
            ExtraWeave(amplitude=0.5, wavelength=30.0, wave_on=False),
        ),
    )


def _print(
    mesh: Path = MESH / "cylinder.obj",
    *,
    pattern: Any = "sine",
    scale: float = 1.0,
    rotation_deg: float = 0.0,
    top_layer: str | None = None,
    **modulate: Any,
) -> str:
    slice_options: dict[str, Any] = {"layer_height": 5.0}
    if top_layer is not None:
        slice_options["top_layer"] = top_layer
    return (
        cl.load_mesh(mesh, up="z", scale=scale, rotation_deg=rotation_deg)
        .slice(**slice_options)
        .modulate(
            pattern,
            reproducible=True,
            prime_mm=0.0,
            end_early_mm=0.0,
            job_id="form-page",
            **{"amplitude": 2.0, "wavelength": 18.0, **modulate},
        )
        .emission.gcode
    )


@cache
def _swap_print() -> str:
    """Placed, ranged and topped so the swap has something to put back."""

    return _print(
        pattern=_three_weaves(),
        scale=1.2,
        rotation_deg=15.0,
        top_layer="below",
        layer_range=(2, 5),
        bottom_layers=0,
    )


def _b64(data: str | bytes) -> str:
    raw = data.encode("utf-8") if isinstance(data, str) else data
    return base64.b64encode(raw).decode("ascii")


# Shared by every script: the form request can be held while the test acts
# during the wait, and the page's state read the way the potter sees it.
_HELPERS = r"""
  const realFetch = window.fetch;
  let holding = false;
  let releaseForm = null;
  window.fetch = (url, init) => {
    if (holding && String(url).startsWith("/api/weave/restore/form")) {
      return new Promise((resolve) => { releaseForm = () => resolve(realFetch(url, init)); });
    }
    return realFetch(url, init);
  };
  const hold = () => { holding = true; };
  const release = async () => {
    holding = false;
    const go = releaseForm;
    releaseForm = null;
    go?.();
    await settle(4000);
  };
  const sent = (path) => requests.filter((request) => request.url.split("?")[0] === path);
  const drop = async (name, base64) => {
    weaveMode.importPrintFile({ name, base64 });
    await settle(4000);
  };
  const switches = () => {
    const pattern = page.patternObject();
    return [
      pattern.settings.wave_on !== false,
      ...(pattern.extra_weaves || []).map((entry) => entry.settings.wave_on !== false),
    ];
  };
  const shown = (selector) => !$(selector).hidden;
  const view = () => {
    const snapshot = page.weaveSettingsSnapshot();
    return {
      model: page.S.file?.name || null,
      mesh: Boolean(page.S.mesh),
      summary: $("#weaveFileSummary").textContent,
      summaryTip: $("#weaveFileSummary").title,
      line: shown("#weaveFromPrint") ? $("#weaveFromPrintText").textContent : null,
      choose: shown("#weaveFromPrintChoose") ? $("#weaveFromPrintChoose").textContent : null,
      chooseTip: $("#weaveFromPrintChoose").title,
      hint: shown("#weaveFromPrintHint") ? $("#weaveFromPrintHint").textContent : null,
      hintTip: $("#weaveFromPrintHint").title,
      switches: switches(),
      placement: snapshot.placement,
      layerHeight: snapshot.slice.layer_height,
      topLayer: page.S.topLayer,
      islandStopDeclined: page.S.islandStopDeclined,
      range: page.S.pendingRange ? { ...page.S.pendingRange } : null,
      empty: shown("#weaveEmptyState"),
      error: shown("#weaveErrorState"),
      title: $("#weaveEmptyTitle").textContent,
      text: $("#weaveEmptyText").textContent,
      emptyChoose: shown("#weaveEmptyChooseModelButton"),
      emptyOpen: shown("#weaveEmptyOpenProjectButton"),
      projectStatus: $("#weaveProjectStatus").textContent,
      restoreStatus: $("#weaveRestoreStatus").textContent,
      inches: shown("#weaveInchesBanner"),
      history: weaveMode.historyState(),
    };
  };
"""


def _run(body: str, **constants: Any) -> dict[str, Any]:
    head = "".join(f"const {name} = {json.dumps(value)};\n" for name, value in constants.items())
    return run_page(head + _HELPERS + body)


def _cylinder() -> str:
    return _b64((MESH / "cylinder.obj").read_bytes())


def test_a_drop_with_no_model_ends_with_the_form_its_settings_and_the_weaves_off() -> None:
    out = _run(
        r"""
  out.before = weaveMode.historyState();
  await drop("swap.gcode", FILE);
  out.view = view();
  out.restores = sent("/api/weave/restore").map((request) => request.url);
  out.forms = sent("/api/weave/restore/form").map((request) => request.url);
  out.uploads = sent("/api/weave/mesh").length;
  click("#weaveResetButton");
  await settle(4000);
  out.reset = view();
""",
        FILE=_b64(_swap_print()),
    )

    view = out["view"]
    assert out["restores"] == ["/api/weave/restore"]
    assert out["forms"] == ["/api/weave/restore/form?filename=swap.gcode"]
    assert out["uploads"] == 1
    # The form is the printed surface, at the size and angle it printed.
    assert view["model"] == "swap-as-printed.obj"
    assert view["mesh"] is True
    assert view["empty"] is False and view["error"] is False
    assert view["summary"] == "swap-as-printed.obj"
    assert view["summaryTip"] == NAME_TIP
    placement = view["placement"]
    assert placement["scale"] == 1 and placement["fit_height"] is None
    assert [placement[key] for key in ("scale_x", "scale_y", "scale_z")] == [1, 1, 1]
    assert [placement[key] for key in ("rotation_deg", "rotation_x_deg", "rotation_y_deg")] == [
        0,
        0,
        0,
    ]
    assert placement["up_axis"] == "z"
    # Every other setting is the file's.
    assert view["layerHeight"] == 5
    assert view["topLayer"] == "below"
    # The whole form is the range, and no island stop is proposed on it.
    assert view["range"] == {
        "from": 1,
        "to": 4,
        "total": 4,
        "enabled": False,
        "autoIslandStop": False,
    }
    assert view["islandStopDeclined"] is True
    # Every weave off, Weave 1 included; the line, its button and the hint.
    assert view["switches"] == [False, False, False]
    assert view["line"] == LINE.format("swap.gcode")
    assert view["choose"] == "Choose cylinder.obj…"
    assert view["chooseTip"] == (
        "Open the model this print file was sliced from, in place of the form made from it. "
        "It is placed as it printed."
    )
    assert view["hint"] == HINT
    assert view["hintTip"] == HINT_TIP
    # The two status lines keep their own words.
    assert view["projectStatus"] == ""
    assert view["restoreStatus"].startswith(
        "A print file Clayline saved gives up its pattern here."
    )
    assert view["inches"] is False
    # One step for the restore and its form.
    assert view["history"]["index"] == out["before"]["index"] + 1
    # After Reset the line still holds: the form is still the printed surface.
    reset = out["reset"]
    assert reset["model"] == "swap-as-printed.obj"
    assert reset["line"] == LINE.format("swap.gcode")
    assert reset["summaryTip"] == NAME_TIP


def test_choose_swaps_in_the_model_where_the_file_printed_it_with_its_weaves_back() -> None:
    cone = _b64((MESH / "cone.obj").read_bytes())
    out = _run(
        r"""
  await drop("swap.gcode", FILE);
  let picked = 0;
  $("#weaveFileInput").click = () => { picked += 1; };
  click("#weaveFromPrintChoose");
  out.picked = picked;
  // An edit made to the form gives way to the file's own values on the swap.
  type("#weaveScale", 2);
  await settle(1000);
  out.edited = page.weaveSettingsSnapshot().placement.scale;
  weaveMode.importMesh({ name: "cylinder.obj", base64: MESH });
  await settle(4000);
  out.swapped = view();
  // Back to the form, and a file of the same name that is not the same model.
  weaveMode.undo();
  await settle(4000);
  out.undone = view();
  weaveMode.importMesh({ name: "cylinder.obj", base64: CONE });
  await settle(4000);
  out.changed = view();
  weaveMode.undo();
  await settle(4000);
  weaveMode.importMesh({ name: "cone.obj", base64: CONE });
  await settle(4000);
  out.other = view();
""",
        FILE=_b64(_swap_print()),
        MESH=_cylinder(),
        CONE=cone,
    )

    assert out["picked"] == 1
    assert out["edited"] == 2
    swapped = out["swapped"]
    assert swapped["model"] == "cylinder.obj" and swapped["mesh"] is True
    placement = swapped["placement"]
    assert placement["scale"] == 1.2
    assert placement["rotation_deg"] == 15
    assert placement["up_axis"] == "z"
    # Weaves on as the file had them: Weave 3 was off in it.
    assert swapped["switches"] == [True, True, False]
    # The file's top rule, island stop and range, waiting for the slice.
    assert swapped["topLayer"] == "below"
    assert swapped["islandStopDeclined"] is False
    assert swapped["range"] == {
        "from": 2,
        "to": 5,
        "total": 7,
        "enabled": True,
        "autoIslandStop": False,
    }
    assert swapped["line"] == "cylinder.obj came in where swap.gcode printed it."
    assert swapped["choose"] is None
    assert swapped["hint"] is None
    assert swapped["summaryTip"] == ""
    assert swapped["inches"] is False

    # Undo brings the form back with its line, its button and its weaves off.
    undone = out["undone"]
    assert undone["model"] == "swap-as-printed.obj"
    assert undone["line"] == LINE.format("swap.gcode")
    assert undone["choose"] == "Choose cylinder.obj…"
    assert undone["switches"] == [False, False, False]
    assert undone["hint"] == HINT

    # A file named like the model but not it is said, in the potter's words.
    assert out["changed"]["line"] == (
        "cylinder.obj has changed since swap.gcode was sliced from it, "
        "so the result may not match the print file."
    )
    assert out["other"]["line"] == (
        "cone.obj is loaded, placed as swap.gcode printed it, "
        "but it is not cylinder.obj, the one it was sliced from."
    )
    for view in (out["changed"], out["other"]):
        assert "SHA" not in view["line"] and "sha" not in view["line"]


def test_one_undo_takes_the_restore_and_its_form_back_whole() -> None:
    out = _run(
        r"""
  out.before = { history: weaveMode.historyState(), view: view() };
  await drop("swap.gcode", FILE);
  out.landed = view();
  weaveMode.undo();
  await settle(4000);
  out.undone = view();
  weaveMode.redo();
  await settle(4000);
  out.redone = view();
""",
        FILE=_b64(_swap_print()),
    )

    before = out["before"]["view"]
    undone = out["undone"]
    assert out["landed"]["history"]["index"] == out["before"]["history"]["index"] + 1
    assert undone["history"]["index"] == out["before"]["history"]["index"]
    assert undone["model"] is None
    assert undone["layerHeight"] == before["layerHeight"]
    assert undone["switches"] == before["switches"]
    assert undone["line"] is None and undone["hint"] is None
    redone = out["redone"]
    assert redone["model"] == "swap-as-printed.obj"
    assert redone["line"] == LINE.format("swap.gcode")
    assert redone["switches"] == [False, False, False]
    assert redone["layerHeight"] == 5


def test_an_edit_made_while_the_form_is_made_is_its_own_step() -> None:
    out = _run(
        r"""
  out.before = weaveMode.historyState();
  hold();
  await drop("swap.gcode", FILE);
  out.waiting = view();
  type("#weaveFlow", 1.1);
  await settle(1000);
  out.edited = weaveMode.historyState();
  await release();
  out.landed = view();
  weaveMode.undo();
  await settle(4000);
  out.first = view();
  out.firstFlow = page.weaveSettingsSnapshot().export.flow_multiplier;
  weaveMode.undo();
  await settle(4000);
  out.second = view();
  out.secondFlow = page.weaveSettingsSnapshot().export.flow_multiplier;
""",
        FILE=_b64(_swap_print()),
    )

    waiting = out["waiting"]
    assert waiting["empty"] is True and waiting["error"] is False
    assert waiting["title"] == "Making the form from swap.gcode…"
    assert waiting["text"] == "Every setting is back. If you have cylinder.obj, choose it instead."
    assert waiting["emptyChoose"] is True and waiting["emptyOpen"] is True
    assert waiting["layerHeight"] == 5
    # Restore, edit, form: three steps.
    base = out["before"]["index"]
    assert out["edited"]["index"] == base + 2
    assert out["landed"]["model"] == "swap-as-printed.obj"
    assert out["landed"]["history"]["index"] == base + 3
    # The first Undo takes the form only; the edit stays.
    assert out["first"]["model"] is None
    assert out["firstFlow"] == 1.1
    assert out["secondFlow"] != 1.1
    assert out["second"]["history"]["index"] == base + 1


def test_undo_reset_or_a_project_opened_while_the_form_is_made_drops_it_quietly() -> None:
    common = {"FILE": _b64(_swap_print())}
    undo = _run(
        r"""
  hold();
  await drop("swap.gcode", FILE);
  weaveMode.undo();
  await settle(1000);
  await release();
  out.view = view();
  out.uploads = sent("/api/weave/mesh").length;
""",
        **common,
    )
    reset = _run(
        r"""
  hold();
  await drop("swap.gcode", FILE);
  click("#weaveResetButton");
  await settle(1000);
  await release();
  out.view = view();
  out.uploads = sent("/api/weave/mesh").length;
""",
        **common,
    )
    opened = _run(
        r"""
  hold();
  await drop("swap.gcode", FILE);
  const settings = page.weaveSettingsSnapshot();
  const project = await codec.read(await codec.write({
    mode: "weave", settings, sources: [{ name: "cone.obj", bytes: new TextEncoder().encode(CONE) }],
  }));
  out.opened = await weaveMode.openProject(project, "cone.clayline");
  await settle(4000);
  await release();
  out.view = view();
  out.uploads = sent("/api/weave/mesh").length;
""",
        CONE=(MESH / "cone.obj").read_text(encoding="utf-8"),
        **common,
    )

    for out in (undo, reset):
        view = out["view"]
        assert out["uploads"] == 0
        assert view["model"] is None
        assert view["error"] is False
        assert view["line"] is None
        assert view["title"] != "Making the form from swap.gcode…"
    assert reset["view"]["title"] == "Load a base mesh"
    assert reset["view"]["emptyChoose"] is False
    assert opened["opened"] is True
    assert opened["uploads"] == 1
    assert opened["view"]["model"] == "cone.obj"
    assert opened["view"]["line"] is None
    assert opened["view"]["error"] is False


def test_a_refused_form_request_goes_back_to_asking_for_the_model() -> None:
    stack = _print(stack_pieces=True)
    lines = _print().splitlines(keepends=True)
    begin = next(i for i, line in enumerate(lines) if line.startswith("; CLAYLINE_BODY_BEGIN"))
    edited = next(i for i in range(begin, len(lines)) if lines[i].startswith("G1 X"))
    lines[edited] = lines[edited].replace("G1 X", "G1 X1", 1)
    out = _run(
        r"""
  // A file turned down first leaves the error panel up.
  out.turnedDown = weaveMode.importPrintFile({ name: "form.stl", base64: STACK });
  await settle(1000);
  out.errorFirst = shown("#weaveErrorState");
  hold();
  await drop("stacked.gcode", STACK);
  out.waiting = view();
  await release();
  out.stack = view();
  await drop("edited.gcode", EDITED);
  out.edited = view();
  // The engine out of reach: the settings are back all the same.
  window.fetch = (url, init) => (String(url).startsWith("/api/weave/restore/form")
    ? Promise.reject(new TypeError("Load failed"))
    : realFetch(url, init));
  await drop("lost.gcode", PLAIN);
  out.lost = view();
""",
        STACK=_b64(stack),
        EDITED=_b64("".join(lines)),
        PLAIN=_b64(_print()),
    )

    # The empty preview takes over from the error panel, while the form is
    # made and after it is refused.
    assert out["turnedDown"] is False and out["errorFirst"] is True
    waiting = out["waiting"]
    assert waiting["error"] is False and waiting["empty"] is True
    assert waiting["title"] == "Making the form from stacked.gcode…"
    stacked = out["stack"]
    sentence = "Clayline can't yet make a form from a print made with Stack pieces."
    assert stacked["model"] is None and stacked["error"] is False and stacked["empty"] is True
    assert stacked["title"] == "Load cylinder.obj"
    assert stacked["text"] == sentence
    assert stacked["emptyChoose"] is True
    # Said once, in the middle of the window: the two lines keep their words.
    assert stacked["projectStatus"] == ""
    assert stacked["restoreStatus"].startswith(
        "A print file Clayline saved gives up its pattern here."
    )
    assert stacked["layerHeight"] == 5
    assert out["edited"]["text"] == (
        "edited.gcode has been changed since Clayline wrote it, so only its settings came back."
    )
    lost = out["lost"]
    assert lost["error"] is False
    assert lost["text"] == (
        "Every setting came back from lost.gcode, but Clayline couldn't make a form from it. "
        "Load cylinder.obj to go on with the job."
    )
    assert lost["emptyChoose"] is True
    assert lost["projectStatus"] == ""


def test_a_printer_gone_or_changed_is_said_in_its_own_sentence() -> None:
    # The engine's reasons are its own tests' (tests/test_form_from_print.py);
    # here the page is handed each one and says it.
    out = _run(
        r"""
  for (const reason of ["profile_missing", "profile_changed"]) {
    window.fetch = (url, init) => (String(url).startsWith("/api/weave/restore/form")
      ? Promise.resolve({ ok: true, status: 200, json: async () => ({ kind: "none", reason }) })
      : realFetch(url, init));
    await drop(`${reason}.gcode`, PLAIN);
    out[reason] = view();
  }
""",
        PLAIN=_b64(_print()),
    )

    assert out["profile_missing"]["text"] == (
        "Clayline can't make a form from a print made with a printer that is no longer in the list."
    )
    assert out["profile_changed"]["text"] == (
        "Clayline can't make a form from a print whose printer's bed has changed since it printed."
    )
    for reason in ("profile_missing", "profile_changed"):
        view = out[reason]
        assert view["model"] is None and view["error"] is False and view["empty"] is True
        assert view["title"] == "Load cylinder.obj"
        assert view["emptyChoose"] is True
        assert view["projectStatus"] == ""


def test_a_small_print_raises_no_inches_banner() -> None:
    out = _run(
        r"""
  await drop("tile.gcode", FILE);
  out.form = view();
  const form = page.S.file;
  // Saved and opened again, it is still not asked about.
  const saved = [];
  const createObjectURL = URL.createObjectURL;
  URL.createObjectURL = (blob) => { saved.push(blob); return createObjectURL(blob); };
  await weaveMode.saveProject();
  out.opened = await weaveMode.openProject(await codec.read(saved[0]), "tile.clayline");
  await settle(4000);
  out.reopened = view();
  // The same surface loaded as an ordinary model is asked about.
  weaveMode.undo();
  await settle(4000);
  weaveMode.undo();
  await settle(4000);
  const bytes = Buffer.from(await form.arrayBuffer()).toString("base64");
  weaveMode.importMesh({ name: "tile.obj", base64: bytes });
  await settle(4000);
  out.plain = view();
""",
        FILE=_b64(_print(scale=0.5)),
    )

    assert out["form"]["model"] == "tile-as-printed.obj"
    assert out["form"]["inches"] is False
    assert out["opened"] is True
    assert out["reopened"]["model"] == "tile-as-printed.obj"
    assert out["reopened"]["inches"] is False
    assert out["plain"]["model"] == "tile.obj"
    assert out["plain"]["inches"] is True


def test_a_print_made_from_a_form_from_a_print(tmp_path: Path) -> None:
    form = tmp_path / "first-as-printed.obj"
    form.write_bytes((MESH / "cylinder.obj").read_bytes())
    out = _run(
        r"""
  await drop("first.gcode", FIRST);
  out.first = view();
  hold();
  await drop("second.gcode", SECOND);
  out.waiting = view();
  await release();
  out.second = view();
  out.restores = sent("/api/weave/restore").map((request) => request.url);
  type("#weaveOffsetX", 7);
  await settle(1000);
  weaveMode.importMesh({ name: "cylinder.obj", base64: MESH });
  await settle(4000);
  out.loaded = view();
  for (let step = 0; step < 3; step += 1) {
    weaveMode.undo();
    await settle(4000);
  }
  out.undone = view();
""",
        FIRST=_b64(_swap_print()),
        SECOND=_b64(_print(form)),
        MESH=_cylinder(),
    )

    assert out["first"]["model"] == "first-as-printed.obj"
    # The form on the table is named, is not the model the second file was
    # sliced from, and so counts as no model.
    assert out["restores"][0] == "/api/weave/restore"
    assert out["restores"][1].startswith("/api/weave/restore?mesh_id=")
    waiting = out["waiting"]
    assert waiting["model"] is None and waiting["empty"] is True
    # The model the second file names was never on disk, so it is not asked for.
    assert waiting["title"] == "Making the form from second.gcode…"
    assert waiting["text"] == "Every setting is back."
    assert waiting["emptyChoose"] is False
    second = out["second"]
    assert second["model"] == "second-as-printed.obj"
    assert second["line"] == LINE.format("second.gcode")
    assert second["choose"] is None
    assert second["hint"] == "Weaves are off: this form already carries the pattern."
    assert second["switches"] == [False]
    # A model loaded over it stays where it is put, but its weaves come back
    # on as the file had them: it is not left a plain wall without a word.
    loaded = out["loaded"]
    assert loaded["model"] == "cylinder.obj"
    assert loaded["placement"]["offset_x"] == 7
    assert loaded["switches"] == [True]
    assert loaded["line"] is None and loaded["hint"] is None
    # Undo brings the first form back as it was.
    undone = out["undone"]
    assert undone["model"] == "first-as-printed.obj"
    assert undone["line"] == LINE.format("first.gcode")
    assert undone["choose"] == "Choose cylinder.obj…"


def test_a_saved_form_reopens_as_the_printed_surface_and_offers_no_swap() -> None:
    out = _run(
        r"""
  await drop("swap.gcode", FILE);
  out.session = view();
  const saved = [];
  const createObjectURL = URL.createObjectURL;
  URL.createObjectURL = (blob) => { saved.push(blob); return createObjectURL(blob); };
  out.wrote = await weaveMode.saveProject();
  out.afterSave = view();
  const project = await codec.read(saved[0]);
  out.opened = await weaveMode.openProject(project, "swap-as-printed.clayline");
  await settle(4000);
  out.reopened = view();
  weaveMode.importMesh({ name: "cylinder.obj", base64: MESH });
  await settle(4000);
  out.loaded = view();
""",
        FILE=_b64(_swap_print()),
        MESH=_cylinder(),
    )

    # Within the session the swap is offered, and a save leaves it there.
    assert out["session"]["choose"] == "Choose cylinder.obj…"
    assert out["wrote"] is True
    assert out["afterSave"]["choose"] == "Choose cylinder.obj…"
    assert out["afterSave"]["line"] == LINE.format("swap.gcode")
    reopened = out["reopened"]
    assert out["opened"] is True
    assert reopened["model"] == "swap-as-printed.obj"
    # Worked out from the name: still the printed surface, with its tooltip.
    assert reopened["line"] == "Form is swap.gcode's printed surface, pattern and all."
    assert reopened["summaryTip"] == NAME_TIP
    assert reopened["hint"] == "Weaves are off: this form already carries the pattern."
    assert reopened["switches"] == [False, False, False]
    assert reopened["choose"] is None
    # No swap after a reopen: a model loaded now is loaded as any model is.
    loaded = out["loaded"]
    assert loaded["model"] == "cylinder.obj"
    assert loaded["placement"]["scale"] == 1
    assert loaded["switches"] == [False, False, False]
    assert loaded["line"] is None


def test_two_print_files_dropped_at_once_end_with_the_second_ones_form() -> None:
    out = _run(
        r"""
  out.before = weaveMode.historyState();
  weaveMode.importPrintFile({ name: "first.gcode", base64: FIRST });
  weaveMode.importPrintFile({ name: "second.gcode", base64: SECOND });
  await settle(6000);
  out.view = view();
  out.forms = sent("/api/weave/restore/form").map((request) => request.url);
""",
        FIRST=_b64(_swap_print()),
        SECOND=_b64(_print(MESH / "cone.obj")),
    )

    # The first file's form is never asked for: the second file is the job.
    assert out["forms"] == ["/api/weave/restore/form?filename=second.gcode"]
    view = out["view"]
    assert view["model"] == "second-as-printed.obj"
    assert view["line"] == LINE.format("second.gcode")
    assert view["choose"] == "Choose cone.obj…"
    # The second file's own settings, under its own form.
    assert view["switches"] == [False]
    assert view["topLayer"] == "nearest"
    assert view["empty"] is False and view["error"] is False


def test_another_slicers_print_file_over_a_form_is_not_placed_as_the_print_was() -> None:
    from test_gcode_import import _cura_like

    out = _run(
        r"""
  await drop("swap.gcode", FILE);
  weaveMode.importPrintFile({ name: "other.gcode", base64: CURA });
  await settle(6000);
  out.view = view();
  out.facts = $("#weaveModelFacts").textContent;
""",
        FILE=_b64(_swap_print()),
        CURA=_b64(_cura_like()),
    )

    view = out["view"]
    assert view["model"] == "other.gcode" and view["error"] is False
    assert out["facts"].startswith("rebuilt from other.gcode")
    # Already at the size it printed: not scaled or turned to swap.gcode's model.
    assert view["placement"]["scale"] == 1
    assert view["placement"]["rotation_deg"] == 0
    assert view["line"] is None


def test_restore_pattern_while_the_form_is_made_leaves_the_form_to_land() -> None:
    out = _run(
        r"""
  out.before = weaveMode.historyState();
  hold();
  await drop("swap.gcode", FILE);
  const input = $("#weaveRestoreFile");
  input.files = [new File([Buffer.from(OTHER, "base64")], "other.gcode")];
  input.dispatchEvent(new Event("change", { bubbles: true }));
  await settle(4000);
  out.patterned = view();
  await release();
  out.view = view();
  out.uploads = sent("/api/weave/mesh").length;
""",
        FILE=_b64(_swap_print()),
        OTHER=_b64(_print()),
    )

    assert out["patterned"]["title"] == "Making the form from swap.gcode…"
    view = out["view"]
    assert out["uploads"] == 1
    assert view["model"] == "swap-as-printed.obj"
    assert view["line"] == LINE.format("swap.gcode")
    assert view["switches"] == [False]
    # Restore, pattern, form: the form is its own step.
    assert view["history"]["index"] == out["before"]["index"] + 3


def test_a_print_with_every_weave_off_says_nothing_of_a_pattern() -> None:
    plain = cl.preset_pattern("sine")
    plain = replace(plain, settings=replace(plain.settings, wave_on=False))
    out = _run(
        r"""
  await drop("plain.gcode", FILE);
  out.form = view();
  weaveMode.importMesh({ name: "cylinder.obj", base64: MESH });
  await settle(4000);
  out.swapped = view();
""",
        FILE=_b64(_print(pattern=plain)),
        MESH=_cylinder(),
    )

    form = out["form"]
    assert form["model"] == "plain-as-printed.obj"
    assert form["line"] == LINE.format("plain.gcode")
    assert form["switches"] == [False]
    assert form["hint"] is None
    swapped = out["swapped"]
    assert swapped["switches"] == [False]
    assert swapped["line"] == "cylinder.obj came in where plain.gcode printed it."


def test_a_reopened_form_gives_way_to_its_print_file_dropped_again() -> None:
    out = _run(
        r"""
  await drop("swap.gcode", FILE);
  const saved = [];
  const createObjectURL = URL.createObjectURL;
  URL.createObjectURL = (blob) => { saved.push(blob); return createObjectURL(blob); };
  await weaveMode.saveProject();
  const project = await codec.read(saved[0]);
  await weaveMode.openProject(project, "swap-as-printed.clayline");
  await settle(4000);
  out.reopened = view();
  await drop("swap.gcode", FILE);
  out.again = view();
  out.forms = sent("/api/weave/restore/form").length;
  weaveMode.undo();
  await settle(4000);
  out.undone = view();
""",
        FILE=_b64(_swap_print()),
    )

    assert out["reopened"]["choose"] is None
    # Dropped again on the reopened form, the print file makes its form anew
    # and the button to swap in its model comes back, as the guide says.
    again = out["again"]
    assert out["forms"] == 2
    assert again["model"] == "swap-as-printed.obj"
    assert again["line"] == LINE.format("swap.gcode")
    assert again["choose"] == "Choose cylinder.obj…"
    assert again["switches"] == [False, False, False]
    assert again["error"] is False
    # Undo brings the reopened form back.
    assert out["undone"]["model"] == "swap-as-printed.obj"
    assert out["undone"]["choose"] is None


def test_the_model_a_print_was_sliced_from_is_kept_even_named_like_a_form(tmp_path: Path) -> None:
    own = tmp_path / "bowl-as-printed.obj"
    own.write_bytes((MESH / "cylinder.obj").read_bytes())
    out = _run(
        r"""
  weaveMode.importMesh({ name: "bowl-as-printed.obj", base64: MESH });
  await settle(4000);
  out.loaded = view();
  await drop("bowl.gcode", FILE);
  out.after = view();
  out.restores = sent("/api/weave/restore").map((request) => request.url);
  out.forms = sent("/api/weave/restore/form").length;
""",
        MESH=_cylinder(),
        FILE=_b64(_print(own)),
    )

    # Known by its name, it reads as the printed surface ...
    assert out["loaded"]["line"] == LINE.format("bowl.gcode")
    # ... but a loaded model is never replaced: the print's settings go onto it.
    assert len(out["restores"]) == 1
    assert out["restores"][0].startswith("/api/weave/restore?mesh_id=")
    assert out["forms"] == 0
    after = out["after"]
    assert after["model"] == "bowl-as-printed.obj"
    assert after["switches"] == [True]
    assert after["projectStatus"] == (
        "Every setting came back from bowl.gcode, "
        "and the loaded model is the one it was sliced from."
    )


def test_a_print_whose_model_was_never_on_disk_asks_for_none_by_name(tmp_path: Path) -> None:
    form = tmp_path / "first-as-printed.obj"
    form.write_bytes((MESH / "cylinder.obj").read_bytes())
    out = _run(
        r"""
  await drop("stacked.gcode", STACK);
  out.stack = view();
  window.fetch = (url, init) => (String(url).startsWith("/api/weave/restore/form")
    ? Promise.reject(new TypeError("Load failed"))
    : realFetch(url, init));
  await drop("lost.gcode", PLAIN);
  out.lost = view();
""",
        STACK=_b64(_print(form, stack_pieces=True)),
        PLAIN=_b64(_print(form)),
    )

    stacked = out["stack"]
    assert stacked["title"] == "Load a model"
    assert stacked["text"] == "Clayline can't yet make a form from a print made with Stack pieces."
    # The button still opens a model, such as one written beside the print.
    assert stacked["emptyChoose"] is True
    lost = out["lost"]
    assert lost["title"] == "Load a model"
    assert lost["text"] == (
        "Every setting came back from lost.gcode, but Clayline couldn't make a form from it. "
        "Open the project it was made in, or load a model, to go on with the job."
    )
    assert lost["emptyChoose"] is True and lost["error"] is False
