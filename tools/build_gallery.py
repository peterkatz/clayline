#!/usr/bin/env python3
"""Build the organized gallery of example drawings that ships inside the Mac app.

The example drawings stay flat in their source folders. ``examples/gallery-manifest.json``
says which category folder each one belongs to, and this tool turns that into
``<out>/<folder>/<file>.svg`` by plain byte-for-byte copy.

    python3 tools/build_gallery.py --check      validate the manifest only
    python3 tools/build_gallery.py --out DIR    validate, then build DIR

Standard library only, so a bare ``python3`` can run it.
"""

from __future__ import annotations

import argparse
import filecmp
import json
import os
import re
import shutil
import sys
import unicodedata
from pathlib import Path, PurePosixPath
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "examples" / "gallery-manifest.json"
SCHEMA = "clayline.gallery.v1"
FOLDER_MODE = 0o755
FILE_MODE = 0o644

# Duplicated from BANNED_PATH_PARTS in scripts/verify_macos_app.py: the app audit
# rejects any bundle path with one of these parts, so a category folder may not
# use one. tests/test_gallery_manifest.py checks that the two lists agree.
BANNED_FOLDER_NAMES = frozenset(
    {
        ".git",
        ".hypothesis",
        ".pytest_cache",
        ".ruff_cache",
        ".venv",
        "__pycache__",
        "output",
        "tests",
    }
)

# Text that must never ship inside an example drawing.
PRIVATE_MARKERS = (b"/Users/", b"Dropbox")
EMAIL_ADDRESS = re.compile(rb"[A-Za-z0-9][A-Za-z0-9._%+-]*@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+")


class GalleryError(Exception):
    """The manifest or the requested build is not acceptable."""

    def __init__(self, problems: list[str]) -> None:
        super().__init__("; ".join(problems))
        self.problems = list(problems)


def load_manifest(path: Path) -> dict[str, Any]:
    """Read the manifest file; raise GalleryError when it is not a JSON object."""

    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
    except OSError as exc:
        raise GalleryError([f"cannot read the manifest {path}: {exc}"]) from exc
    except ValueError as exc:
        raise GalleryError([f"the manifest {path} is not valid JSON: {exc}"]) from exc
    if not isinstance(payload, dict):
        raise GalleryError([f"the manifest {path} must be a JSON object"])
    return payload


def _name_key(name: str) -> str:
    """Two names with the same key are one name on a Mac disk."""

    return unicodedata.normalize("NFC", name).casefold()


def _relative_parts(text: str) -> tuple[str, ...] | None:
    """Parts of a plain repository-relative path, or None when it is anything else."""

    if not text or "\\" in text or "\x00" in text:
        return None
    path = PurePosixPath(text)
    if path.is_absolute() or str(path) != text:
        return None
    if any(part in {"", ".", ".."} for part in path.parts):
        return None
    return path.parts


def _folder_name_problems(folder: str) -> list[str]:
    label = f"folder {folder!r}"
    if not folder:
        return ["a category has an empty folder name"]
    problems = []
    if "/" in folder or ":" in folder:
        problems.append(f"{label}: the name must not contain '/' or ':'")
    if folder[0] == "." or folder[0].isspace():
        problems.append(f"{label}: the name must not start with '.' or a space")
    if folder[-1].isspace():
        problems.append(f"{label}: the name must not end with a space")
    if any(unicodedata.category(character) == "Cc" for character in folder):
        problems.append(f"{label}: the name must not contain control characters")
    if _name_key(folder) in {_name_key(name) for name in BANNED_FOLDER_NAMES}:
        problems.append(f"{label}: the name is reserved for development files and cannot ship")
    return problems


def _private_text_problems(listed: str, source: Path) -> list[str]:
    try:
        payload = source.read_bytes()
    except OSError as exc:
        return [f"{listed}: cannot be read: {exc}"]
    problems = [
        f"{listed}: contains {marker.decode()!r}, which must not ship"
        for marker in PRIVATE_MARKERS
        if marker in payload
    ]
    match = EMAIL_ADDRESS.search(payload)
    if match is not None:
        address = match.group().decode("ascii", "replace")
        problems.append(f"{listed}: contains an e-mail address ({address})")
    return problems


def _entries(manifest: dict[str, Any], problems: list[str]) -> list[tuple[str, str]]:
    """Every well-formed (folder, listed file) pair, noting malformed ones as problems."""

    categories = manifest.get("categories")
    if not isinstance(categories, list) or not categories:
        problems.append("'categories' must be a non-empty list")
        return []
    entries: list[tuple[str, str]] = []
    seen_folders: dict[str, str] = {}
    for index, category in enumerate(categories):
        if not isinstance(category, dict):
            problems.append(f"category #{index + 1} must be an object with 'folder' and 'files'")
            continue
        folder = category.get("folder")
        files = category.get("files")
        if not isinstance(folder, str):
            problems.append(f"category #{index + 1}: 'folder' must be a string")
            continue
        problems.extend(_folder_name_problems(folder))
        if _name_key(folder) in seen_folders:
            earlier = seen_folders[_name_key(folder)]
            problems.append(f"folder {folder!r}: listed twice (also as {earlier!r})")
        seen_folders.setdefault(_name_key(folder), folder)
        if not isinstance(files, list) or not files:
            problems.append(f"folder {folder!r}: 'files' must be a non-empty list")
            continue
        for listed in files:
            if isinstance(listed, str):
                entries.append((folder, listed))
            else:
                problems.append(f"folder {folder!r}: every file must be a string, got {listed!r}")
    return entries


def validate(manifest: dict[str, Any], root: Path) -> list[str]:
    """Return every problem with the manifest, one line each; empty means valid."""

    root = Path(root)
    problems: list[str] = []
    if manifest.get("schema") != SCHEMA:
        problems.append(f"'schema' must be {SCHEMA!r}, got {manifest.get('schema')!r}")

    sources: list[tuple[str, ...]] = []
    raw_sources = manifest.get("sources")
    if not isinstance(raw_sources, list) or not raw_sources:
        problems.append("'sources' must be a non-empty list of folders")
        raw_sources = []
    for source in raw_sources:
        parts = _relative_parts(source) if isinstance(source, str) else None
        if parts is None:
            problems.append(f"source {source!r}: must be a plain path inside the repository")
        elif not root.joinpath(*parts).is_dir():
            problems.append(f"source {source!r}: the folder does not exist")
        elif parts in sources:
            problems.append(f"source {source!r}: listed twice")
        else:
            sources.append(parts)

    listed_count: dict[str, int] = {}
    names_in_folder: dict[tuple[str, str], str] = {}
    for folder, listed in _entries(manifest, problems):
        listed_count[listed] = listed_count.get(listed, 0) + 1
        if listed_count[listed] > 1:
            continue
        parts = _relative_parts(listed)
        if parts is None:
            problems.append(f"{listed!r}: must be a plain path inside the repository")
            continue
        if not listed.endswith(".svg"):
            problems.append(f"{listed}: must end in .svg")
        if not any(
            len(parts) > len(source) and parts[: len(source)] == source for source in sources
        ):
            problems.append(f"{listed}: is not under any of the 'sources' folders")
        source_file = root.joinpath(*parts)
        if source_file.is_symlink():
            problems.append(f"{listed}: is a link, not a drawing file")
        elif not source_file.is_file():
            problems.append(f"{listed}: the file does not exist")
        elif parts[-1] not in os.listdir(source_file.parent):
            # A Mac disk ignores capitals; other checkouts of the repository do not.
            problems.append(f"{listed}: the file name on disk is capitalized differently")
        else:
            problems.extend(_private_text_problems(listed, source_file))
        earlier = names_in_folder.setdefault((_name_key(folder), _name_key(parts[-1])), listed)
        if earlier != listed:
            problems.append(f"folder {folder!r}: {listed} and {earlier} share the name {parts[-1]}")

    for listed, count in sorted(listed_count.items()):
        if count > 1:
            problems.append(f"{listed}: listed {count} times, must be listed exactly once")
    for source in sources:
        for path in sorted(root.joinpath(*source).iterdir()):
            relative = "/".join((*source, path.name))
            is_drawing = path.suffix.lower() == ".svg" and not path.is_dir()
            if is_drawing and relative not in listed_count:
                problems.append(f"{relative}: is in a source folder but not listed in the manifest")
    return problems


def planned_layout(manifest: dict[str, Any], root: Path) -> list[tuple[PurePosixPath, Path]]:
    """(<folder>/<file>.svg, source file) for every drawing, in a deterministic order."""

    root = Path(root)
    layout = []
    for category in manifest["categories"]:
        for listed in category["files"]:
            source = PurePosixPath(listed)
            layout.append(
                (PurePosixPath(category["folder"], source.name), root.joinpath(*source.parts))
            )
    return sorted(layout, key=lambda item: item[0].parts)


def build(manifest: dict[str, Any], root: Path, out: Path) -> tuple[int, int]:
    """Validate, then copy the gallery into ``out``; return (folders, files).

    ``out`` must not exist yet, or must be an empty folder. Nothing is ever deleted.
    """

    problems = validate(manifest, root)
    if problems:
        raise GalleryError(problems)
    out = Path(out)
    if out.is_symlink() or (out.exists() and not out.is_dir()):
        raise GalleryError([f"the output {out} exists and is not a folder; nothing was written"])
    if out.is_dir() and any(out.iterdir()):
        raise GalleryError([f"the output folder {out} is not empty; nothing was written"])

    layout = planned_layout(manifest, root)
    out.mkdir(parents=True, exist_ok=True)
    os.chmod(out, FOLDER_MODE)
    folders = sorted({destination.parts[0] for destination, _ in layout})
    for folder in folders:
        (out / folder).mkdir()
        os.chmod(out / folder, FOLDER_MODE)
    for destination, source in layout:
        target = out.joinpath(*destination.parts)
        # copyfile, not copy2: the bytes only, no extended attributes and no source mode.
        shutil.copyfile(source, target)
        os.chmod(target, FILE_MODE)
        if not filecmp.cmp(source, target, shallow=False):
            raise GalleryError([f"the copy of {source} into {target} does not match its source"])
    return len(folders), len(layout)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--check", action="store_true", help="validate the manifest and stop")
    action.add_argument("--out", type=Path, metavar="DIR", help="build the gallery into DIR")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST, help=argparse.SUPPRESS)
    parser.add_argument("--root", type=Path, default=ROOT, help=argparse.SUPPRESS)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        manifest = load_manifest(args.manifest)
        if args.out is not None:
            folders, files = build(manifest, args.root, args.out)
            print(f"Gallery built: {folders} folders, {files} drawings in {args.out}")
            return 0
        problems = validate(manifest, args.root)
        if problems:
            raise GalleryError(problems)
        layout = planned_layout(manifest, args.root)
        folders = len({destination.parts[0] for destination, _ in layout})
        print(f"Gallery manifest is valid: {folders} folders, {len(layout)} drawings")
        return 0
    except GalleryError as error:
        for problem in error.problems:
            print(f"build_gallery.py: {problem}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
