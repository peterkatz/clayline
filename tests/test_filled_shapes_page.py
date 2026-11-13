# ruff: noqa: E501
"""The page's half of lines from a drawing.

What the page reads off a drawing and the queue are run under node as they ship.
The studio side is the "lines from a drawing" section of ``app.js``, lifted and run
against a small stand-in for the rest of the page, with the real history behind it.
The real thing in a real web view is a separate check: these pin what it found.
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any

import pytest

from clayline.shape_lines import keep_original, make_lines
from clayline.webui import app as webui

ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "src" / "clayline" / "webui" / "static"
APP = (STATIC / "app.js").read_text(encoding="utf-8")
DRAW = (STATIC / "draw.js").read_text(encoding="utf-8")
HTML = (STATIC / "index.html").read_text(encoding="utf-8")
LINES_JS = STATIC / "shape-lines.js"
STATE_JS = STATIC / "studio-state.js"
_SECTION_OPENS = "/* ---------- lines from a drawing"
SECTION = _SECTION_OPENS + APP.split(_SECTION_OPENS, 1)[1].split("async function readFiles", 1)[0]

CONVERTED = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="110mm" height="60mm" '
    'viewBox="0 0 110 60" fill="none" stroke="#000" stroke-width="5" stroke-linecap="round" '
    'data-clayline-converted="1" data-clayline-target="100" data-clayline-coil="5" '
    'data-clayline-join="0.2" data-clayline-size-basis="fit" '
    'data-clayline-sentence="At this size, 17 of 19 small gaps fill in. '
    'It reads well from about {size}." data-clayline-sentence-kind="fine_detail" '
    'data-clayline-suggested="240" data-clayline-place="1 2 0.5 5 200 100">\n'
    '<metadata id="clayline-original">&lt;svg&gt;the &amp;lt;file&amp;gt;&#13;&lt;/svg&gt;</metadata>\n'
    '  <path id="from-shape-0" d="M 5 5 L 105 55"/>\n</svg>\n'
)


def _node(script: str) -> str:
    result = subprocess.run(["node", "-e", script], check=False, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    return result.stdout


def _with_lines(body: str) -> str:
    return _node(
        'const assert = require("node:assert/strict");\n'
        f"const Lines = require({json.dumps(str(LINES_JS))});\n"
        f"const CONVERTED = {json.dumps(CONVERTED)};\n"
        f"{body}\n"
        'console.log("ok");\n'
    )


# What the page stands on: the real history, and a stand-in for everything else in app.js.
RIG = (
    """
const assert = require("node:assert/strict");
const realLines = require(@@LINES@@);
const Studio = require(@@STATE@@);
const asked = [];
let answers = {};
const respond = (status, payload) => ({ ok: status < 400, status, json: async () => payload });
globalThis.fetch = async (path, init) => {
  const body = JSON.parse(init.body);
  asked.push({ path, body });
  const answer = answers[path];
  if (typeof answer === "function") return answer(body);
  return respond(200, answer);
};
const element = () => {
  const node = {
    hidden: false, textContent: "", title: "", children: [], attrs: {},
    classList: { add() {}, toggle() {} }, dataset: {}, style: {},
    append(...items) { this.children.push(...items); },
    addEventListener(type, fn) { this[`on${type}`] = fn; },
    setAttribute(name, value) { this.attrs[name] = value; },
    removeAttribute() {}, replaceChildren() { this.children = []; }, remove() {},
    scrollIntoView() {},
  };
  return node;
};
globalThis.document = { createElement: element, createElementNS: () => element() };
const nodes = new Map();
const $ = (selector) => {
  if (selector.startsWith("#pageList")) return null;
  if (selector === "#profile") return { value: "test" };
  if (!nodes.has(selector)) nodes.set(selector, element());
  return nodes.get(selector);
};
const $$ = () => [];
globalThis.window = {
  claylineUnits: { fmt: (mm, digits = 1) => `${mm.toFixed(digits)} mm` },
  setTimeout: (fn, ms) => (ms > 1000 ? 0 : setTimeout(fn, 0)),
  clearTimeout: (timer) => clearTimeout(timer),
};
const state = {
  files: [], linesAnswers: new Map(), selectedFile: null, stageKind: "empty", layout: null,
  layoutToken: 0, layoutTimer: 0, revision: 0,
  profiles: new Map([["test", { work_bounds: { min_x: 0, max_x: 381, min_y: 0, max_y: 381 } }]]),
};
const Lines = { ...realLines, paintToBlob: async () => ({}), blobToBase64: async () => "data:image/png;base64,AAAA" };
let coil = 5;
let join = 0.2;
const counts = { render: 0, layout: 0, dirty: 0 };
const effectiveBeadWidth = () => coil;
const overlapFraction = () => join;
const renderPages = () => { counts.render += 1; };
const updateDependencies = () => {};
const scheduleLayoutCheck = () => { counts.layout += 1; };
const markDirty = () => { counts.dirty += 1; };
const invalidatePassMeasurement = (file) => {
  file.sourceLongestMm = null;
  file.measurementStatus = "pending";
};
const normalizePassFile = (file) => file;
const pageColor = () => "#a94f32";
const passMeasurementReady = (file) => file.measurementStatus === "ready" && file.sourceLongestMm > 0 && file.sizeMm > 0;
const passScaleFactor = (file, fallback) => (passMeasurementReady(file) ? file.sizeMm / file.sourceLongestMm : fallback);
const URL = { revokeObjectURL() {}, createObjectURL: () => "blob:x" };
const snapshot = () => ({
  passes: state.files.map((file) => ({
    name: file.name, svg: file.svg, size_mm: file.sizeMm, size_pinned: file.sizePinned,
  })),
  job: { bead_width_mm: coil, overlap_fraction: join },
});
const drawHistory = Studio.createHistory({ limit: 100 });
const drawStateWriter = {
  flush() { drawHistory.push(snapshot()); },
  schedule() {},
};
const endDrawGesture = () => drawStateWriter.flush();
function setFiles(files) {
  carryLinesJobs(files);
  state.files = files;
  drawStateWriter.flush();
}
const pass = (name, svg, extra = {}) => ({
  name, svg, sizeMm: null, sizePinned: false, measurementStatus: "pending", ...extra,
});
const tick = async () => { for (let i = 0; i < 20; i += 1) await new Promise((r) => setTimeout(r, 0)); };
const CONVERTED = Lines.withLinesHash(@@CONVERTED@@);
const LEAVE = { verdict: "leave" };
const CONVERT = { verdict: "convert", paint_svg: "<svg/>", canvas: { width: 10, height: 10 } };
const LINES = { verdict: "lines", svg: CONVERTED, size_basis: "fit", target_mm: 100 };
drawHistory.seed(snapshot());
""".replace("@@LINES@@", json.dumps(str(LINES_JS)))
    .replace("@@STATE@@", json.dumps(str(STATE_JS)))
    .replace("@@CONVERTED@@", json.dumps(CONVERTED))
)


def _run_section(scenario: str) -> str:
    return _node(RIG + SECTION + f"\n(async () => {{\n{scenario}\nconsole.log('ok');\n}})();\n")


def test_a_kept_original_comes_back_exactly_and_never_goes_to_the_engine() -> None:
    original = (
        '<?xml version="1.0"?>\r\n<svg><style><![CDATA[.a{fill:#000}]]></style>'
        '<text>&amp; &lt;tag&gt; "</text></svg>\r\n'
    )
    svg = CONVERTED.replace(
        "&lt;svg&gt;the &amp;lt;file&amp;gt;&#13;&lt;/svg&gt;", keep_original(original)
    )
    out = _with_lines(
        f"const svg = {json.dumps(svg)};\n"
        f"assert.equal(Lines.originalOf(svg), {json.dumps(original)});\n"
        'assert.ok(!Lines.withoutOriginal(svg).includes("<metadata"));\n'
        "assert.ok(Lines.withoutOriginal(svg).includes('id=\"from-shape-0\"'));\n"
    )
    assert "ok" in out


def test_a_file_that_was_left_alone_stays_the_identical_string() -> None:
    plain = '<svg xmlns="http://www.w3.org/2000/svg"><metadata id="clayline-original">x</metadata></svg>'
    _with_lines(
        f"const plain = {json.dumps(plain)};\n"
        "assert.equal(Lines.isConverted(plain), false);\n"
        "assert.equal(Lines.withoutOriginal(plain), plain);\n"
        "assert.equal(Lines.originalOf(plain), null);\n"
        "assert.equal(Lines.marksOf(plain), null);\n"
    )


def test_a_kept_answer_comes_off_to_the_byte_whatever_the_sentence_holds() -> None:
    _with_lines(
        """
const answer = { verdict: "photo", sentence: 'A "quoted" <sentence> & more', next: "trace", asked: null };
for (const file of [
  '<?xml version="1.0"?>\\n<!-- <svg> --><svg xmlns="x" width="9">\\r\\n<path/></svg>',
  "<svg/>",
  "<svg>filled</svg>",
  '<svg\\n  xmlns="x"\\n><g/></svg>',
]) {
  const kept = Lines.withAnswer(file, answer);
  assert.notEqual(kept, file);
  assert.deepEqual(Lines.answerOf(kept), answer);
  assert.equal(Lines.withoutAnswer(kept), file);
  assert.equal(Lines.isConverted(kept), false);
  // A second answer takes the place of the first.
  const again = Lines.withAnswer(kept, { verdict: "nothing" });
  assert.deepEqual(Lines.answerOf(again), { verdict: "nothing" });
  assert.equal(Lines.withoutAnswer(again), file);
}
// A file with none is the identical string.
assert.equal(Lines.withoutAnswer("<svg>plain</svg>"), "<svg>plain</svg>");
assert.equal(Lines.answerOf("<svg>plain</svg>"), null);
assert.equal(Lines.answerOf('<svg data-clayline-no-lines="not json"/>'), null);
"""
    )


def test_making_lines_again_from_a_kept_answer_sends_the_file_as_it_came() -> None:
    _run_section(
        """
answers["/api/svg/examine"] = CONVERT;
answers["/api/svg/make-lines"] = { verdict: "nothing", nothing_to_draw: true, sentence: "This file has nothing to draw.", next: "remove" };
const file = pass("cat.svg", "<svg>filled</svg>");
addDrawings([file]);
await tick();
assert.notEqual(file.svg, "<svg>filled</svg>");
// Its size can still change the answer. The file sent is the one that came.
answers["/api/svg/make-lines"] = LINES;
setLinesSize(file, 300);
await tick();
const last = asked.filter((c) => c.path === "/api/svg/make-lines").at(-1);
assert.equal(last.body.svg, "<svg>filled</svg>");
assert.equal(last.body.target_mm, 300);
assert.equal(file.svg, CONVERTED);
"""
    )


def test_marks_are_read_from_the_root_and_the_size_is_filled_in_the_units_in_use() -> None:
    _with_lines(
        """
const marks = Lines.marksOf(CONVERTED);
assert.equal(marks.target, 100);
assert.equal(marks.coil, 5);
assert.equal(marks.join, 0.2);
assert.equal(marks.basis, "fit");
assert.equal(marks.suggested, 240);
assert.equal(marks.width, 110);
assert.deepEqual(marks.place, [1, 2, 0.5, 5, 200, 100]);
assert.equal(
  Lines.sentenceFor(marks.sentence, marks.suggested, (mm) => `${mm} mm`),
  "At this size, 17 of 19 small gaps fill in. It reads well from about 240 mm.",
);
assert.equal(
  Lines.sentenceFor(marks.sentence, marks.suggested, (mm) => `${(mm / 25.4).toFixed(2)} in`),
  "At this size, 17 of 19 small gaps fill in. It reads well from about 9.45 in.",
);
// A sentence with no size in it stands, and one missing its size says nothing false.
assert.equal(Lines.sentenceFor("Plain words.", null, String), "Plain words.");
assert.equal(Lines.sentenceFor("From about {size}.", null, String), "");
"""
    )


def test_only_lines_clayline_made_go_in_the_where_lines_meet_block() -> None:
    _with_lines(
        """
const made = { provenance: { element_id: "from-shape-3" } };
assert.equal(Lines.whereLinesMeet({ ...made, code: "tight_radius" }), true);
assert.equal(Lines.whereLinesMeet({ ...made, code: "under_spaced" }), true);
assert.equal(Lines.whereLinesMeet({ ...made, code: "open_end" }), false);
assert.equal(Lines.whereLinesMeet({ code: "tight_radius", provenance: { element_id: "p1" } }), false);
assert.equal(Lines.whereLinesMeet({ code: "tight_radius" }), false);
"""
    )


def test_the_queue_runs_one_at_a_time_and_rows_with_the_same_settings_share_an_answer() -> None:
    _with_lines(
        """
(async () => {
  const landed = [];
  let running = 0;
  let most = 0;
  const release = [];
  const queue = Lines.createQueue({
    work: (job) => new Promise((resolve) => {
      running += 1;
      most = Math.max(most, running);
      release.push(() => { running -= 1; resolve(`answer ${job.key}`); });
    }),
    land: (job, outcome) => landed.push([job.id, outcome.answer]),
  });
  queue.add({ id: 1, key: "a" });
  queue.add({ id: 2, key: "b" });
  queue.add({ id: 3, key: "a" });
  const dropped = { id: 4, key: "a", dropped: true };
  queue.add(dropped);
  assert.equal(release.length, 1);
  release.shift()();
  await new Promise((resolve) => setTimeout(resolve, 0));
  assert.deepEqual(landed, [[1, "answer a"], [3, "answer a"]]);
  assert.equal(release.length, 1);
  release.shift()();
  await new Promise((resolve) => setTimeout(resolve, 0));
  assert.deepEqual(landed.at(-1), [2, "answer b"]);
  assert.equal(most, 1);
  assert.equal(release.length, 0);
})();
"""
    )


def test_a_job_dropped_while_it_runs_shares_nothing_and_its_followers_run_themselves() -> None:
    _with_lines(
        """
(async () => {
  const landed = [];
  const ran = [];
  const release = [];
  const queue = Lines.createQueue({
    work: (job) => new Promise((resolve) => {
      ran.push(job.id);
      release.push(() => resolve(`answer from ${job.id}`));
    }),
    land: (job, outcome) => landed.push([job.id, outcome.answer]),
  });
  const first = { id: 1, key: "a" };
  queue.add(first);
  queue.add({ id: 2, key: "a" });
  queue.add({ id: 3, key: "a" });
  first.dropped = true;
  release.shift()();
  await new Promise((resolve) => setTimeout(resolve, 0));
  // Job 1 lands nowhere and hands nothing on. Job 2 runs, and job 3 shares job 2's.
  assert.deepEqual(ran, [1, 2]);
  assert.deepEqual(landed, []);
  release.shift()();
  await new Promise((resolve) => setTimeout(resolve, 0));
  assert.deepEqual(landed, [[2, "answer from 2"], [3, "answer from 2"]]);
  assert.equal(release.length, 0);
})();
"""
    )


def test_a_picture_that_will_not_paint_ends_with_an_answer_never_a_wait() -> None:
    _node(
        f"const Lines = require({json.dumps(str(LINES_JS))});\n"
        """
const assert = require("node:assert/strict");
globalThis.URL = { createObjectURL: () => "blob:x", revokeObjectURL() {} };
let mode = "";
const canvas = () => ({
  getContext: () => ({ clearRect() {}, drawImage() {} }),
  toBlob(callback) {
    if (mode === "tainted") throw new Error("SecurityError");
    callback(mode === "nothing" ? null : { size: 1 });
  },
});
globalThis.document = { createElement: canvas };
globalThis.Image = class {
  set src(_url) {
    if (mode === "never") return;
    setTimeout(() => (mode === "error" ? this.onerror() : this.onload()), 0);
  }
};
const size = { width: 10, height: 10 };
(async () => {
  mode = "fine";
  assert.deepEqual(await Lines.paintToBlob("<svg/>", size, 50), { size: 1 });
  for (mode of ["error", "tainted", "nothing", "never"]) {
    await assert.rejects(Lines.paintToBlob("<svg/>", size, 50));
  }
  console.log("ok");
})();
"""
    )


def test_a_change_that_took_a_while_can_reach_back_over_the_steps_recorded_meanwhile() -> None:
    _node(
        f"const Studio = require({json.dumps(str(STATE_JS))});\n"
        """
const assert = require("node:assert/strict");
const history = Studio.createHistory({ limit: 10 });
history.seed({ at: "empty", svg: null });
history.push({ at: "loaded", svg: "O" });
history.push({ at: "nudged", svg: "O" });
const amended = history.amendBack((entry) => (entry.svg === "O" ? { ...entry, svg: "L" } : null));
assert.equal(amended, true);
assert.deepEqual(history.current(), { at: "nudged", svg: "L" });
assert.deepEqual(history.undo(), { at: "loaded", svg: "L" });
assert.deepEqual(history.undo(), { at: "empty", svg: null });
assert.deepEqual(history.redo(), { at: "loaded", svg: "L" });
console.log("ok");
"""
    )


def test_plain_lines_stay_the_same_string_and_nothing_is_made() -> None:
    _run_section(
        """
answers["/api/svg/examine"] = LEAVE;
const file = pass("plain.svg", "<svg>plain</svg>");
addDrawings([file]);
assert.equal(file.makingLines.phase, "sorting");
assert.equal(linesSliceFootnote(), null);
await tick();
assert.equal(file.svg, "<svg>plain</svg>");
assert.equal(file.makingLines, null);
assert.ok(!asked.some((call) => call.path === "/api/svg/make-lines"));
assert.ok(counts.layout > 0);
assert.equal(layoutFiles()[0], file);
"""
    )


def test_loading_and_its_lines_are_one_undo_step() -> None:
    _run_section(
        """
answers["/api/svg/examine"] = CONVERT;
answers["/api/svg/make-lines"] = LINES;
const file = pass("cat.svg", "<svg>filled</svg>", { thumbUrl: "blob:old" });
addDrawings([file]);
await tick();
assert.equal(file.svg, CONVERTED);
assert.equal(file.makingLines, null);
assert.equal(file.thumbUrl, null);
assert.equal(file.measurementStatus, "pending");
assert.equal(asked.find((c) => c.path === "/api/svg/make-lines").body.target_mm, undefined);
assert.deepEqual(asked.find((c) => c.path === "/api/svg/make-lines").body.bed_mm, [381, 381]);
assert.equal(drawHistory.current().passes[0].svg, CONVERTED);
assert.equal(drawHistory.state().length, 2);
assert.deepEqual(drawHistory.undo().passes, []);
"""
    )


def test_two_files_loaded_close_together_each_keep_their_lines_through_an_undo() -> None:
    _run_section(
        """
const finish = [];
answers["/api/svg/examine"] = CONVERT;
const made = (name) => Lines.withLinesHash(CONVERTED.replace('data-clayline-target="100"', `data-clayline-target="${name}"`));
answers["/api/svg/make-lines"] = (body) => new Promise((resolve) => {
  finish.push(() => resolve(respond(200, { ...LINES, svg: body.svg === "<svg>a</svg>" ? made(1) : made(2) })));
});
const a = pass("a.svg", "<svg>a</svg>");
addDrawings([a]);
await tick();
assert.equal(finish.length, 1);
const b = pass("b.svg", "<svg>b</svg>");
addDrawings([b]);
await tick();
finish.shift()();
await tick();
assert.equal(a.svg, made(1));
finish.shift()();
await tick();
assert.equal(b.svg, made(2));
assert.deepEqual(drawHistory.current().passes.map((one) => one.svg), [made(1), made(2)]);
// One undo takes b away. a is still its lines, on the step from before b arrived.
assert.deepEqual(drawHistory.undo().passes.map((one) => one.svg), [made(1)]);
assert.equal(drawHistory.undo().passes.length, 0);
"""
    )


def test_a_load_never_reaches_back_into_another_pass_holding_the_same_file() -> None:
    _run_section(
        """
answers["/api/svg/examine"] = CONVERT;
answers["/api/svg/make-lines"] = LINES;
// The file itself, as the potter put it back with Use original, on its own step.
const kept = pass("cat.svg", "<svg>same</svg>");
setFiles([kept]);
addDrawings([pass("cat.svg", "<svg>same</svg>")]);
await tick();
assert.equal(state.files[0].svg, "<svg>same</svg>");
assert.equal(state.files[1].svg, CONVERTED);
assert.deepEqual(drawHistory.current().passes.map((one) => one.svg), ["<svg>same</svg>", CONVERTED]);
assert.deepEqual(drawHistory.undo().passes.map((one) => one.svg), ["<svg>same</svg>"]);
"""
    )


def test_every_waiting_pass_says_it_is_being_made_before_the_first_one_finishes() -> None:
    _run_section(
        """
let finish;
answers["/api/svg/examine"] = CONVERT;
answers["/api/svg/make-lines"] = () => new Promise((resolve) => { finish = () => resolve(respond(200, LINES)); });
const first = pass("one.svg", "<svg>one</svg>");
const second = pass("two.svg", "<svg>two</svg>");
addDrawings([first, second]);
await tick();
assert.equal(first.makingLines.phase, "making");
assert.equal(second.makingLines.phase, "making");
assert.equal(asked.filter((c) => c.path === "/api/svg/examine").length, 2);
assert.equal(asked.filter((c) => c.path === "/api/svg/make-lines").length, 1);
finish();
await tick();
assert.equal(first.svg, CONVERTED);
assert.equal(asked.filter((c) => c.path === "/api/svg/make-lines").length, 2);
finish();
await tick();
assert.equal(second.svg, CONVERTED);
assert.equal(first.makingLines, null);
assert.equal(second.makingLines, null);
"""
    )


def test_two_rows_of_the_same_file_share_one_answer() -> None:
    _run_section(
        """
answers["/api/svg/examine"] = CONVERT;
answers["/api/svg/make-lines"] = LINES;
const first = pass("one.svg", "<svg>same</svg>");
const second = pass("two.svg", "<svg>same</svg>");
addDrawings([first, second]);
await tick();
assert.equal(first.svg, CONVERTED);
assert.equal(second.svg, CONVERTED);
assert.equal(asked.filter((c) => c.path === "/api/svg/make-lines").length, 1);
"""
    )


def test_slice_is_off_with_its_reason_while_a_pass_is_being_made() -> None:
    _run_section(
        """
let finish;
answers["/api/svg/examine"] = CONVERT;
answers["/api/svg/make-lines"] = () => new Promise((resolve) => { finish = () => resolve(respond(200, LINES)); });
const first = pass("cat.svg", "<svg>filled</svg>");
addDrawings([first]);
await tick();
assert.equal(first.makingLines.phase, "making");
assert.equal(linesSliceFootnote(), "Making lines from your drawing — Slice is ready in a moment.");
assert.equal(linesNoteContent(first).text, "Making lines from your drawing…");
assert.equal(passOpensInDraw(first), false);
assert.equal(passSizeStaysOpen(first), false);
state.files = [first, pass("other.svg", "<svg>x</svg>")];
assert.equal(linesSliceFootnote(), "Making lines from cat.svg — Slice is ready in a moment.");
finish();
await tick();
"""
    )


def test_a_late_answer_for_a_pass_removed_meanwhile_is_ignored() -> None:
    _run_section(
        """
let finish;
answers["/api/svg/examine"] = CONVERT;
answers["/api/svg/make-lines"] = () => new Promise((resolve) => { finish = () => resolve(respond(200, LINES)); });
const file = pass("cat.svg", "<svg>filled</svg>");
addDrawings([file]);
await tick();
setFiles([]);
const steps = drawHistory.state().length;
finish();
await tick();
assert.equal(file.svg, "<svg>filled</svg>");
assert.equal(state.files.length, 0);
assert.equal(drawHistory.state().length, steps);
"""
    )


def test_a_job_follows_its_pass_when_undo_rebuilds_it() -> None:
    _run_section(
        """
let finish;
answers["/api/svg/examine"] = CONVERT;
answers["/api/svg/make-lines"] = () => new Promise((resolve) => { finish = () => resolve(respond(200, LINES)); });
const file = pass("cat.svg", "<svg>filled</svg>");
addDrawings([file]);
await tick();
const rebuilt = pass("cat.svg", "<svg>filled</svg>");
setFiles([rebuilt]);
assert.ok(rebuilt.makingLines);
assert.equal(file.makingLines, null);
finish();
await tick();
assert.equal(rebuilt.svg, CONVERTED);
"""
    )


def test_a_rebuild_at_another_size_drops_the_answer() -> None:
    _run_section(
        """
let finish;
answers["/api/svg/examine"] = CONVERT;
answers["/api/svg/make-lines"] = () => new Promise((resolve) => { finish = () => resolve(respond(200, LINES)); });
const file = pass("cat.svg", CONVERTED, { sizeMm: 300, sizePinned: true, measurementStatus: "ready" });
state.files = [file];
startLinesJob(file, "remake");
await tick();
const rebuilt = pass("cat.svg", CONVERTED, { sizeMm: 120, sizePinned: true });
setFiles([rebuilt]);
assert.equal(rebuilt.makingLines, undefined);
finish();
await tick();
assert.equal(rebuilt.svg, CONVERTED);
"""
    )


def test_a_size_and_its_lines_are_one_step_and_the_typed_size_is_what_is_asked_for() -> None:
    _run_section(
        """
const remade = Lines.withLinesHash(CONVERTED.replace('data-clayline-target="100"', 'data-clayline-target="240"'));
answers["/api/svg/examine"] = CONVERT;
answers["/api/svg/make-lines"] = { ...LINES, svg: remade, target_mm: 240 };
const file = pass("cat.svg", CONVERTED, { sizeMm: 100, measurementStatus: "ready" });
state.files = [file];
drawStateWriter.flush();
const steps = drawHistory.state().length;
setLinesSize(file, 240);
assert.equal(file.measurementStatus, "pending");
assert.equal(linesSliceFootnote(), "Making lines from your drawing — Slice is ready in a moment.");
await tick();
assert.equal(asked.find((c) => c.path === "/api/svg/make-lines").body.target_mm, 240);
assert.equal(file.svg, remade);
assert.equal(drawHistory.state().length, steps + 1);
assert.equal(drawHistory.current().passes[0].svg, remade);
assert.equal(drawHistory.undo().passes[0].svg, CONVERTED);
"""
    )


def test_a_size_changed_and_changed_back_while_it_is_sorted_still_ends_in_lines() -> None:
    _run_section(
        """
let finishFirst = null;
answers["/api/svg/examine"] = () => new Promise((resolve) => {
  if (!finishFirst) finishFirst = () => resolve(respond(200, CONVERT));
  else resolve(respond(200, CONVERT));
});
answers["/api/svg/make-lines"] = LINES;
const file = pass("cat.svg", CONVERTED, { sizeMm: 100, sizePinned: true, measurementStatus: "ready" });
state.files = [file];
setLinesSize(file, 200);
setLinesSize(file, 150);
setLinesSize(file, 200);
assert.ok(finishFirst);
finishFirst();
await tick();
// The same settings as the first, whose sort went nowhere: it gets lines of its own.
assert.equal(file.makingLines, null);
assert.ok(Lines.hasOriginal(file.svg));
assert.deepEqual(
  asked.filter((call) => call.path === "/api/svg/make-lines").map((call) => call.body.target_mm),
  [200],
);
"""
    )


def test_a_sort_alone_never_gives_a_job_that_wanted_lines_its_file_back() -> None:
    _run_section(
        """
answers["/api/svg/make-lines"] = LINES;
const file = pass("cat.svg", CONVERTED, { sizeMm: 100, sizePinned: true, measurementStatus: "ready" });
state.files = [file];
const job = readyLinesJob(file, "remake");
landLines(job, { answer: { ...CONVERT, sorted: true } });
// It stays lines, and goes on to the lines it was owed without sorting twice.
assert.ok(Lines.hasOriginal(file.svg));
assert.ok(file.makingLines);
await tick();
assert.equal(file.makingLines, null);
assert.ok(Lines.hasOriginal(file.svg));
assert.equal(asked.filter((call) => call.path === "/api/svg/examine").length, 0);
assert.equal(asked.filter((call) => call.path === "/api/svg/make-lines").length, 1);
"""
    )


def test_the_same_size_fed_back_asks_for_nothing() -> None:
    _run_section(
        """
const file = pass("cat.svg", CONVERTED, { sizeMm: 100, sizePinned: true, measurementStatus: "ready" });
state.files = [file];
remakeLinesIfStale(file);
assert.equal(file.makingLines, undefined);
assert.equal(asked.length, 0);
assert.equal(linesOutOfDate(file), false);
// A size that followed the drawing isn't a size anyone asked for, so it's never sent back.
file.sizePinned = false;
file.sizeMm = 96.5;
assert.equal(linesOutOfDate(file), false);
remakeLinesIfStale(file);
assert.equal(asked.length, 0);
"""
    )


def test_a_pass_edited_by_hand_is_never_remade() -> None:
    _run_section(
        """
const edited = '<svg data-clayline-converted="1" data-clayline-origin="edited" xmlns="x" viewBox="0 0 9 9"><path d="M0 0L9 9"/></svg>';
const file = pass("cat.svg", edited, { sizeMm: 100, sizePinned: true, measurementStatus: "ready" });
state.files = [file];
coil = 8;
remakeLinesIfStale(file);
noteCoilOrJoinChanged({ settled: true });
await tick();
assert.equal(file.makingLines, undefined);
assert.equal(asked.length, 0);
assert.equal(linesRowActions(file).length, 0);
"""
    )


def test_a_new_coil_width_makes_the_lines_again_and_undo_holds_both() -> None:
    _run_section(
        """
const remade = Lines.withLinesHash(CONVERTED.replace('data-clayline-coil="5"', 'data-clayline-coil="8"'));
answers["/api/svg/examine"] = CONVERT;
answers["/api/svg/make-lines"] = { ...LINES, svg: remade };
const file = pass("cat.svg", CONVERTED, { sizeMm: 96, measurementStatus: "ready" });
state.files = [file];
drawStateWriter.flush();
coil = 8;
noteCoilOrJoinChanged({ settled: false });
// Off at once, before any work has started.
assert.equal(file.makingLines.phase, "making");
assert.equal(file.measurementStatus, "pending");
assert.ok(linesSliceFootnote().startsWith("Making lines"));
noteCoilOrJoinChanged({ settled: true });
drawStateWriter.flush();
await tick();
assert.equal(asked.find((c) => c.path === "/api/svg/make-lines").body.coil_width_mm, 8);
assert.equal(file.svg, remade);
assert.equal(drawHistory.current().passes[0].svg, remade);
coil = 5;
assert.equal(drawHistory.undo().passes[0].svg, CONVERTED);
"""
    )


def test_a_typed_coil_put_back_before_the_pause_does_no_work() -> None:
    _run_section(
        """
const file = pass("cat.svg", CONVERTED, { sizeMm: 96, measurementStatus: "ready" });
state.files = [file];
coil = 8;
noteCoilOrJoinChanged({ settled: false });
assert.ok(file.makingLines);
coil = 5;
noteCoilOrJoinChanged({ settled: true });
await tick();
assert.equal(file.makingLines, null);
assert.equal(asked.length, 0);
"""
    )


def test_a_coil_box_left_empty_says_nothing_is_on_its_way_and_starts_again_on_a_number() -> None:
    _run_section(
        """
answers["/api/svg/examine"] = CONVERT;
answers["/api/svg/make-lines"] = LINES;
const file = pass("cat.svg", CONVERTED, { sizeMm: 96, measurementStatus: "ready" });
state.files = [file];
coil = 8;
noteCoilOrJoinChanged({ settled: false });
assert.ok(file.makingLines);
// Cleared, as it reads to the page: the box is 0, and its own footnote speaks.
coil = 0;
noteCoilOrJoinChanged({ settled: false });
assert.equal(file.makingLines, null);
assert.equal(linesOutOfDate(file), false);
assert.equal(linesSliceFootnote(), null);
assert.deepEqual(linesRowActions(file).map((b) => b.textContent), ["Use original"]);
noteCoilOrJoinChanged({ settled: true });
assert.equal(file.makingLines, null);
await tick();
assert.equal(asked.length, 0);
// The next number makes them for it.
coil = 8;
noteCoilOrJoinChanged({ settled: true });
assert.ok(file.makingLines);
await tick();
assert.equal(asked.find((c) => c.path === "/api/svg/make-lines").body.coil_width_mm, 8);
"""
    )


def test_scaled_to_fit_goes_when_the_measured_pass_no_longer_fits() -> None:
    _run_section(
        """
const measured = { sizeMm: 100, sourceLongestMm: 100, sourceWmm: 100, sourceHmm: 60, measurementStatus: "ready" };
const file = pass("cat.svg", CONVERTED, measured);
state.files = [file];
assert.equal(passOverBed(file), false);
assert.equal(passScaledToFit(file), true);
assert.equal(passWantsFitSize(file), false);
// On a printer it no longer fits, the same nozzle or not: no lines are remade.
state.profiles.set("test", { work_bounds: { min_x: 0, max_x: 90, min_y: 0, max_y: 90 } });
assert.equal(passOverBed(file), true);
assert.equal(passScaledToFit(file), false);
assert.equal(passWantsFitSize(file), true);
assert.equal(passFitSize(file), 70);
assert.equal(file.makingLines, undefined);
// A file with no lines to make isn't on offer, however big.
const plain = pass("p.svg", "<svg>lines</svg>", measured);
assert.equal(passWantsFitSize(plain), false);
"""
    )


@pytest.mark.parametrize(
    ("answer", "sentence", "steps", "button"),
    (
        (
            {
                "verdict": "photo",
                "sentence": "This looks like a photo, so there are no clean lines to follow.",
                "next": "trace",
            },
            "This looks like a photo, so there are no clean lines to follow.",
            "trace it, or remove it",
            "Trace over it",
        ),
        (
            {
                "verdict": "linked_picture",
                "sentence": "This file only links to its picture.",
                "next": "remove",
            },
            "This file only links to its picture.",
            "remove it",
            "Remove this pass",
        ),
        (
            {
                "verdict": "nothing",
                "nothing_to_draw": True,
                "sentence": "This file has nothing to draw.",
                "next": "remove",
            },
            "This file has nothing to draw.",
            "set its size, or remove it",
            "Remove this pass",
        ),
    ),
    ids=("photo", "linked", "nothing"),
)
def test_with_nothing_to_print_the_row_says_why_and_offers_the_step(
    answer: dict[str, Any], sentence: str, steps: str, button: str
) -> None:
    _run_section(
        f"""
answers["/api/svg/examine"] = CONVERT;
answers["/api/svg/make-lines"] = {json.dumps(answer)};
const file = pass("cat.svg", "<svg>filled</svg>");
addDrawings([file]);
await tick();
assert.equal(Lines.withoutAnswer(file.svg), "<svg>filled</svg>");
assert.equal(linesSourceOf(file), "<svg>filled</svg>");
assert.equal(file.makingLines, null);
assert.deepEqual(layoutFiles(), []);
assert.equal(passOpensInDraw(file), false);
const note = linesNoteContent(file);
assert.equal(note.text, {json.dumps(sentence)});
assert.ok(note.tip && note.tip !== note.text);
assert.deepEqual(note.buttons.map((b) => b.textContent), [{json.dumps(button)}]);
assert.equal(linesSliceFootnote(), {json.dumps(f"Nothing to print in cat.svg — {steps}.")});
// A rebuilt pass finds the same words, with no new question to the engine.
const calls = asked.length;
state.files = [pass("cat.svg", "<svg>filled</svg>")];
assert.equal(linesNoteContent(state.files[0]).text, {json.dumps(sentence)});
assert.equal(asked.length, calls);
// So does a project opened in a new session, off the pass alone.
state.linesAnswers.clear();
const reopened = pass("cat.svg", file.svg);
state.files = [reopened];
assert.equal(linesNoteContent(reopened).text, {json.dumps(sentence)});
assert.deepEqual(linesNoteContent(reopened).buttons.map((b) => b.textContent), [{json.dumps(button)}]);
assert.equal(linesSliceFootnote(), {json.dumps(f"Nothing to print in cat.svg — {steps}.")});
assert.equal(passMayPaint(reopened), true);
askAboutUnsortedPasses();
await tick();
assert.equal(asked.length, calls);
// And the load and its answer are one step.
assert.equal(drawHistory.current().passes[0].svg, file.svg);
assert.equal(drawHistory.undo().passes.length, 0);
"""
    )


def test_a_file_that_may_never_finish_painting_is_not_painted_or_offered_for_tracing() -> None:
    _run_section(
        """
answers["/api/svg/examine"] = { verdict: "too_large", reason: "too_many_repeats", next: "remove", sentence: "This file is too large for Clayline. Save a simpler copy from your drawing program, or trace over it." };
const file = pass("bomb.svg", "<svg>repeats</svg>");
addDrawings([file]);
assert.equal(passMayPaint(file), false);
await tick();
assert.equal(passMayPaint(file), false);
const note = linesNoteContent(file);
assert.equal(note.text, "This file is too large for Clayline. Save a simpler copy from your drawing program.");
assert.deepEqual(note.buttons.map((b) => b.textContent), ["Remove this pass"]);
assert.ok(!asked.some((call) => call.path === "/api/svg/make-lines"));
"""
    )


def test_too_short_to_print_fills_in_its_size_and_a_press_that_changes_nothing_is_not_offered() -> (
    None
):
    _run_section(
        """
const words = "At this size the lines are too short to print. It prints from about {size}.";
answers["/api/svg/examine"] = CONVERT;
answers["/api/svg/make-lines"] = { verdict: "too_small", sentence: words, sentence_kind: "too_short", next: "set_size", suggested_mm: 20, target_mm: 6.3 };
const file = pass("icon.svg", "<svg>icon</svg>");
addDrawings([file]);
await tick();
let note = linesNoteContent(file);
assert.equal(note.text, "At this size the lines are too short to print. It prints from about 20 mm.");
assert.deepEqual(note.buttons.map((b) => b.textContent), ["Set Size"]);
assert.equal(passSizeStaysOpen(file), true);
assert.equal(linesSliceFootnote(), "Nothing to print in icon.svg — set its size, or remove it.");
// The engine can name the size already typed. Then its words wouldn't be true.
file.sizeMm = 20;
file.sizePinned = true;
note = linesNoteContent(file);
assert.equal(note.text, "At this size the lines are too short to print. Type a bigger size.");
assert.deepEqual(note.buttons, []);
"""
    )


def test_the_row_says_the_size_sentence_as_itself_and_offers_no_try_again() -> None:
    _run_section(
        """
answers["/api/svg/examine"] = CONVERT;
answers["/api/svg/make-lines"] = () => respond(422, { detail: LINES_SIZE_TOO_BIG });
const file = pass("cat.svg", CONVERTED, { sizeMm: 9000, sizePinned: true, measurementStatus: "ready" });
state.files = [file];
startLinesJob(file, "remake");
await tick();
assert.equal(file.linesFailed, false);
assert.equal(linesNoteContent(file).text, "That size is too big for this drawing. Type a smaller size.");
assert.deepEqual(linesNoteContent(file).buttons, []);
assert.equal(passSizeStaysOpen(file), true);
assert.equal(linesSliceFootnote(), "cat.svg needs a smaller size.");
assert.equal(linesRowActions(file).length, 1);
"""
    )


def test_a_size_past_any_bed_is_refused_at_the_box_only_for_a_pass_of_made_lines() -> None:
    _run_section(
        """
const made = pass("cat.svg", CONVERTED, { sizeMm: 100, measurementStatus: "ready" });
assert.equal(linesSizeRefusal(made, 10001), LINES_SIZE_TOO_BIG);
assert.equal(linesSizeRefusal(made, 10000), null);
assert.equal(linesSizeRefusal(made, 0.5), "Type a size of at least 1 mm.");
const plain = pass("plain.svg", "<svg>plain</svg>", { measurementStatus: "ready" });
assert.equal(linesSizeRefusal(plain, 20000), null);
"""
    )


def test_any_other_refusal_or_a_broken_connection_gets_the_plain_failure_row() -> None:
    _run_section(
        """
answers["/api/svg/examine"] = CONVERT;
answers["/api/svg/make-lines"] = () => respond(422, { detail: "bed_mm must be two positive numbers" });
const file = pass("cat.svg", "<svg>filled</svg>");
addDrawings([file]);
await tick();
assert.equal(file.linesFailed, "load");
const note = linesNoteContent(file);
assert.equal(note.text, "Clayline couldn't make lines from this drawing.");
assert.deepEqual(note.buttons.map((b) => b.textContent), ["Try again", "Use original"]);
assert.equal(linesSliceFootnote(), "Clayline couldn't make lines from cat.svg — try again, or use the original.");
answers["/api/svg/make-lines"] = LINES;
tryLinesAgain(file);
await tick();
assert.equal(file.svg, CONVERTED);
assert.equal(file.linesFailed, false);
"""
    )


def test_use_original_puts_the_file_back_as_its_own_step_and_offers_make_lines_again() -> None:
    _run_section(
        """
answers["/api/svg/examine"] = CONVERT;
answers["/api/svg/make-lines"] = LINES;
const original = Lines.originalOf(CONVERTED);
const file = pass("cat.svg", CONVERTED, { sizeMm: 100, sizePinned: true, measurementStatus: "ready", thumbUrl: "blob:lines" });
state.files = [file];
drawStateWriter.flush();
const steps = drawHistory.state().length;
assert.deepEqual(linesRowActions(file).map((b) => b.textContent), ["Use original"]);
useOriginal(file);
assert.equal(file.svg, original);
assert.equal(file.thumbUrl, null);
assert.equal(file.sizePinned, false);
assert.equal(file.sizeMm, null);
assert.equal(drawHistory.state().length, steps + 1);
assert.deepEqual(linesRowActions(file).map((b) => b.textContent), ["Make lines again"]);
// Making them again is its own step too.
makeLinesAgain(file);
await tick();
assert.equal(file.svg, CONVERTED);
assert.equal(drawHistory.state().length, steps + 2);
assert.equal(drawHistory.undo().passes[0].svg, original);
"""
    )


def test_the_sentence_and_size_come_from_the_drawing_with_no_answer_remembered() -> None:
    _run_section(
        """
// A pass as a project hands it back in a new session.
const file = pass("cat.svg", CONVERTED, { sizeMm: 120, measurementStatus: "ready" });
state.files = [file];
const note = linesNoteContent(file);
assert.equal(note.text, "At this size, 17 of 19 small gaps fill in. It reads well from about 240 mm.");
assert.deepEqual(note.buttons.map((b) => b.textContent), ["Set Size"]);
assert.ok(note.tip && note.tip !== note.text);
assert.equal(passScaledToFit(file), true);
assert.deepEqual(linesRowActions(file).map((b) => b.textContent), ["Use original"]);
assert.equal(asked.length, 0);
askAboutUnsortedPasses();
await tick();
assert.equal(asked.length, 0);
"""
    )


def test_clayline_s_own_saved_file_comes_back_as_it_was_saved() -> None:
    _run_section(
        """
const edited = CONVERTED
  .replace(/<metadata[\\s\\S]*?<\\/metadata>\\n?/, "")
  .replace(/ data-clayline-lines-hash="[^"]*"/, "")
  .replace("<svg ", '<svg data-clayline-origin="edited" ');
const traced = '<svg data-clayline-converted="1" data-clayline-origin="drawn" xmlns="x"><path d="M0 0L9 9"/></svg>';
const saved = pass("cat-lines.svg", CONVERTED);
const hand = pass("hand.svg", edited);
const page = pass("page.svg", traced);
addDrawings([saved, hand, page]);
await tick();
assert.equal(asked.length, 0);
assert.equal(saved.svg, CONVERTED);
assert.equal(hand.svg, edited);
assert.equal(page.svg, traced);
for (const file of [saved, hand, page]) {
  assert.equal(file.makingLines, undefined);
  assert.ok(!file.linesFailed);
  assert.equal(passHeldByLines(file), false);
  assert.equal(linesOutOfDate(file), false);
  // The mark that keeps a save off the source is still there.
  assert.equal(Lines.isConverted(file.svg), true);
}
assert.equal(linesSliceFootnote(), null);
// Only the file that still holds its original has one to go back to.
assert.deepEqual(linesRowActions(saved).map((b) => b.textContent), ["Use original"]);
assert.deepEqual(linesRowActions(hand).map((b) => b.textContent), []);
assert.deepEqual(linesRowActions(page).map((b) => b.textContent), []);
// Nothing goes on to make lines from the file hidden inside on its own.
state.files = [saved, hand, page];
askAboutUnsortedPasses();
await tick();
assert.equal(asked.length, 0);
"""
    )


def test_saved_lines_at_a_typed_size_come_back_at_that_size() -> None:
    _run_section(
        """
const typed = Lines.withLinesHash(CONVERTED.replace('data-clayline-size-basis="fit"', 'data-clayline-size-basis="typed"').replace('data-clayline-target="100"', 'data-clayline-target="140"'));
const saved = pass("cat-lines.svg", typed);
const fitted = pass("dog-lines.svg", CONVERTED);
addDrawings([saved, fitted]);
await tick();
assert.equal(asked.length, 0);
assert.equal(saved.svg, typed);
assert.equal(saved.sizeMm, 140);
assert.equal(saved.sizePinned, true);
assert.equal(typedLinesSize(saved), 140);
assert.equal(linesOutOfDate(saved), false);
// A size Clayline chose stays Clayline's to change.
assert.equal(fitted.sizePinned, false);
"""
    )


def test_saved_lines_added_at_another_coil_say_so_and_print_nothing_until_asked() -> None:
    _run_section(
        """
coil = 3.5;
const saved = pass("cat-lines.svg", CONVERTED);
addDrawings([saved]);
await tick();
assert.equal(asked.length, 0);
assert.equal(saved.svg, CONVERTED);
assert.equal(linesNoteContent(saved).text, "These lines were made for another size or coil width.");
assert.deepEqual(linesRowActions(saved).map((b) => b.textContent), ["Use original", "Make lines again"]);
assert.match(linesSliceFootnote(), /Press Make lines again/);
"""
    )


def test_a_pass_with_no_answer_yet_is_only_asked_what_it_is() -> None:
    _run_section(
        """
answers["/api/svg/examine"] = CONVERT;
const file = pass("kept.svg", "<svg>filled</svg>");
state.files = [file];
assert.equal(passMayPaint(file), false);
askAboutUnsortedPasses();
askAboutUnsortedPasses();
await tick();
assert.equal(asked.length, 1);
assert.equal(asked[0].path, "/api/svg/examine");
assert.equal(file.svg, "<svg>filled</svg>");
assert.equal(file.makingLines, undefined);
assert.equal(passMayPaint(file), true);
assert.deepEqual(linesRowActions(file).map((b) => b.textContent), ["Make lines again"]);
// A page Clayline drew is nobody's file, so there's nothing to ask.
const drawn = pass("d.svg", '<svg data-clayline-origin="drawn" xmlns="x"/>');
state.files = [drawn];
askAboutUnsortedPasses();
await tick();
assert.equal(asked.length, 1);
"""
    )


def _block(text: str, start: str, end: str) -> str:
    return text.split(start, 1)[1].split(end, 1)[0]


def _lift_saving(extra: str) -> str:
    saving = "  const nativeSave = () =>" + _block(
        DRAW, "  const nativeSave = () =>", "  /* ---------- wiring"
    )
    return _node(
        'const assert = require("node:assert/strict");\n'
        f"const Lines = require({json.dumps(str(LINES_JS))});\n"
        f"const CONVERTED = {json.dumps(CONVERTED)};\n"
        """
const posted = [];
const downloads = [];
globalThis.window = {
  webkit: { messageHandlers: { claylineSaveSVG: { postMessage: (m) => posted.push(m) } } },
  ClaylineShapeLines: Lines,
  setTimeout: () => 0,
};
globalThis.URL = { createObjectURL: () => "blob:x", revokeObjectURL() {} };
globalThis.Blob = class {};
globalThis.document = {
  createElement: () => ({ set download(name) { downloads.push(name); }, click() {}, remove() {} }),
  body: { append() {} },
};
const ORIGIN_RE = /data-clayline-origin="([a-z]+)"/;
const originOf = (svg) => (ORIGIN_RE.exec(String(svg || "")) || [])[1] || "";
const isConverted = (svg) => Lines.isConverted(svg);
const SAVE_LINES_TIP = "Saves the lines Clayline made as a new file. Your original file is not changed.";
let files = [];
const host = {
  files: () => files,
  markDirty() {},
  saveMustAsk: (file) => Boolean(file.makingLines) || Boolean(file.wants),
};
"""
        f"{saving}\n{extra}\n"
        'console.log("ok");\n'
    )


def test_a_save_on_made_lines_asks_where_and_never_uses_the_shell_that_writes_over_the_source() -> (
    None
):
    _lift_saving(
        """
files = [{ name: "cat.svg", svg: CONVERTED }];
assert.equal(saveLabel(files[0]), "Save SVG…");
assert.equal(saveTip(files[0]), SAVE_LINES_TIP);
saveSVG(0);
assert.equal(posted.length, 0);
assert.deepEqual(downloads, ["cat-lines.svg"]);
// Saved lines added again keep the one name, however many times round.
files = [{ name: "cat-lines.svg", svg: CONVERTED }];
saveSVG(0);
assert.equal(downloads.at(-1), "cat-lines.svg");
downloads.pop();
// The same once it has been edited by hand: commit puts the mark back every time.
const edited = '<svg data-clayline-converted="1" data-clayline-origin="edited" xmlns="x"></svg>';
files = [{ name: "cat.svg", svg: edited }];
assert.equal(saveLabel(files[0]), "Save SVG…");
saveSVG(0);
assert.equal(posted.length, 0);
assert.equal(downloads.length, 2);
"""
    )


def test_a_file_that_wants_lines_or_is_still_being_sorted_asks_where_to_save() -> None:
    assert (
        'saveMustAsk: (file) => Boolean(file.makingLines) || passLinesAnswer(file)?.verdict === "convert",'
        in APP
    )
    _lift_saving(
        """
// Use original put a filled file back: its name may still point at saved lines.
files = [{ name: "square-lines.svg", svg: "<svg xmlns='x'></svg>", wants: true }];
saveSVG(0);
assert.equal(posted.length, 0);
assert.deepEqual(downloads, ["square-lines.svg"]);
// Still being sorted: nobody knows yet, and a save may not change the file on disk.
files = [{ name: "square.svg", svg: "<svg xmlns='x'></svg>", makingLines: {} }];
saveSVG(0);
assert.equal(posted.length, 0);
assert.equal(downloads.at(-1), "square.svg");
// An ordinary file, with its sort done, goes where it always has.
files = [{ name: "plain.svg", svg: "<svg xmlns='x'></svg>" }];
saveSVG(0);
assert.equal(posted.length, 1);
"""
    )


def test_a_save_on_an_ordinary_edited_file_still_goes_through_the_shell() -> None:
    _lift_saving(
        """
const edited = '<svg data-clayline-origin="edited" xmlns="x"></svg>';
files = [{ name: "cat.svg", svg: edited }];
assert.equal(saveLabel(files[0]), "Save over original");
saveSVG(0);
assert.equal(posted.length, 1);
assert.equal(downloads.length, 0);
"""
    )


def test_only_the_file_picker_and_the_native_open_can_start_a_conversion() -> None:
    assert APP.count("addDrawings(") == 3  # the function, readFiles and desktopImport
    read_files = _block(APP, "async function readFiles", "function movePageSource")
    assert "addDrawings(loaded)" in read_files
    desktop = _block(APP, "function desktopImport", "/* ---------- project files")
    assert "addDrawings(loaded)" in desktop
    for block in (
        _block(APP, "function applyDrawSettings", "function restoreDrawSettings"),
        _block(APP, "function repeatPass", "function pageRow"),
        _block(APP, "async function applyDrawProject", "function sliceOpenedProjectWhenReady"),
        _block(DRAW, "function openNew", "// Trace over it:"),
    ):
        for call in ("addDrawings", "startLinesJob", "readyLinesJob"):
            assert call not in block


def test_the_original_never_counts_against_a_request_and_measurements_key_on_a_hash() -> None:
    assert "svg: Lines.withoutOriginal(file.svg)," in _block(
        APP, "async function runLayoutCheck", "function bedMapFrame"
    )
    assert "svg: Lines.withoutOriginal(pass.svg)," in _block(
        APP, "function requestPayload", "function applyDrawSettings"
    )
    key = _block(APP, "function sourceMeasurementKey", "function hydratePassMeasurement")
    assert "passHash(file)" in key
    assert "file.svg" not in key
    # Neither remembered: what a pass is being made into isn't part of its snapshot.
    snapshot = _block(APP, "function drawSettingsSnapshot", "function sameKeys")
    for field in ("makingLines", "linesFailed", "linesWantCoil", "linesProblem", "svgHash"):
        assert field not in snapshot


def test_the_tag_has_a_line_of_its_own_and_its_tooltip_says_something_new() -> None:
    meta = _block(APP, "function updatePageMeta", "function applySelectionClasses")
    assert 'tag.title = madeLines ? LINES_MADE_TIP : "";' in meta
    assert '"scaled to fit"' in meta
    assert "if (mark && !madeLines) parts.push(mark);" in meta
    assert 'tagLine.className = "page-row-tag";' in APP
    assert "lines made from your drawing" in DRAW


def test_the_caption_about_slicing_goes_whenever_slice_can_not_run() -> None:
    caption = _block(APP, "function syncLinesCaption", "// In the empty middle of the window")
    for reason in (
        "making",
        "!linesCoilAndJoinAreSet()",
        "Boolean(linesSliceFootnote())",
        '$("#sliceButton").disabled',
    ):
        assert reason in caption
    assert "syncLinesCaption();" in _block(
        APP, "function syncLinesPreview", "async function readFiles"
    )
    # Slice's state is worked out in one place, and the caption follows it there.
    sets_slice = APP.index('$("#sliceButton").disabled = !canSlice || state.isSlicing;')
    assert APP.index("syncLinesCaption();", sets_slice) - sets_slice < 80


def test_the_size_check_waits_for_lines_and_a_commit_keeps_the_mark() -> None:
    schedule = _block(APP, "function scheduleLayoutCheck", "async function runLayoutCheck")
    assert "if (anyPassMakingLines()) return;" in schedule
    assert "if (state.layoutHeld) return;" in schedule
    hold = _block(APP, "holdLayoutCheck: (held) =>", "lastPlanHit:")
    assert "makingLines" not in hold
    commit = _block(DRAW, "function commit()", "function schedulePages")
    assert "withConverted(written)" in commit
    assert "this.makingLines" not in APP
    assert 'measurementStatus = "making' not in APP


PLAN_WORDS_IN_THE_PAGE = (
    "Making lines from your drawing…",
    "Still working — big drawings take longer.",
    "— Slice is ready in a moment.",
    "Clayline couldn't make lines from this drawing.",
    "lines made from your drawing",
    "Put your file back exactly as you added it. The lines Clayline made are removed.",
    "The longest side of this pass. It follows the drawing until you type a size.",
    "Scaled to fit your bed. Type a size to change it.",
    "Editing keeps your changes. Undo returns the lines Clayline made.",
    "Saves the lines Clayline made as a new file. Your original file is not changed.",
    "Press Slice when you're ready.",
    "Nothing to print in ${stuck.name} — ${steps}.",
    "is a picture, not a drawing. Trace over it in Draw.",
    "These are normal. Lines in your drawing cross or touch here.",
    "Where lines meet",
    "These are the lines Clayline will print. Press Slice to build the print.",
    "Drop in a drawing — lines, shapes or text. Shapes become lines you can check before slicing.",
    "Add a drawing. Each one becomes a pass, in the order you add them.",
)

DEVELOPER_WORDS = (
    "centerline",
    "stroke",
    "engine",
    "pixel",
    "medial",
    "voronoi",
    "lint",
    "svg element",
)


@pytest.mark.parametrize("words", PLAN_WORDS_IN_THE_PAGE)
def test_the_plan_words_are_on_the_page(words: str) -> None:
    assert words in APP or words in DRAW or words in HTML


def _shown_words() -> list[str]:
    # Everything in this section a potter can read is a whole quoted sentence.
    quoted = re.findall(r'"([^"\n]*[a-z] [a-z][^"\n]*)"|`([^`\n]*[a-z] [a-z][^`\n]*)`', SECTION)
    return [one or other for one, other in quoted]


def test_no_words_a_potter_reads_are_developers_words() -> None:
    shown = _shown_words()
    assert len(shown) > 25
    for sentence in shown:
        lowered = sentence.lower()
        for word in DEVELOPER_WORDS:
            assert word not in lowered, sentence
    for sentence in ("Fill-only shapes are reported", "Centerline SVGs only", "centerline SVG"):
        assert sentence not in HTML
    assert "Filled shapes without" not in APP
    assert "Ignored ${rejected.length}" not in APP


def test_a_final_check_failure_reads_in_plain_words_with_its_detail_in_small_print(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from clayline import workflow
    from clayline.stack import StackError

    def fails(_request: Any) -> None:
        raise StackError("combined job failed independent G-code lint:\nline 88: a finding")

    monkeypatch.setattr(workflow, "build_pipeline", fails)
    line = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="50mm" height="50mm" viewBox="0 0 50 50">'
        '<path d="M5 5H45" fill="none" stroke="#000"/></svg>'
    )
    with pytest.raises(webui.UiRequestError) as caught:
        webui._slice_payload({"files": [{"name": "a.svg", "svg": line}]})
    assert caught.value.detail["message"] == (
        "Clayline's final check found a problem it could not repair, so nothing was exported. "
        "Try a different size or coil width."
    )
    assert caught.value.detail["code"] == "emission_lint_failed"
    assert "line 88: a finding" in caught.value.detail["data"]["technical"]["message"]
    for word in ("lint", "g-code", "stroke", "engine"):
        assert word not in caught.value.detail["message"].lower()
    show = _block(APP, "function showSliceError", "async function loadProfiles")
    assert "technical.hidden = !detail;" in show
    assert 'id="errorTechnical"' in HTML


def test_a_slice_refused_for_another_reason_keeps_its_own_words(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from clayline import workflow
    from clayline.stack import StackError

    def fails(_request: Any) -> None:
        raise StackError(
            "The lines in this drawing are too short to print. Make the drawing bigger."
        )

    monkeypatch.setattr(workflow, "build_pipeline", fails)
    line = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="50mm" height="50mm" viewBox="0 0 50 50">'
        '<path d="M5 5H45" fill="none" stroke="#000"/></svg>'
    )
    with pytest.raises(StackError, match="too short to print"):
        webui._slice_payload({"files": [{"name": "a.svg", "svg": line}]})


def _painted_square() -> bytes:
    import io

    from PIL import Image, ImageDraw

    picture = Image.new("RGBA", (1000, 1000), (0, 0, 0, 0))
    ImageDraw.Draw(picture).rectangle((250, 250, 750, 750), fill=(0, 0, 0, 255))
    out = io.BytesIO()
    picture.save(out, format="PNG")
    return out.getvalue()


def test_the_lines_say_where_the_files_own_page_lands_under_them() -> None:
    # A real kept line tells the two frames apart: its ends go through the same sums.
    file = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="200mm" height="200mm" viewBox="0 0 200 200">'
        '<rect x="50" y="50" width="100" height="100" fill="#000"/>'
        '<path d="M20 20L180 20" fill="none" stroke="#000" stroke-width="1"/></svg>'
    )
    from clayline.shape_lines import examine

    canvas = examine(file)["canvas"]
    import io

    from PIL import Image, ImageDraw

    picture = Image.new("RGBA", (canvas["width"], canvas["height"]), (0, 0, 0, 0))
    ImageDraw.Draw(picture).rectangle(
        (
            0.1 * canvas["width"],
            0.1 * canvas["height"],
            0.9 * canvas["width"],
            0.9 * canvas["height"],
        ),
        fill=(0, 0, 0, 255),
    )
    out = io.BytesIO()
    picture.save(out, format="PNG")
    answer = make_lines(file, out.getvalue(), bead=5.0)
    assert answer["verdict"] == "lines"
    place = re.search(r'data-clayline-place="([^"]+)"', answer["svg"])
    assert place is not None
    left, top, final, margin, page_width, page_height = map(float, place.group(1).split())
    assert (page_width, page_height) == pytest.approx((200 * 96 / 25.4, 200 * 96 / 25.4), rel=1e-6)
    # Marks come before the <metadata>, because Draw's reader matches by pattern.
    assert answer["svg"].index("data-clayline-place") < answer["svg"].index("<metadata")
    # The kept line, placed by the same numbers the page uses for the faded copy.
    start = re.search(r'id="from-shape-\d+" d="M ([\d.]+) ([\d.]+) L [\d.]+ [\d.]+"', answer["svg"])
    assert start is not None
    to_page_mm = 25.4 / 96
    x = (float(start.group(1)) - margin) / final + left
    y = (float(start.group(2)) - margin) / final + top
    assert x * to_page_mm == pytest.approx(20.0, abs=0.5)
    assert y * to_page_mm == pytest.approx(20.0, abs=0.5)


# --- the coil box empty when a drawing arrives ------------------------------------


def test_a_drawing_added_with_the_coil_box_empty_waits_and_a_number_starts_it() -> None:
    _run_section(
        """
answers["/api/svg/examine"] = CONVERT;
answers["/api/svg/make-lines"] = LINES;
coil = 0;
const file = pass("cat.svg", "<svg>filled</svg>");
addDrawings([file]);
await tick();
// Sorted, since that asks for no coil, and nothing else went out.
assert.deepEqual(asked.map((c) => c.path), ["/api/svg/examine"]);
assert.equal(file.svg, "<svg>filled</svg>");
assert.equal(file.makingLines, null);
assert.equal(file.linesFailed, false);
assert.equal(passHeldByLines(file), true);
assert.equal(layoutFiles().length, 0);
const note = linesNoteContent(file);
assert.equal(note.text, "Type a coil width to make lines from this drawing.");
assert.equal(note.role, "status");
assert.deepEqual(note.buttons, []);
assert.deepEqual(linesRowActions(file), []);
assert.equal(linesSliceFootnote(), "Type a coil width before Slice.");
// Half a number is still no number.
coil = 0.05;
noteCoilOrJoinChanged({ settled: false });
assert.equal(file.makingLines, null);
assert.equal(linesNoteContent(file).text, "Type a coil width to make lines from this drawing.");
// The number starts it, with nothing more to press.
coil = 5;
noteCoilOrJoinChanged({ settled: false });
assert.equal(file.makingLines.phase, "making");
assert.equal(linesNoteContent(file).text, "Making lines from your drawing…");
noteCoilOrJoinChanged({ settled: true });
await tick();
assert.equal(asked.find((c) => c.path === "/api/svg/make-lines").body.coil_width_mm, 5);
assert.equal(file.svg, CONVERTED);
assert.equal(file.linesWantCoil, false);
assert.equal(passHeldByLines(file), false);
assert.equal(linesSliceFootnote(), null);
"""
    )


def test_the_number_and_the_lines_it_started_are_one_undo_step() -> None:
    _run_section(
        """
answers["/api/svg/examine"] = CONVERT;
answers["/api/svg/make-lines"] = LINES;
coil = 0;
const file = pass("cat.svg", "<svg>filled</svg>");
addDrawings([file]);
await tick();
coil = 5;
noteCoilOrJoinChanged({ settled: true });
drawStateWriter.flush();
await tick();
assert.equal(drawHistory.current().passes[0].svg, CONVERTED);
assert.equal(drawHistory.current().job.bead_width_mm, 5);
const before = drawHistory.undo();
assert.equal(before.passes[0].svg, "<svg>filled</svg>");
assert.equal(before.job.bead_width_mm, 0);
"""
    )


def test_clearing_the_box_again_goes_back_to_waiting_and_says_so() -> None:
    _run_section(
        """
answers["/api/svg/examine"] = CONVERT;
coil = 0;
const file = pass("cat.svg", "<svg>filled</svg>");
addDrawings([file]);
await tick();
coil = 5;
noteCoilOrJoinChanged({ settled: false });
assert.equal(linesNoteContent(file).text, "Making lines from your drawing…");
coil = 0;
noteCoilOrJoinChanged({ settled: false });
assert.equal(file.makingLines, null);
assert.equal(linesNoteContent(file).text, "Type a coil width to make lines from this drawing.");
await tick();
assert.equal(asked.filter((c) => c.path === "/api/svg/make-lines").length, 0);
"""
    )


def test_a_number_that_comes_while_the_file_is_sorted_is_the_one_used() -> None:
    _run_section(
        """
answers["/api/svg/examine"] = () => {
  coil = 6;
  return respond(200, CONVERT);
};
answers["/api/svg/make-lines"] = LINES;
coil = 0;
const file = pass("cat.svg", "<svg>filled</svg>");
addDrawings([file]);
await tick();
const made = asked.filter((c) => c.path === "/api/svg/make-lines");
assert.equal(made.length, 1);
assert.equal(made[0].body.coil_width_mm, 6);
assert.equal(file.svg, CONVERTED);
"""
    )


def test_a_box_emptied_before_its_turn_sends_nothing() -> None:
    _run_section(
        """
answers["/api/svg/examine"] = () => {
  coil = 0;
  return respond(200, CONVERT);
};
coil = 5;
const file = pass("cat.svg", "<svg>filled</svg>");
addDrawings([file]);
await tick();
assert.equal(asked.filter((c) => c.path === "/api/svg/make-lines").length, 0);
assert.equal(file.linesWantCoil, true);
"""
    )


def test_every_way_of_asking_for_lines_waits_for_the_box() -> None:
    _run_section(
        """
answers["/api/svg/examine"] = CONVERT;
answers["/api/svg/make-lines"] = () => respond(422, { detail: "bed_mm must be two positive numbers" });
const failed = pass("failed.svg", "<svg>failed</svg>");
addDrawings([failed]);
await tick();
assert.equal(failed.linesFailed, "load");
const madeCount = () => asked.filter((c) => c.path === "/api/svg/make-lines").length;
const before = madeCount();
coil = 0;
// Try again.
tryLinesAgain(failed);
await tick();
assert.equal(failed.linesFailed, false);
assert.equal(failed.linesWantCoil, true);
// Make lines again.
const again = pass("again.svg", CONVERTED, { sizeMm: 96, measurementStatus: "ready" });
state.files = [failed, again];
makeLinesAgain(again);
await tick();
assert.equal(again.linesWantCoil, true);
// A new size. These lines still can't be used, and it can still be set back.
const sized = pass("sized.svg", CONVERTED, { sizeMm: 96, measurementStatus: "ready" });
state.files = [failed, again, sized];
setLinesSize(sized, 240);
await tick();
assert.equal(sized.linesWantCoil, true);
assert.equal(sized.svg, CONVERTED);
assert.equal(passSizeStaysOpen(sized), true);
assert.equal(passSizeStaysOpen(failed), false);
assert.deepEqual(linesNoteContent(sized).buttons.map((b) => b.textContent), ["Use original"]);
assert.equal(madeCount(), before);
// One number, and each goes on its way for its own size.
answers["/api/svg/make-lines"] = LINES;
coil = 5;
noteCoilOrJoinChanged({ settled: true });
await tick();
for (const file of [failed, again, sized]) assert.equal(file.linesWantCoil, false);
assert.equal(failed.svg, CONVERTED);
assert.equal(asked.filter((c) => c.path === "/api/svg/make-lines").at(-1).body.target_mm, 240);
"""
    )


def test_a_pass_put_back_with_use_original_stays_as_it_is_when_a_coil_is_typed() -> None:
    _run_section(
        """
answers["/api/svg/examine"] = CONVERT;
answers["/api/svg/make-lines"] = LINES;
const file = pass("cat.svg", CONVERTED, { sizeMm: 96, measurementStatus: "ready" });
state.files = [file];
coil = 0;
useOriginal(file);
const original = Lines.originalOf(CONVERTED);
assert.equal(file.svg, original);
assert.equal(file.linesWantCoil, false);
coil = 8;
noteCoilOrJoinChanged({ settled: true });
await tick();
assert.equal(asked.length, 0);
assert.equal(file.svg, original);
// It waited, then the potter chose the file instead: no lines come for it after all.
const waiting = pass("dog.svg", "<svg>dog</svg>");
coil = 0;
addDrawings([waiting]);
await tick();
assert.equal(waiting.linesWantCoil, true);
useOriginal(waiting);
assert.equal(waiting.linesWantCoil, false);
const sofar = asked.length;
coil = 8;
noteCoilOrJoinChanged({ settled: true });
await tick();
assert.equal(asked.length, sofar);
"""
    )


def test_a_coil_the_engine_turned_down_is_tried_again_only_when_the_number_changes() -> None:
    _run_section(
        """
answers["/api/svg/examine"] = CONVERT;
answers["/api/svg/make-lines"] = () => respond(422, { detail: "coil_width_mm must be at most 100" });
coil = 500;
const file = pass("cat.svg", "<svg>filled</svg>");
addDrawings([file]);
await tick();
assert.equal(file.linesFailed, "load");
const count = () => asked.filter((c) => c.path === "/api/svg/make-lines").length;
const before = count();
// The same number, or another setting saying nothing moved, asks nothing new.
noteCoilOrJoinChanged({ settled: true });
await tick();
assert.equal(count(), before);
assert.equal(file.linesFailed, "load");
answers["/api/svg/make-lines"] = LINES;
coil = 5;
noteCoilOrJoinChanged({ settled: true });
await tick();
assert.equal(count(), before + 1);
assert.equal(file.svg, CONVERTED);
assert.equal(file.linesFailed, false);
"""
    )


def test_waiting_for_a_coil_follows_the_pass_through_undo_and_never_makes_lines_of_its_own() -> (
    None
):
    _run_section(
        """
answers["/api/svg/examine"] = CONVERT;
coil = 0;
const file = pass("cat.svg", "<svg>filled</svg>");
addDrawings([file]);
await tick();
const same = pass("cat.svg", "<svg>filled</svg>");
setFiles([same]);
assert.equal(same.linesWantCoil, true);
// A rebuild that puts a number back makes nothing, and the row offers it instead.
coil = 5;
const back = pass("cat.svg", "<svg>filled</svg>");
setFiles([back]);
assert.equal(back.linesWantCoil, undefined);
await tick();
assert.equal(asked.filter((c) => c.path === "/api/svg/make-lines").length, 0);
assert.deepEqual(linesRowActions(back).map((b) => b.textContent), ["Make lines again"]);
"""
    )


def test_plain_lines_added_with_the_coil_box_empty_stay_the_identical_string() -> None:
    _run_section(
        """
answers["/api/svg/examine"] = LEAVE;
coil = 0;
const plain = '<svg xmlns="x" viewBox="0 0 9 9">\\r\\n<path d="M0 0L9 9" stroke="#000"/></svg>';
const file = pass("plain.svg", plain);
addDrawings([file]);
await tick();
assert.equal(file.svg, plain);
assert.equal(asked[0].body.svg, plain);
assert.equal(asked.length, 1);
assert.equal(passHeldByLines(file), false);
assert.equal(layoutFiles()[0], file);
assert.equal(linesNoteContent(file), null);
coil = 5;
noteCoilOrJoinChanged({ settled: true });
await tick();
assert.equal(asked.length, 1);
assert.equal(file.svg, plain);
"""
    )


# --- saved lines changed in another app --------------------------------------------

# Inkscape 1.3.2 on a saved lines file, as it really wrote it: every mark kept, the
# root and the kept file's tag laid out its own way.
OUT_OF_INKSCAPE = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg
   width="110mm"
   height="60mm"
   viewBox="0 0 110 60"
   fill="none"
   stroke="#000"
   stroke-width="5"
   stroke-linecap="round"
   data-clayline-converted="1"
   data-clayline-target="100"
   data-clayline-coil="5"
   data-clayline-join="0.2"
   data-clayline-size-basis="typed"
   data-clayline-place="1 2 0.5 5 200 100"
   data-clayline-lines-hash="123:abc"
   version="1.1"
   id="svg1"
   xmlns="http://www.w3.org/2000/svg"
   xmlns:svg="http://www.w3.org/2000/svg">
  <defs
     id="defs1" />
  <metadata
     id="clayline-original">&lt;svg xmlns=&quot;http://www.w3.org/2000/svg&quot;&gt;&lt;/svg&gt;
</metadata>
  <path
     id="from-shape-0"
     d="M 5 5 L 105 55" />
</svg>
"""


def test_the_hash_covers_the_lines_and_the_page_and_leaves_other_files_alone() -> None:
    _with_lines(
        """
const stamped = Lines.withLinesHash(CONVERTED);
assert.notEqual(stamped, CONVERTED);
assert.equal(Lines.withLinesHash(stamped), stamped);
assert.equal(Lines.changedElsewhere(stamped), false);
// What the page reads off it, and the kept file, are as they were.
assert.deepEqual(Lines.marksOf(stamped), Lines.marksOf(CONVERTED));
assert.equal(Lines.originalOf(stamped), Lines.originalOf(CONVERTED));
// A line moved, or the page resized, with every mark left in place.
assert.equal(Lines.changedElsewhere(stamped.replace("M 5 5 L 105 55", "M 5 5 L 105 50")), true);
assert.equal(Lines.changedElsewhere(stamped.replace('width="110mm"', 'width="220mm"')), true);
// Saved by Clayline's last release there is no hash, and nothing to go on.
assert.equal(Lines.changedElsewhere(CONVERTED), false);
assert.equal(Lines.changedElsewhere(CONVERTED.replace("M 5 5", "M 6 6")), false);
// A file that isn't Clayline's lines is the identical string, and is never asked.
for (const plain of ["<svg>plain</svg>", '<svg xmlns="x">\\r\\n<path/></svg>', ""]) {
  assert.equal(Lines.withLinesHash(plain), plain);
  assert.equal(Lines.changedElsewhere(plain), false);
}
assert.equal(Lines.changedElsewhere('<svg data-clayline-lines-hash="1:a"><path/></svg>'), false);
"""
    )


def test_lines_changed_elsewhere_lose_the_kept_file_and_read_as_edited_by_hand() -> None:
    _with_lines(
        f"""
const stamped = Lines.withLinesHash(CONVERTED);
const changed = Lines.asHandEdited(stamped.replace("M 5 5", "M 6 6"));
assert.equal(Lines.hasOriginal(changed), false);
assert.ok(!changed.includes("<metadata"));
assert.ok(!changed.includes("lines-hash"));
assert.ok(changed.includes('d="M 6 6 L 105 55"'));
assert.equal(Lines.isConverted(changed), true);
assert.equal(Lines.originOf(changed), "edited");
// A drawing with an origin keeps it.
const drawn = '<svg data-clayline-converted="1" data-clayline-origin="drawn" data-clayline-lines-hash="1:a" xmlns="x"><path/></svg>';
assert.equal(Lines.originOf(Lines.asHandEdited(drawn)), "drawn");
// What Inkscape wrote is seen as changed, and its kept file goes too.
const inkscape = {json.dumps(OUT_OF_INKSCAPE)};
assert.equal(Lines.changedElsewhere(inkscape), true);
const owned = Lines.asHandEdited(inkscape);
assert.ok(!owned.includes("metadata"));
assert.ok(!owned.includes("lines-hash"));
assert.equal(Lines.originOf(owned), "edited");
assert.ok(owned.includes('d="M 5 5 L 105 55"'));
assert.ok(/^<\\?xml[^>]*>\\n<svg data-clayline-origin="edited"\\n   width="110mm"/.test(owned));
"""
    )


def test_lines_that_land_are_stamped_and_come_back_unchanged() -> None:
    _run_section(
        """
answers["/api/svg/examine"] = CONVERT;
answers["/api/svg/make-lines"] = { ...LINES, svg: LINES.svg.replace(/ data-clayline-lines-hash="[^"]*"/, "") };
const file = pass("cat.svg", "<svg>filled</svg>");
addDrawings([file]);
await tick();
assert.equal(file.svg, CONVERTED);
assert.equal(drawHistory.current().passes[0].svg, CONVERTED);
const back = pass("cat-lines.svg", file.svg);
addDrawings([back]);
await tick();
assert.equal(back.svg, CONVERTED);
assert.equal(Lines.hasOriginal(back.svg), true);
assert.deepEqual(linesRowActions(back).map((b) => b.textContent), ["Use original"]);
"""
    )


def test_a_saved_file_changed_elsewhere_keeps_the_change_through_size_and_coil() -> None:
    _run_section(
        f"""
answers["/api/svg/examine"] = CONVERT;
answers["/api/svg/make-lines"] = LINES;
const changed = CONVERTED.replace("M 5 5 L 105 55", "M 5 5 L 105 20").replace('data-clayline-size-basis="fit"', 'data-clayline-size-basis="typed"');
const file = pass("cat-lines.svg", changed);
const inkscaped = pass("ink.svg", {json.dumps(OUT_OF_INKSCAPE)});
addDrawings([file, inkscaped]);
await tick();
for (const each of [file, inkscaped]) {{
  assert.equal(Lines.hasOriginal(each.svg), false);
  assert.equal(Lines.isConverted(each.svg), true);
  assert.equal(Lines.originOf(each.svg), "edited");
  // A size typed for the old lines doesn't come back onto these.
  assert.equal(each.sizePinned, false);
  assert.deepEqual(linesRowActions(each), []);
  assert.equal(linesNoteContent(each), null);
}}
assert.ok(file.svg.includes("M 5 5 L 105 20"));
const kept = file.svg;
// The next size or coil change leaves them alone.
coil = 8;
noteCoilOrJoinChanged({{ settled: true }});
setLinesSize(file, 240);
await tick();
assert.equal(asked.length, 0);
assert.equal(file.svg, kept);
assert.equal(file.makingLines, undefined);
"""
    )


# --- words --------------------------------------------------------------------------


def test_an_empty_coil_box_is_never_sent_and_slice_says_what_it_wants() -> None:
    check = _block(APP, "async function runLayoutCheck", "function bedMapFrame")
    assert (
        'if (selectedBeadWidthMode() === "measured" && coilWidthIsSet()) '
        'body.bead_width = numberValue("#beadWidth");' in check
    )
    settled = _block(APP, "function updateDependencies", "const DRAW_SETTINGS_SCHEMA")
    assert "&& coilWidthIsSet()\n" in settled
    assert ": !coilWidthIsSet()\n          ? COIL_WANTED_FOOTNOTE" in settled
    assert "effectiveBeadWidth() > 0" not in settled
    # The box's own smallest, so what it holds is a width or it isn't.
    assert re.search(r'id="beadWidth"[^>]*\bmin="0\.1"', HTML)
    assert "const SMALLEST_COIL_MM = 0.1;" in APP
