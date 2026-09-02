"""Render photo/fixture comparisons used by the M0 gate."""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps

ROOT = Path(__file__).resolve().parents[1]
INKSCAPE = Path("/Applications/Inkscape.app/Contents/MacOS/inkscape")
OUTPUT = ROOT / "docs" / "verification" / "M0" / "photo-fixture-comparison.png"
ROWS = (
    ("IMG_3074.jpg", "rings-grid.svg", "Rings grid topology"),
    ("IMG_3073.jpg", "rosette.svg", "Nested rosette topology"),
    ("IMG_3071.jpg", "petal-flower.svg", "Petal flower and deliberate hub crossing"),
)


def _fit(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    background = Image.new("RGB", size, "white")
    contained = ImageOps.contain(image.convert("RGB"), size, Image.Resampling.LANCZOS)
    offset = ((size[0] - contained.width) // 2, (size[1] - contained.height) // 2)
    background.paste(contained, offset)
    return background


def main() -> None:
    if not INKSCAPE.exists():
        raise SystemExit(f"Inkscape not found at {INKSCAPE}")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    width = 1800
    cell = (860, 500)
    row_height = 560
    canvas = Image.new("RGB", (width, 70 + len(ROWS) * row_height), "#ede9e1")
    draw = ImageDraw.Draw(canvas)
    draw.text((30, 20), "Clayline M0 — photo-derived fixture comparison", fill="#171717")
    with tempfile.TemporaryDirectory(prefix="clayline-m0-") as temporary:
        temp = Path(temporary)
        for index, (photo_name, svg_name, label) in enumerate(ROWS):
            rendered = temp / f"{Path(svg_name).stem}.png"
            subprocess.run(
                [
                    str(INKSCAPE),
                    str(ROOT / "tests" / "fixtures" / "svg" / svg_name),
                    "--export-background=white",
                    "--export-width=1000",
                    f"--export-filename={rendered}",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            photo = Image.open(ROOT / "docs" / "reference" / photo_name)
            fixture = Image.open(rendered)
            top = 70 + index * row_height
            canvas.paste(_fit(photo, cell), (30, top + 35))
            canvas.paste(_fit(fixture, cell), (910, top + 35))
            draw.text((30, top + 8), f"Reference: {photo_name}", fill="#171717")
            draw.text((910, top + 8), f"Fixture: {svg_name} — {label}", fill="#171717")
    canvas.save(OUTPUT, optimize=True)
    print(OUTPUT)


if __name__ == "__main__":
    main()
