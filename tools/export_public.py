#!/usr/bin/env python3
"""Export a public snapshot of this repository into a separate git checkout.

The development repository holds the maintainer's own print jobs, reference
photos, Rhino/Grasshopper exports, verification bundles built from them, and
agent handoff notes. None of that belongs in the public repository, so the public
repository is a fresh history that receives filtered snapshots of the working
tree (tracked files plus untracked files that are not ignored).

Usage:
    python tools/export_public.py DEST [--commit "message"]

DEST is the public checkout. Everything in it except ``.git`` is replaced by the
filtered snapshot. Markdown links in README.md and examples/README.md that point
at files absent from the snapshot are reduced to their link text.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Whole directories that are never published.
EXCLUDED_PREFIXES = (
    "tests/fixtures/reference/",  # maintainer's Rhino/Grasshopper exports and G-code
    "artifacts/",  # outputs of the maintainer's own jobs
    ".claude/",  # local agent configuration with machine paths
    "docs/",  # handoffs, PRDs, verification bundles (re-included selectively below)
)

# Individual files under excluded prefixes that are still published.
INCLUDED_EXACT = {
    "docs/assets/clayline-demo.gif",
    "docs/index.html",  # GitHub Pages landing page (served from main:/docs)
    "docs/reference/potterbot-10xl-reference-header-footer.gcode",  # machine facts, not a job
    "docs/verification/M7/rings-grid-plan.png",
    "docs/verification/M7/rosette-plan.png",
    "docs/verification/M7/petal-flower-plan.png",
}

# Patterns excluded anywhere in the tree.
EXCLUDED_PATTERNS = (
    re.compile(r"^examples/[^/]+\.gcode$"),  # generated jobs
    re.compile(r"^examples/gallery/compare-.*\.jpg$"),  # contain reference photos
    re.compile(r"^scripts/extract_reference_texture\.py$"),  # bound to the private corpus
    re.compile(r"(^|/)\.DS_Store$"),
    re.compile(r"(^|/)__pycache__/"),
    re.compile(r"\.py[cod]$"),
)

STATUS_SENTENCE = re.compile(
    r"Status is based on committed evidence under `docs/verification/`, not feature\s+"
    r"names or screenshots alone\."
)
STATUS_REPLACEMENT = (
    "Status is based on committed evidence bundles under `docs/verification/` in the\n"
    "maintainer's development repository. They are not part of this public snapshot\n"
    "because they were built from the maintainer's own print jobs."
)

LINK = re.compile(r"(!?)\[([^\]]*)\]\(([^)\s]+)\)")


def published(path: str) -> bool:
    if path in INCLUDED_EXACT:
        return True
    if any(path.startswith(prefix) for prefix in EXCLUDED_PREFIXES):
        return False
    return not any(pattern.search(path) for pattern in EXCLUDED_PATTERNS)


def working_tree_files() -> list[str]:
    output = subprocess.run(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    ).stdout
    names = sorted({name for name in output.decode("utf-8").split("\0") if name})
    return [name for name in names if (ROOT / name).is_file()]


def rewrite_links(markdown_path: Path, dest: Path) -> int:
    text = markdown_path.read_text(encoding="utf-8")
    changed = 0

    def replace(match: re.Match[str]) -> str:
        nonlocal changed
        _bang, label, target = match.groups()
        if "://" in target or target.startswith("#"):
            return match.group(0)
        resolved = (markdown_path.parent / target.split("#")[0]).resolve()
        try:
            resolved.relative_to(dest.resolve())
        except ValueError:
            return match.group(0)
        if resolved.exists():
            return match.group(0)
        changed += 1
        return label

    text = LINK.sub(replace, text)
    if markdown_path.name == "README.md" and markdown_path.parent == dest:
        text, count = STATUS_SENTENCE.subn(STATUS_REPLACEMENT, text)
        changed += count
    markdown_path.write_text(text, encoding="utf-8")
    return changed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("dest", type=Path)
    parser.add_argument("--commit", metavar="MESSAGE", help="commit the snapshot in DEST")
    args = parser.parse_args()
    dest: Path = args.dest.resolve()
    if dest == ROOT or ROOT in dest.parents:
        print("DEST must be outside the development repository", file=sys.stderr)
        return 2
    dest.mkdir(parents=True, exist_ok=True)
    for child in dest.iterdir():
        if child.name == ".git":
            continue
        if child.is_dir() and not child.is_symlink():
            shutil.rmtree(child)
        else:
            child.unlink()

    files = working_tree_files()
    kept = [name for name in files if published(name)]
    for name in kept:
        target = dest / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / name, target)

    rewritten = 0
    for readme in (dest / "README.md", dest / "examples" / "README.md"):
        if readme.exists():
            rewritten += rewrite_links(readme, dest)

    print(f"exported {len(kept)} of {len(files)} working-tree files to {dest}")
    print(f"rewrote {rewritten} markdown links/sentences that pointed at unpublished files")
    if args.commit:
        subprocess.run(["git", "add", "-A"], cwd=dest, check=True)
        subprocess.run(["git", "commit", "-q", "-m", args.commit], cwd=dest, check=True)
        print("committed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
