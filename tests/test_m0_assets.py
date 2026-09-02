from pathlib import Path
from xml.etree import ElementTree

import pytest

from scripts.validate_fixtures import REQUIRED_JOBS, REQUIRED_SVG, validate

ROOT = Path(__file__).resolve().parents[1]


def test_fixture_inventory_is_complete_and_parseable() -> None:
    assert not validate()
    assert len(REQUIRED_SVG) == 20
    assert len(REQUIRED_JOBS) == 3


@pytest.mark.skipif(
    not (ROOT / "docs" / "reference" / "IMG_3071.jpg").exists(),
    reason="maintainer-only fixture not in this checkout",
)
def test_reference_photos_are_committed() -> None:
    reference = ROOT / "docs" / "reference"
    for name in ("IMG_3071.jpg", "IMG_3073.jpg", "IMG_3074.jpg"):
        assert (reference / name).stat().st_size > 100_000


def test_tile_fixtures_are_exact_six_inch_photo_tracings() -> None:
    fixtures = ROOT / "tests" / "fixtures" / "svg"
    tracings = ROOT / "examples" / "gallery"

    for name in ("rings-grid.svg", "rosette.svg", "petal-flower.svg"):
        fixture = fixtures / name
        tracing = tracings / name

        assert fixture.read_bytes() == tracing.read_bytes()
        root = ElementTree.parse(fixture).getroot()
        assert root.attrib["width"] == "152.4mm"
        assert root.attrib["height"] == "152.4mm"
