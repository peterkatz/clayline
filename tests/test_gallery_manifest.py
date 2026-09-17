"""The gallery manifest and the builder that turns it into the app's example folders."""

from __future__ import annotations

import copy
import importlib.util
import json
import stat
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

from scripts.verify_macos_app import BANNED_PATH_PARTS

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "tools" / "build_gallery.py"
XATTR = Path("/usr/bin/xattr")


def _load_builder() -> ModuleType:
    # tools/ is a folder of standalone scripts, not a package, so load by path.
    spec = importlib.util.spec_from_file_location("clayline_build_gallery", BUILDER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


gallery = _load_builder()


def _drawing(path_data: str) -> bytes:
    return f'<svg xmlns="http://www.w3.org/2000/svg"><path d="{path_data}"/></svg>\n'.encode()


DRAWINGS = {
    "examples/first/knot.svg": _drawing("M0 0L9 9"),
    "examples/first/cross.svg": _drawing("M1 1L8 8"),
    "examples/second/owl.svg": _drawing("M2 2L7 7"),
    # The same file name as above, from another source folder, in another category.
    "examples/first/owl.svg": _drawing("M3 3L6 6"),
}
MANIFEST: dict[str, Any] = {
    "schema": "clayline.gallery.v1",
    "note": "a small stand-in for the real manifest",
    "sources": ["examples/first", "examples/second"],
    "categories": [
        {
            "folder": "Celtic",
            "files": [
                "examples/first/knot.svg",
                "examples/first/cross.svg",
                "examples/first/owl.svg",
            ],
        },
        {"folder": "Animals & Birds", "files": ["examples/second/owl.svg"]},
    ],
}


def _tree(tmp_path: Path) -> tuple[Path, dict[str, Any]]:
    root = tmp_path / "repo"
    for relative, payload in DRAWINGS.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)
    return root, copy.deepcopy(MANIFEST)


def _inventory(out: Path) -> dict[str, bytes]:
    return {
        path.relative_to(out).as_posix(): path.read_bytes()
        for path in out.rglob("*")
        if path.is_file()
    }


def test_the_real_manifest_is_valid_and_covers_every_example_drawing() -> None:
    manifest = gallery.load_manifest(gallery.DEFAULT_MANIFEST)

    assert gallery.validate(manifest, ROOT) == []

    on_disk = {
        path
        for source in manifest["sources"]
        for path in (ROOT / source).iterdir()
        if path.suffix == ".svg"
    }
    planned = gallery.planned_layout(manifest, ROOT)
    assert on_disk
    assert {source for _, source in planned} == on_disk
    assert len(planned) == len(on_disk)


def test_a_faithful_small_tree_is_valid(tmp_path: Path) -> None:
    root, manifest = _tree(tmp_path)

    assert gallery.validate(manifest, root) == []


def _wrong_schema(root: Path, manifest: dict[str, Any]) -> None:
    manifest["schema"] = "clayline.gallery.v2"


def _listed_file_is_missing(root: Path, manifest: dict[str, Any]) -> None:
    (root / "examples/first/knot.svg").unlink()


def _listed_file_is_not_a_drawing(root: Path, manifest: dict[str, Any]) -> None:
    (root / "examples/first/notes.txt").write_bytes(b"notes\n")
    manifest["categories"][0]["files"].append("examples/first/notes.txt")


def _listed_file_is_outside_the_sources(root: Path, manifest: dict[str, Any]) -> None:
    (root / "elsewhere").mkdir()
    (root / "elsewhere/stray.svg").write_bytes(b"<svg/>\n")
    manifest["categories"][0]["files"].append("elsewhere/stray.svg")


def _listed_file_climbs_out_of_the_repository(root: Path, manifest: dict[str, Any]) -> None:
    (root.parent / "stray.svg").write_bytes(b"<svg/>\n")
    manifest["categories"][0]["files"].append("examples/first/../../../stray.svg")


def _listed_file_is_a_link(root: Path, manifest: dict[str, Any]) -> None:
    (root.parent / "stray.svg").write_bytes(b"<svg/>\n")
    (root / "examples/first/link.svg").symlink_to(root.parent / "stray.svg")
    manifest["categories"][0]["files"].append("examples/first/link.svg")


def _drawing_on_disk_is_unlisted(root: Path, manifest: dict[str, Any]) -> None:
    (root / "examples/second/heron.svg").write_bytes(b"<svg/>\n")


def _drawing_is_listed_twice_in_one_folder(root: Path, manifest: dict[str, Any]) -> None:
    manifest["categories"][0]["files"].append("examples/first/knot.svg")


def _drawing_is_listed_in_two_folders(root: Path, manifest: dict[str, Any]) -> None:
    manifest["categories"][1]["files"].append("examples/first/knot.svg")


def _two_drawings_share_a_name_in_one_folder(root: Path, manifest: dict[str, Any]) -> None:
    manifest["categories"][0]["files"].remove("examples/first/owl.svg")
    manifest["categories"][1]["files"].append("examples/first/owl.svg")


def _two_categories_share_a_folder(root: Path, manifest: dict[str, Any]) -> None:
    manifest["categories"][1]["folder"] = "celtic"


def _source_folder_is_missing(root: Path, manifest: dict[str, Any]) -> None:
    manifest["sources"].append("examples/third")


def _renamed(folder: str) -> Callable[[Path, dict[str, Any]], None]:
    def doctor(root: Path, manifest: dict[str, Any]) -> None:
        manifest["categories"][1]["folder"] = folder

    return doctor


def _containing(text: bytes) -> Callable[[Path, dict[str, Any]], None]:
    def doctor(root: Path, manifest: dict[str, Any]) -> None:
        path = root / "examples/second/owl.svg"
        path.write_bytes(path.read_bytes().replace(b"<path", b"<!-- " + text + b" --><path"))

    return doctor


RULES = [
    (_wrong_schema, "'schema' must be 'clayline.gallery.v1'"),
    (_listed_file_is_missing, "examples/first/knot.svg: the file does not exist"),
    (_listed_file_is_not_a_drawing, "examples/first/notes.txt: must end in .svg"),
    (_listed_file_is_outside_the_sources, "elsewhere/stray.svg: is not under any of the 'sources'"),
    (_listed_file_climbs_out_of_the_repository, "must be a plain path inside the repository"),
    (_listed_file_is_a_link, "examples/first/link.svg: is a link"),
    (
        _drawing_on_disk_is_unlisted,
        "examples/second/heron.svg: is in a source folder but not listed",
    ),
    (_drawing_is_listed_twice_in_one_folder, "examples/first/knot.svg: listed 2 times"),
    (_drawing_is_listed_in_two_folders, "examples/first/knot.svg: listed 2 times"),
    (_two_drawings_share_a_name_in_one_folder, "share the name owl.svg"),
    (_two_categories_share_a_folder, "folder 'celtic': listed twice"),
    (_source_folder_is_missing, "source 'examples/third': the folder does not exist"),
    (_renamed(""), "empty folder name"),
    (_renamed("Birds/Owls"), "must not contain '/' or ':'"),
    (_renamed("Birds: Owls"), "must not contain '/' or ':'"),
    (_renamed(".Birds"), "must not start with '.' or a space"),
    (_renamed(" Birds"), "must not start with '.' or a space"),
    (_renamed("\tBirds"), "must not start with '.' or a space"),
    (_renamed("tests"), "reserved for development files"),
    (_renamed("Output"), "reserved for development files"),
    (_renamed("__PyCache__"), "reserved for development files"),
    (_containing(b"/Users/someone/Desktop/owl.ai"), "examples/second/owl.svg: contains '/Users/'"),
    (_containing(b"saved from Dropbox"), "examples/second/owl.svg: contains 'Dropbox'"),
    (_containing(b"drawn by potter@example.com"), "e-mail address (potter@example.com)"),
]


@pytest.mark.parametrize(
    ("doctor", "expected"),
    RULES,
    ids=[f"{index:02d}-{expected[:40]}" for index, (_, expected) in enumerate(RULES)],
)
def test_each_rule_rejects_a_doctored_tree(
    tmp_path: Path,
    doctor: Callable[[Path, dict[str, Any]], None],
    expected: str,
) -> None:
    root, manifest = _tree(tmp_path)
    doctor(root, manifest)

    problems = gallery.validate(manifest, root)

    assert any(expected in problem for problem in problems), problems
    assert all("\n" not in problem for problem in problems)
    with pytest.raises(gallery.GalleryError):
        gallery.build(manifest, root, tmp_path / "out")
    assert not (tmp_path / "out").exists()


def test_every_banned_bundle_name_is_refused_as_a_folder(tmp_path: Path) -> None:
    assert set(gallery.BANNED_FOLDER_NAMES) == set(BANNED_PATH_PARTS)

    for name in sorted(BANNED_PATH_PARTS):
        root, manifest = _tree(tmp_path / name.strip("._"))
        manifest["categories"][1]["folder"] = name.upper()
        problems = gallery.validate(manifest, root)
        assert any("reserved for development files" in problem for problem in problems), name


def test_build_reproduces_the_planned_layout_byte_for_byte(tmp_path: Path) -> None:
    root, manifest = _tree(tmp_path)
    out = tmp_path / "built" / "Gallery"

    assert gallery.build(manifest, root, out) == (2, 4)

    assert _inventory(out) == {
        "Celtic/knot.svg": DRAWINGS["examples/first/knot.svg"],
        "Celtic/cross.svg": DRAWINGS["examples/first/cross.svg"],
        "Celtic/owl.svg": DRAWINGS["examples/first/owl.svg"],
        "Animals & Birds/owl.svg": DRAWINGS["examples/second/owl.svg"],
    }
    assert sorted(path.name for path in out.iterdir()) == ["Animals & Birds", "Celtic"]
    planned = gallery.planned_layout(manifest, root)
    assert [destination.as_posix() for destination, _ in planned] == [
        "Animals & Birds/owl.svg",
        "Celtic/cross.svg",
        "Celtic/knot.svg",
        "Celtic/owl.svg",
    ]
    shuffled = copy.deepcopy(manifest)
    shuffled["categories"].reverse()
    shuffled["categories"][1]["files"].reverse()
    assert gallery.planned_layout(shuffled, root) == planned


def test_build_sets_plain_modes_whatever_the_sources_carry(tmp_path: Path) -> None:
    root, manifest = _tree(tmp_path)
    (root / "examples/first/knot.svg").chmod(0o600)
    (root / "examples/first/cross.svg").chmod(0o777)
    out = tmp_path / "Gallery"

    gallery.build(manifest, root, out)

    folders = [out, *(path for path in out.rglob("*") if path.is_dir())]
    files = [path for path in out.rglob("*") if path.is_file()]
    assert {stat.S_IMODE(path.stat().st_mode) for path in folders} == {0o755}
    assert {stat.S_IMODE(path.stat().st_mode) for path in files} == {0o644}


@pytest.mark.skipif(not XATTR.is_file(), reason="needs the macOS xattr tool")
def test_build_does_not_carry_extended_attributes_across(tmp_path: Path) -> None:
    root, manifest = _tree(tmp_path)
    source = root / "examples/first/knot.svg"
    marked = subprocess.run(
        [str(XATTR), "-w", "com.clayline.test-marker", "kept at home", str(source)],
        capture_output=True,
        check=False,
    )
    if marked.returncode != 0:
        pytest.skip("this volume does not take extended attributes")
    out = tmp_path / "Gallery"

    gallery.build(manifest, root, out)

    def names(path: Path) -> str:
        return subprocess.run(
            [str(XATTR), str(path)], capture_output=True, text=True, check=True
        ).stdout

    assert "com.clayline.test-marker" in names(source)
    assert "com.clayline.test-marker" not in names(out / "Celtic" / "knot.svg")


def test_build_refuses_an_output_folder_that_holds_anything(tmp_path: Path) -> None:
    root, manifest = _tree(tmp_path)
    out = tmp_path / "Gallery"
    out.mkdir()
    (out / "keep.txt").write_bytes(b"mine\n")

    with pytest.raises(gallery.GalleryError) as refused:
        gallery.build(manifest, root, out)

    assert "is not empty" in refused.value.problems[0]
    assert _inventory(out) == {"keep.txt": b"mine\n"}
    assert [path.name for path in out.iterdir()] == ["keep.txt"]

    not_a_folder = tmp_path / "Gallery.txt"
    not_a_folder.write_bytes(b"mine\n")
    with pytest.raises(gallery.GalleryError):
        gallery.build(manifest, root, not_a_folder)
    assert not_a_folder.read_bytes() == b"mine\n"


def test_build_accepts_an_existing_empty_output_folder(tmp_path: Path) -> None:
    root, manifest = _tree(tmp_path)
    out = tmp_path / "Gallery"
    out.mkdir()

    assert gallery.build(manifest, root, out) == (2, 4)
    assert len(_inventory(out)) == 4


def test_the_real_gallery_builds_exactly_as_planned(tmp_path: Path) -> None:
    manifest = gallery.load_manifest(gallery.DEFAULT_MANIFEST)
    out = tmp_path / "Gallery"

    folders, files = gallery.build(manifest, ROOT, out)

    planned = gallery.planned_layout(manifest, ROOT)
    assert folders == len(manifest["categories"])
    assert files == len(planned)
    assert _inventory(out) == {
        destination.as_posix(): source.read_bytes() for destination, source in planned
    }
    assert {path.name for path in out.iterdir()} == {
        category["folder"] for category in manifest["categories"]
    }


def test_the_command_line_reports_one_problem_per_line(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root, manifest = _tree(tmp_path)
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    arguments = ["--manifest", str(manifest_path), "--root", str(root)]

    assert gallery.main(["--check", *arguments]) == 0
    assert "2 folders, 4 drawings" in capsys.readouterr().out

    assert gallery.main(["--out", str(tmp_path / "Gallery"), *arguments]) == 0
    assert "2 folders, 4 drawings" in capsys.readouterr().out
    assert len(_inventory(tmp_path / "Gallery")) == 4

    (root / "examples/second/heron.svg").write_bytes(b"<svg/>\n")
    (root / "examples/first/knot.svg").unlink()
    assert gallery.main(["--check", *arguments]) == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    lines = captured.err.splitlines()
    assert len(lines) == 2
    assert all(line.startswith("build_gallery.py: ") for line in lines)

    manifest_path.write_text("{not json", encoding="utf-8")
    assert gallery.main(["--check", *arguments]) == 1
    assert "is not valid JSON" in capsys.readouterr().err


def test_the_script_runs_on_its_own_against_the_real_manifest() -> None:
    result = subprocess.run(
        [sys.executable, str(BUILDER), "--check"],
        capture_output=True,
        text=True,
        check=False,
        cwd="/",
    )

    assert result.returncode == 0, result.stderr
    assert "Gallery manifest is valid" in result.stdout
