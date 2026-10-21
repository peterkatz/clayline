"""Run the studio's Weave page under node, against the real studio server.

weave.js runs whole, as the page runs it, in a small stand-in for the browser
document built from index.html: every element with its attributes, range and
number boxes that hold values the way a browser does (a range snaps to its
step and stays inside its limits), radio groups, clicks and events that bubble.
Timers run on a clock the test moves. Every request the page makes goes to the
studio app in this process (the FastAPI test client), so a texture, a noise
wave or a boost comes from the engine exactly as it does in the app.

A test script is the body of an async function. It can use:

    page     the running weave.js internals: S, patternObject(),
             weaveSettingsSnapshot(), validWeaveSettings(), applyWeaveSettings(),
             settingsSnapshotFromRestore(), renderPatternVisuals(), renderWarnings()
    $(sel)   the stand-in document's querySelector
    click(sel), type(sel, value), toggle(sel)
    settle(ms)   let timers due within `ms` run and every request finish
    requests     every request the page sent, oldest first
    weaveMode    window.claylineWeaveMode
    codec        window.ClaylineProjectFile
    out          an object returned to the test as JSON

Nothing here is the app: it is only how the tests reach the page.
"""

from __future__ import annotations

import base64
import json
import os
import subprocess
import tempfile
import threading
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "src" / "clayline" / "webui" / "static"

_VOID = {
    "area",
    "base",
    "br",
    "col",
    "embed",
    "hr",
    "img",
    "input",
    "link",
    "meta",
    "source",
    "track",
    "wbr",
}


class _Tree(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.root: list[Any] = ["#document", {}, []]
        self.stack: list[list[Any]] = [self.root]

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        node = [tag, {name: ("" if value is None else value) for name, value in attrs}, []]
        self.stack[-1][2].append(node)
        if tag not in _VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        node = [tag, {name: ("" if value is None else value) for name, value in attrs}, []]
        self.stack[-1][2].append(node)

    def handle_endtag(self, tag: str) -> None:
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                return

    def handle_data(self, data: str) -> None:
        if self.stack[-1][0] in {"script", "style"}:
            return
        if data:
            self.stack[-1][2].append(data)


def html_tree(html: str | None = None) -> list[Any]:
    parser = _Tree()
    parser.feed(html if html is not None else (STATIC / "index.html").read_text(encoding="utf-8"))
    parser.close()
    return parser.root


HARNESS = Path(__file__).with_name("weave_page_rig.js")


def run_page(
    script: str,
    *,
    weave_source: str | None = None,
    html: str | None = None,
    timeout_s: float = 180.0,
) -> dict[str, Any]:
    """Run ``script`` against the Weave page and return its ``out`` object."""

    from fastapi.testclient import TestClient

    from clayline.webui.app import create_app

    with tempfile.TemporaryDirectory() as scratch:
        folder = Path(scratch)
        tree = folder / "tree.json"
        tree.write_text(json.dumps(html_tree(html)), encoding="utf-8")
        weave = folder / "weave.js"
        weave.write_text(
            weave_source
            if weave_source is not None
            else (STATIC / "weave.js").read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        steps = folder / "script.js"
        steps.write_text(script, encoding="utf-8")
        errors = folder / "stderr.txt"
        env = {
            **os.environ,
            "CLAYLINE_PAGE_TREE": str(tree),
            "CLAYLINE_PAGE_WEAVE": str(weave),
            "CLAYLINE_PAGE_STATIC": str(STATIC),
            "CLAYLINE_PAGE_SCRIPT": str(steps),
        }
        result: dict[str, Any] | None = None
        with errors.open("w", encoding="utf-8") as stderr, TestClient(create_app()) as client:
            process = subprocess.Popen(
                ["node", str(HARNESS)],
                cwd=ROOT,
                env=env,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=stderr,
                text=True,
                bufsize=1,
            )
            watchdog = threading.Timer(timeout_s, process.kill)
            watchdog.start()
            try:
                assert process.stdout is not None and process.stdin is not None
                for line in process.stdout:
                    if line.startswith("@@REQ "):
                        request = json.loads(line[len("@@REQ ") :])
                        body = request["body"]
                        if body is None:
                            content = None
                        elif request["binary"]:
                            content = base64.b64decode(body)
                        else:
                            content = body.encode("utf-8")
                        response = client.request(
                            request["method"],
                            request["url"],
                            content=content,
                            headers=request["headers"],
                        )
                        headers = response.headers.items()
                        answer = {
                            "id": request["id"],
                            "status": response.status_code,
                            "body": response.text,
                            "headers": {key.lower(): value for key, value in headers},
                        }
                        process.stdin.write(json.dumps(answer) + "\n")
                        process.stdin.flush()
                    elif line.startswith("@@OUT "):
                        result = json.loads(line[len("@@OUT ") :])
                process.wait()
            finally:
                watchdog.cancel()
                if process.poll() is None:
                    process.kill()
        if process.returncode != 0 or result is None:
            raise AssertionError(
                f"the page script failed ({process.returncode}):\n"
                + errors.read_text(encoding="utf-8")[-6000:]
            )
        return result


__all__ = ["HARNESS", "html_tree", "run_page"]
