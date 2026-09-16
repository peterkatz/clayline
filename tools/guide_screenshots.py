"""Capture the user-guide screenshots from a running Clayline studio.

Start the studio first (``make ui`` or the clayline-ui launch configuration on
port 8765), then run::

    python tools/guide_screenshots.py [http://localhost:8765]

Images land in guide/images/ and are referenced by the guide pages. Nothing
here touches the printer; it drives the studio the way a person would: load a
gallery design, slice it, look at both previews, then load the synthetic
tumbler in Weave mode and slice that.
"""

from __future__ import annotations

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "guide" / "images"
SVG = ROOT / "examples" / "gallery" / "celtic-shield-knot.svg"
OBJ = ROOT / "examples" / "weave" / "pete-job.obj"
BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8765"


def wait_text_gone(page, text: str, timeout: int = 120_000) -> None:
    page.wait_for_function(
        "t => !document.body.innerText.includes(t)", arg=text, timeout=timeout
    )


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        # bypass_csp: the studio forbids eval, which wait_for_function needs.
        context = browser.new_context(
            viewport={"width": 1440, "height": 900}, device_scale_factor=2, bypass_csp=True
        )
        page = context.new_page()
        page.goto(BASE)
        page.wait_for_selector("#fileInput", state="attached")
        page.wait_for_timeout(800)
        page.screenshot(path=OUT / "tiles-empty.png")

        page.set_input_files("#fileInput", str(SVG))
        page.wait_for_function("!document.getElementById('sliceButton').disabled", timeout=60_000)
        page.wait_for_timeout(800)
        page.screenshot(path=OUT / "tiles-loaded.png")

        page.click("#sliceButton")
        wait_text_gone(page, "Slice to see the numbers.")
        page.wait_for_timeout(1500)
        page.screenshot(path=OUT / "tiles-sliced.png")

        page.click("#toolpathTab")
        page.wait_for_timeout(2500)
        page.screenshot(path=OUT / "tiles-3d.png")

        page.click("#weaveModeButton")
        page.wait_for_timeout(800)
        page.screenshot(path=OUT / "weave-empty.png")
        page.set_input_files("#weaveFileInput", str(OBJ))
        page.wait_for_function("!document.getElementById('weaveSettleButton').disabled", timeout=60_000)
        page.wait_for_timeout(800)
        page.screenshot(path=OUT / "weave-loaded.png")

        page.click("#weaveSettleButton")
        wait_text_gone(page, "Slice the form to see the numbers.")
        page.wait_for_timeout(2500)
        page.click("#weaveFitButton")  # frame the form instead of the whole bed
        page.wait_for_timeout(1500)
        page.screenshot(path=OUT / "weave-sliced.png")
        browser.close()
    for name in sorted(OUT.glob("*.png")):
        print(f"{name.relative_to(ROOT)}  {name.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
