"""The project container: one file that carries a whole Draw or Weave job.

The codec lives in the page, so these tests drive it the way the studio does —
through node — and then open the same bytes with Python's zipfile to prove the
file is an ordinary archive both sides agree on.
"""

from __future__ import annotations

import base64
import hashlib
import json
import struct
import subprocess
import zipfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "src" / "clayline" / "webui" / "static"
MODULE = STATIC / "project-file.js"

# The only three sentences the reader may ever show a person.
DAMAGED = "That isn't a Clayline project file, or it's damaged."
NEWER = "This project was saved by a newer Clayline. Update Clayline to open it."
TOO_LARGE = "This project is too large to open here."

DRAW_SETTINGS: dict[str, Any] = {
    "schema": "clayline.draw-settings.v2",
    "passes": [{"name": "rim", "svg": "<svg><path d='M0 0 L10 10'/></svg>", "scale": 1.5}],
    "job": {"profile": "potterbot-xl", "nozzle_mm": 5.0},
}
WEAVE_SETTINGS: dict[str, Any] = {
    "schema": "clayline.weave-settings.v1",
    "placement": {"up_axis": "z", "scale": 1.0},
    "slice": {"profile": "potterbot-xl", "layer_height": 1.5},
}


def _run_node(script: str, *args: str) -> Any:
    completed = subprocess.run(
        ["node", "-e", script, str(MODULE), *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise AssertionError(f"node refused the script:\n{completed.stderr.strip()}")
    return json.loads(completed.stdout)


def _manifest(mode: str = "draw", **overrides: Any) -> dict[str, Any]:
    manifest: dict[str, Any] = {
        "schema": "clayline.project.v1",
        "mode": mode,
        "saved_at": "2026-09-16T18:04:00Z",
        "saved_with": "0.1.0",
        "state": {"sliced": True},
        "settings": json.loads(json.dumps(DRAW_SETTINGS if mode == "draw" else WEAVE_SETTINGS)),
        "sources": [],
        "references": [],
    }
    manifest.update(overrides)
    return manifest


def _write_archive(
    path: Path,
    manifest: dict[str, Any] | None,
    entries: tuple[tuple[str, bytes], ...] = (),
    compression: int = zipfile.ZIP_DEFLATED,
) -> Path:
    with zipfile.ZipFile(path, "w", compression) as archive:
        if manifest is not None:
            archive.writestr("project.json", json.dumps(manifest))
        for name, payload in entries:
            archive.writestr(name, payload)
    return path


def _write_long_entry_archive(
    path: Path,
    manifest: dict[str, Any] | None,
    name: str,
    payload_bytes: int,
    declared_size: int | None = None,
) -> Path:
    """An archive holding a long run of zeros under *name*.

    The run is written a megabyte at a time so the test never holds the whole
    thing, and zeros pack down to a few hundred kilobytes on disk.
    ``declared_size`` rewrites the size the archive's index reports for that
    entry — the shape of a file that claims to be small and is not.  It only
    means anything when the archive holds one entry.
    """
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        if manifest is not None:
            archive.writestr("project.json", json.dumps(manifest))
        with archive.open(name, "w") as handle:
            chunk = b"\0" * (1024 * 1024)
            for _ in range(payload_bytes // len(chunk)):
                handle.write(chunk)
    if declared_size is None:
        return path
    raw = bytearray(path.read_bytes())
    at = raw.rindex(b"PK\x01\x02")
    struct.pack_into("<I", raw, at + 24, declared_size)
    path.write_bytes(bytes(raw))
    return path


def test_write_and_read_round_trip_both_modes_in_the_page() -> None:
    result = _run_node(
        """
        const assert = require("node:assert/strict");
        const pf = require(process.argv[1]);
        const utf8 = new TextEncoder();
        const text = new TextDecoder();
        (async () => {
          const drawSettings = {
            schema: "clayline.draw-settings.v2",
            passes: [{ name: "rim \\u8336", svg: "<svg><path d='M0 0 L10 10'/></svg>" }],
            job: { profile: "potterbot-xl", nozzle_mm: 5 },
          };
          const photo = new Uint8Array([137, 80, 78, 71, 13, 10, 26, 10, 0, 255, 7]);
          const drawBlob = await pf.write({
            mode: "draw",
            settings: drawSettings,
            state: { sliced: true },
            references: [{ image_id: "8f3a1c", media_type: "image/png", bytes: photo }],
            savedWith: "0.1.0",
          });
          assert.equal(drawBlob.type, "application/vnd.clayline.project+zip");
          const draw = await pf.read(drawBlob);
          assert.equal(draw.mode, "draw");
          assert.deepEqual(draw.settings, drawSettings);
          assert.deepEqual(draw.state, { sliced: true });
          assert.equal(draw.saved_with, "0.1.0");
          assert.match(draw.saved_at, /^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}Z$/);
          assert.equal(draw.sources.length, 0);
          assert.equal(draw.references.length, 1);
          assert.equal(draw.references[0].path, "references/8f3a1c.png");
          assert.equal(draw.references[0].media_type, "image/png");
          assert.deepEqual([...draw.references[0].bytes], [...photo]);
          assert.equal(draw.references[0].blob.type, "image/png");

          const weaveSettings = {
            schema: "clayline.weave-settings.v1",
            placement: { up_axis: "z", scale: 1 },
            pattern_json: "{}",
          };
          const mesh = utf8.encode("v 0 0 0\\nv 1 0 0\\nv 0 1 0\\nf 1 2 3\\n");
          const weaveBlob = await pf.write({
            mode: "weave",
            settings: weaveSettings,
            state: { sliced: false },
            sources: [{ name: "tumbler.obj", bytes: mesh }],
          });
          const weave = await pf.read(weaveBlob);
          assert.equal(weave.mode, "weave");
          assert.deepEqual(weave.settings, weaveSettings);
          assert.deepEqual(weave.state, { sliced: false });
          assert.equal(weave.saved_with, null);
          assert.equal(weave.references.length, 0);
          assert.equal(weave.sources.length, 1);
          assert.equal(weave.sources[0].name, "tumbler.obj");
          assert.equal(weave.sources[0].path, "sources/tumbler.obj");
          assert.equal(text.decode(weave.sources[0].bytes), text.decode(mesh));
          assert.equal(weave.sources[0].sha256.length, 64);

          // A settings snapshot from the other mode is a programming mistake,
          // not something a person can cause, so it is a plain failure.
          await assert.rejects(
            () => pf.write({ mode: "draw", settings: weaveSettings }),
            (error) => !(error instanceof pf.ProjectFileError),
          );

          console.log(JSON.stringify({
            surface: Object.keys(pf).sort(),
            zip: Object.keys(pf.zip).sort(),
            messages: pf.MESSAGES,
            project_schema: pf.PROJECT_SCHEMA,
            settings_schema: pf.SETTINGS_SCHEMA,
            caps: [pf.MAX_ARCHIVE_BYTES, pf.MAX_MANIFEST_BYTES, pf.MAX_REFERENCE_BYTES],
            mesh_sha256: weave.sources[0].sha256,
          }));
        })().catch((error) => { console.error(error); process.exit(1); });
        """
    )
    assert result["surface"] == [
        "MAX_ARCHIVE_BYTES",
        "MAX_MANIFEST_BYTES",
        "MAX_REFERENCE_BYTES",
        "MESSAGES",
        "PROJECT_MEDIA_TYPE",
        "PROJECT_SCHEMA",
        "ProjectFileError",
        "SETTINGS_SCHEMA",
        "read",
        "write",
        "zip",
    ]
    assert result["zip"] == ["read", "write"]
    assert result["messages"] == {
        "not-a-project": DAMAGED,
        "newer-version": NEWER,
        "too-large": TOO_LARGE,
    }
    assert result["project_schema"] == "clayline.project.v1"
    assert result["settings_schema"] == {
        "draw": "clayline.draw-settings.v2",
        "weave": "clayline.weave-settings.v1",
    }
    assert result["caps"] == [1024 * 1024 * 1024, 32 * 1024 * 1024, 64 * 1024 * 1024]
    assert (
        result["mesh_sha256"] == hashlib.sha256(b"v 0 0 0\nv 1 0 0\nv 0 1 0\nf 1 2 3\n").hexdigest()
    )


def test_archive_written_by_the_page_opens_as_an_ordinary_zip(tmp_path: Path) -> None:
    target = tmp_path / "bowl.clayline"
    written = _run_node(
        """
        const fs = require("node:fs");
        const pf = require(process.argv[1]);
        (async () => {
          const mesh = new TextEncoder().encode("v 0 0 0\\n".repeat(500));
          const blob = await pf.write({
            mode: "weave",
            settings: { schema: "clayline.weave-settings.v1", placement: { scale: 2 } },
            state: { sliced: true },
            sources: [{ name: "tumbler.obj", bytes: mesh }],
            savedWith: "0.1.0",
          });
          const bytes = Buffer.from(await blob.arrayBuffer());
          fs.writeFileSync(process.argv[2], bytes);
          console.log(JSON.stringify({
            size: bytes.length,
            mesh: Buffer.from(mesh).toString("base64"),
          }));
        })().catch((error) => { console.error(error); process.exit(1); });
        """,
        str(target),
    )

    assert target.stat().st_size == written["size"]
    with zipfile.ZipFile(target) as archive:
        assert archive.testzip() is None
        assert archive.namelist() == ["project.json", "sources/tumbler.obj"]
        for info in archive.infolist():
            assert info.compress_type in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED)
            assert info.flag_bits & 0x800, "names must be marked UTF-8"
            assert info.create_system == 0
        manifest = json.loads(archive.read("project.json"))
        mesh = archive.read("sources/tumbler.obj")

    assert base64.b64encode(mesh).decode("ascii") == written["mesh"]
    assert manifest["schema"] == "clayline.project.v1"
    assert manifest["mode"] == "weave"
    assert manifest["state"] == {"sliced": True}
    assert manifest["saved_with"] == "0.1.0"
    assert manifest["settings"] == {
        "schema": "clayline.weave-settings.v1",
        "placement": {"scale": 2},
    }
    assert manifest["sources"] == [
        {
            "path": "sources/tumbler.obj",
            "name": "tumbler.obj",
            "size": len(mesh),
            "sha256": hashlib.sha256(mesh).hexdigest(),
        }
    ]
    assert manifest["references"] == []


def test_packed_and_stored_archives_written_by_python_open_in_the_page(tmp_path: Path) -> None:
    mesh = b"v 0 0 0\nv 1 0 0\nv 0 1 0\nf 1 2 3\n" * 40
    manifest = _manifest(
        "weave",
        sources=[
            {
                "path": "sources/tumbler.obj",
                "name": "tumbler.obj",
                "size": len(mesh),
                "sha256": hashlib.sha256(mesh).hexdigest(),
            }
        ],
    )
    packed = _write_archive(
        tmp_path / "packed.clayline",
        manifest,
        (("sources/tumbler.obj", mesh),),
        zipfile.ZIP_DEFLATED,
    )
    stored = _write_archive(
        tmp_path / "stored.clayline",
        manifest,
        (("sources/tumbler.obj", mesh),),
        zipfile.ZIP_STORED,
    )
    with zipfile.ZipFile(packed) as archive:
        assert archive.getinfo("sources/tumbler.obj").compress_type == zipfile.ZIP_DEFLATED
    with zipfile.ZipFile(stored) as archive:
        assert archive.getinfo("sources/tumbler.obj").compress_type == zipfile.ZIP_STORED

    result = _run_node(
        """
        const assert = require("node:assert/strict");
        const fs = require("node:fs");
        const pf = require(process.argv[1]);
        (async () => {
          const seen = {};
          for (const path of process.argv.slice(2)) {
            const project = await pf.read(new Uint8Array(fs.readFileSync(path)));
            assert.equal(project.mode, "weave");
            assert.deepEqual(project.state, { sliced: true });
            assert.equal(project.settings.schema, "clayline.weave-settings.v1");
            assert.equal(project.sources.length, 1);
            seen[path.split("/").pop()] = {
              mesh: Buffer.from(project.sources[0].bytes).toString("base64"),
              size: project.sources[0].size,
              sha256: project.sources[0].sha256,
              layer_height: project.settings.slice.layer_height,
            };
          }
          console.log(JSON.stringify(seen));
        })().catch((error) => { console.error(error); process.exit(1); });
        """,
        str(packed),
        str(stored),
    )

    expected = {
        "mesh": base64.b64encode(mesh).decode("ascii"),
        "size": len(mesh),
        "sha256": hashlib.sha256(mesh).hexdigest(),
        "layer_height": 1.5,
    }
    assert result == {"packed.clayline": expected, "stored.clayline": expected}


def test_utf8_names_survive_both_writers(tmp_path: Path) -> None:
    name = "tumbler 茶碗 über.obj"
    mesh = b"v 0 0 0\n"
    from_page = tmp_path / "from-page.clayline"
    _run_node(
        """
        const fs = require("node:fs");
        const pf = require(process.argv[1]);
        (async () => {
          const blob = await pf.write({
            mode: "weave",
            settings: { schema: "clayline.weave-settings.v1" },
            sources: [{ name: process.argv[3], bytes: new TextEncoder().encode("v 0 0 0\\n") }],
          });
          fs.writeFileSync(process.argv[2], Buffer.from(await blob.arrayBuffer()));
          console.log(JSON.stringify({ written: true }));
        })().catch((error) => { console.error(error); process.exit(1); });
        """,
        str(from_page),
        name,
    )

    with zipfile.ZipFile(from_page) as archive:
        assert archive.namelist() == ["project.json", f"sources/{name}"]
        assert json.loads(archive.read("project.json"))["sources"][0]["name"] == name

    from_python = _write_archive(
        tmp_path / "from-python.clayline",
        _manifest(
            "weave",
            sources=[
                {
                    "path": f"sources/{name}",
                    "name": name,
                    "size": len(mesh),
                    "sha256": hashlib.sha256(mesh).hexdigest(),
                }
            ],
        ),
        ((f"sources/{name}", mesh),),
    )
    result = _run_node(
        """
        const fs = require("node:fs");
        const pf = require(process.argv[1]);
        (async () => {
          const names = [];
          for (const path of process.argv.slice(2)) {
            const project = await pf.read(new Uint8Array(fs.readFileSync(path)));
            names.push(project.sources[0].name, project.sources[0].path);
          }
          console.log(JSON.stringify(names));
        })().catch((error) => { console.error(error); process.exit(1); });
        """,
        str(from_page),
        str(from_python),
    )
    assert result == [name, f"sources/{name}", name, f"sources/{name}"]


def test_damaged_and_foreign_files_refuse_with_exactly_three_messages(tmp_path: Path) -> None:
    mesh = b"v 0 0 0\n" * 20
    good_manifest = _manifest(
        "weave",
        sources=[
            {
                "path": "sources/tumbler.obj",
                "name": "tumbler.obj",
                "size": len(mesh),
                "sha256": hashlib.sha256(mesh).hexdigest(),
            }
        ],
    )
    good = _write_archive(
        tmp_path / "good.clayline", good_manifest, (("sources/tumbler.obj", mesh),)
    )
    good_bytes = good.read_bytes()

    stored = _write_archive(
        tmp_path / "stored.clayline",
        good_manifest,
        (("sources/tumbler.obj", mesh),),
        zipfile.ZIP_STORED,
    )
    flipped_bytes = bytearray(stored.read_bytes())
    at = flipped_bytes.index(b"v 0 0 0")
    flipped_bytes[at] = ord("V")
    flipped = tmp_path / "flipped.clayline"
    flipped.write_bytes(bytes(flipped_bytes))

    truncated = tmp_path / "truncated.clayline"
    truncated.write_bytes(good_bytes[: len(good_bytes) - 30])

    not_a_zip = tmp_path / "holiday.clayline"
    not_a_zip.write_bytes(b"a photo of a bowl, not a project file\n" * 8)

    foreign = _write_archive(
        tmp_path / "foreign.clayline",
        None,
        (("holiday/beach.jpg", b"\xff\xd8\xff\xe0jpeg"), ("holiday/notes.txt", b"sunny")),
    )
    no_manifest = _write_archive(
        tmp_path / "no-manifest.clayline", None, (("sources/tumbler.obj", mesh),)
    )

    def draw_with(settings_schema: str) -> dict[str, Any]:
        manifest = _manifest("draw")
        manifest["settings"]["schema"] = settings_schema
        return manifest

    def weave_with_source_path(path: str) -> dict[str, Any]:
        return _manifest(
            "weave",
            sources=[
                {
                    "path": path,
                    "name": "tumbler.obj",
                    "size": len(mesh),
                    "sha256": hashlib.sha256(mesh).hexdigest(),
                }
            ],
        )

    over_the_manifest_cap = _manifest("weave")
    # 33 MiB of padding: past the cap project.json is held to, and a few tens
    # of kilobytes on disk once it is packed.
    over_the_manifest_cap["padding"] = "a" * (33 * 1024 * 1024)
    big_manifest = _write_archive(tmp_path / "big-manifest.clayline", over_the_manifest_cap)

    big_photos = _write_long_entry_archive(
        tmp_path / "big-photos.clayline",
        _manifest(
            "draw",
            references=[
                {
                    "path": "references/one.png",
                    "image_id": "one",
                    "media_type": "image/png",
                    "size": 65 * 1024 * 1024,
                }
            ],
        ),
        "references/one.png",
        65 * 1024 * 1024,
    )

    borrowed_photo_kind = _write_archive(
        tmp_path / "borrowed-kind.clayline",
        _manifest(
            "draw",
            references=[
                {
                    "path": "references/one.png",
                    "image_id": "one",
                    "media_type": "constructor",
                    "size": 3,
                }
            ],
        ),
        (("references/one.png", b"\x89PN"),),
    )

    cases: list[dict[str, Any]] = [
        {"name": "good", "path": str(good), "expect": "opened"},
        {"name": "not-a-zip", "path": str(not_a_zip), "expect": DAMAGED},
        {"name": "truncated", "path": str(truncated), "expect": DAMAGED},
        {"name": "foreign-zip", "path": str(foreign), "expect": DAMAGED},
        {"name": "no-project-json", "path": str(no_manifest), "expect": DAMAGED},
        {"name": "crc-flipped", "path": str(flipped), "expect": DAMAGED},
        {
            "name": "bad-outer-schema",
            "path": str(
                _write_archive(tmp_path / "bad-outer.clayline", _manifest(schema="party.mix.v1"))
            ),
            "expect": DAMAGED,
        },
        {
            "name": "unknown-mode",
            "path": str(_write_archive(tmp_path / "bad-mode.clayline", _manifest(mode="knitting"))),
            "expect": DAMAGED,
        },
        {
            "name": "newer-outer-schema",
            "path": str(
                _write_archive(
                    tmp_path / "newer-outer.clayline", _manifest(schema="clayline.project.v9")
                )
            ),
            "expect": NEWER,
        },
        {
            "name": "newer-settings-schema",
            "path": str(
                _write_archive(
                    tmp_path / "newer-inner.clayline", draw_with("clayline.draw-settings.v9")
                )
            ),
            "expect": NEWER,
        },
        {
            "name": "older-settings-schema",
            "path": str(
                _write_archive(
                    tmp_path / "older-inner.clayline", draw_with("clayline.draw-settings.v1")
                )
            ),
            "expect": DAMAGED,
        },
        {
            "name": "escaping-path",
            "path": str(
                _write_archive(
                    tmp_path / "escaping.clayline",
                    weave_with_source_path("sources/../../evil.obj"),
                    (("sources/tumbler.obj", mesh),),
                )
            ),
            "expect": DAMAGED,
        },
        {
            "name": "absolute-path",
            "path": str(
                _write_archive(
                    tmp_path / "absolute.clayline",
                    weave_with_source_path("/etc/hosts"),
                    (("sources/tumbler.obj", mesh),),
                )
            ),
            "expect": DAMAGED,
        },
        {
            "name": "nested-path",
            "path": str(
                _write_archive(
                    tmp_path / "nested.clayline",
                    weave_with_source_path("sources/scans/tumbler.obj"),
                    (("sources/scans/tumbler.obj", mesh),),
                )
            ),
            "expect": DAMAGED,
        },
        {
            "name": "missing-source",
            "path": str(
                _write_archive(
                    tmp_path / "missing.clayline", weave_with_source_path("sources/gone.obj")
                )
            ),
            "expect": DAMAGED,
        },
        {"name": "over-the-size-cap", "path": str(good), "max_bytes": 64, "expect": TOO_LARGE},
        # The two caps the file itself can break, with no caller override in
        # sight: the shipped bounds on project.json and on the photos.
        {"name": "over-the-project-cap", "path": str(big_manifest), "expect": TOO_LARGE},
        {"name": "over-the-photo-cap", "path": str(big_photos), "expect": TOO_LARGE},
        # A name every object carries is not a kind of photo Clayline opens.
        {"name": "borrowed-photo-kind", "path": str(borrowed_photo_kind), "expect": DAMAGED},
    ]
    plan = tmp_path / "cases.json"
    plan.write_text(json.dumps(cases), encoding="utf-8")

    result = _run_node(
        """
        const assert = require("node:assert/strict");
        const fs = require("node:fs");
        const pf = require(process.argv[1]);
        (async () => {
          const cases = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
          const seen = {};
          for (const item of cases) {
            const bytes = new Uint8Array(fs.readFileSync(item.path));
            const options = item.max_bytes ? { maxBytes: item.max_bytes } : {};
            try {
              const project = await pf.read(bytes, options);
              seen[item.name] = { outcome: "opened", mode: project.mode };
            } catch (error) {
              assert.ok(
                error instanceof pf.ProjectFileError,
                `${item.name} refused with ${error}`,
              );
              seen[item.name] = { outcome: error.message, code: error.code, detail: error.detail };
            }
          }
          console.log(JSON.stringify(seen));
        })().catch((error) => { console.error(error); process.exit(1); });
        """,
        str(plan),
    )

    assert result["good"] == {"outcome": "opened", "mode": "weave"}
    codes = {DAMAGED: "not-a-project", NEWER: "newer-version", TOO_LARGE: "too-large"}
    for case in cases:
        if case["name"] == "good":
            continue
        seen = result[case["name"]]
        assert seen["outcome"] == case["expect"], case["name"]
        assert seen["code"] == codes[case["expect"]], case["name"]
        # The detail is for the log, never for a person reading the studio.
        assert seen["detail"], case["name"]
    assert {row["outcome"] for row in result.values()} == {"opened", DAMAGED, NEWER, TOO_LARGE}


def test_a_packed_entry_cannot_expand_past_the_size_it_claims(tmp_path: Path) -> None:
    """The caps bound what a file can make the studio hold, not what it says.

    A quarter of a gigabyte of zeros packs down to a few hundred kilobytes; if
    the index is then told the entry is twelve bytes long, every cap that
    reads the index waves it through.  The refusal has to come out of the
    expansion itself, while it runs, or an ordinary-looking file takes the
    studio — and whatever is unsaved on the bed — down with it.
    """
    bomb = _write_long_entry_archive(
        tmp_path / "small-claim.clayline", None, "project.json", 256 * 1024 * 1024, declared_size=12
    )
    assert bomb.stat().st_size < 2 * 1024 * 1024

    result = _run_node(
        """
        const fs = require("node:fs");
        const pf = require(process.argv[1]);
        (async () => {
          let outcome = "opened";
          try {
            await pf.read(new Uint8Array(fs.readFileSync(process.argv[2])));
          } catch (error) {
            outcome = { message: error.message, code: error.code, detail: error.detail };
          }
          console.log(JSON.stringify({
            outcome,
            held_mib: Math.round(process.memoryUsage.rss() / (1024 * 1024)),
          }));
        })().catch((error) => { console.error(error); process.exit(1); });
        """,
        str(bomb),
    )
    assert result["outcome"]["message"] == DAMAGED
    assert result["outcome"]["code"] == "not-a-project"
    assert result["held_mib"] < 192


def test_the_meshes_are_counted_before_one_of_them_is_unpacked(tmp_path: Path) -> None:
    """Photos were counted against a bound and meshes were not.

    A mesh packs down the way anything else does, so a project file of a few
    kilobytes could name a mesh of hundreds of megabytes and the studio would
    hold every one of them.  The meshes are added up out of the index first,
    against the same bound the whole file has, and the refusal comes before
    the first byte is unpacked.
    """
    manifest = _manifest("weave", sources=[{"path": "sources/big.obj", "name": "big.obj"}])
    packed = _write_long_entry_archive(
        tmp_path / "small-file-big-mesh.clayline", manifest, "sources/big.obj", 8 * 1024 * 1024
    )
    assert packed.stat().st_size < 64 * 1024

    result = _run_node(
        """
        const fs = require("node:fs");
        const pf = require(process.argv[1]);
        (async () => {
          const bytes = new Uint8Array(fs.readFileSync(process.argv[2]));
          const seen = {};
          for (const maxBytes of [4 * 1024 * 1024, 16 * 1024 * 1024]) {
            try {
              const project = await pf.read(bytes, { maxBytes });
              seen[maxBytes] = { outcome: "opened", size: project.sources[0].size };
            } catch (error) {
              seen[maxBytes] = { outcome: error.message, code: error.code, detail: error.detail };
            }
          }
          console.log(JSON.stringify({
            seen,
            held_mib: Math.round(process.memoryUsage.rss() / (1024 * 1024)),
          }));
        })().catch((error) => { console.error(error); process.exit(1); });
        """,
        str(packed),
    )
    refused = result["seen"][str(4 * 1024 * 1024)]
    assert refused["outcome"] == TOO_LARGE
    assert refused["code"] == "too-large"
    assert refused["detail"]
    # The same file under a bound it fits inside still opens, whole.
    assert result["seen"][str(16 * 1024 * 1024)] == {
        "outcome": "opened",
        "size": 8 * 1024 * 1024,
    }


def test_a_twenty_megabyte_mesh_round_trips_byte_exact(tmp_path: Path) -> None:
    target = tmp_path / "scan.clayline"
    result = _run_node(
        """
        const assert = require("node:assert/strict");
        const crypto = require("node:crypto");
        const fs = require("node:fs");
        const pf = require(process.argv[1]);
        (async () => {
          // A scan-sized mesh that does not compress away, built without
          // holding a second copy of the file in the test itself.
          const size = 20 * 1024 * 1024;
          const mesh = new Uint8Array(size);
          let seed = 12345;
          for (let at = 0; at < size; at += 1) {
            seed = (seed * 1103515245 + 12345) & 0x7fffffff;
            mesh[at] = (seed >>> 16) & 0xff;
          }
          const before = crypto.createHash("sha256").update(mesh).digest("hex");
          const blob = await pf.write({
            mode: "weave",
            settings: { schema: "clayline.weave-settings.v1" },
            state: { sliced: true },
            sources: [{ name: "scan.obj", bytes: mesh }],
          });
          fs.writeFileSync(process.argv[2], Buffer.from(await blob.arrayBuffer()));

          const project = await pf.read(new Uint8Array(fs.readFileSync(process.argv[2])));
          const after = crypto.createHash("sha256").update(project.sources[0].bytes).digest("hex");
          assert.equal(project.sources[0].size, size);
          assert.equal(after, before);
          assert.equal(project.sources[0].sha256, before);
          assert.equal(Buffer.compare(Buffer.from(project.sources[0].bytes), mesh), 0);
          console.log(JSON.stringify({ size, sha256: before }));
        })().catch((error) => { console.error(error); process.exit(1); });
        """,
        str(target),
    )

    assert result["size"] == 20 * 1024 * 1024
    with zipfile.ZipFile(target) as archive:
        assert archive.testzip() is None
        mesh = archive.read("sources/scan.obj")
    assert len(mesh) == result["size"]
    assert hashlib.sha256(mesh).hexdigest() == result["sha256"]
