# Changelog

What changed in each release of Clayline, newest first. Dates are release dates.

## 0.3.0 — 2026-09-18

### New
- **Space grabs a shape.** While dragging out a ring, box or polygon, hold
  Space and the shape moves with the pointer instead of growing; let go and it
  goes back to sizing from where you put it. Hold Space over a placed line or
  shape later and a frame with corner grips appears: drag inside to move it,
  drag a corner to resize it, Shift to keep the proportions. A ring stays a
  circle and a polygon stays regular. Without Space the bed is exactly as it
  was: drag a line to bend it, drag a point to move it, tap to add points.
- **Shapes remember what they are**, through saving as SVG and into a
  project file, until you bend or move one of their points.

### Changed
- Space plus drag over a line now moves the line. Panning stays on the empty
  bed, the middle button, and the trackpad.

## 0.2.2 — 2026-09-18

### Changed
- **The Export step is gone from both modes.** The print file is named after
  your design or your model, and the save panel lets you change it. The same
  job always writes the same file.
- **Restore pattern from G-code…** sits beside **Save pattern** and **Load
  pattern** in the Weave pattern section. It pulls only the pattern out of a
  print file Clayline saved: not the model, the size, the layers, or the range.
  A print file dropped on the Model box does the same.
- **The guide** no longer describes the Export step, and its Calibration page
  no longer calls the standard join depth and starting flow provisional.

## 0.2.1 — 2026-09-18

### Fixed
- **Z-blend no longer refuses a job over its own arithmetic.** On some forms
  one tiny step of the rim path came out a hair over the climb limit purely
  because of how the numbers were written into the print file, and the whole
  job was refused with a message nobody could act on. The path now stays inside
  the limit once written; if the final check still complains, Clayline eases the
  rim slightly and rebuilds; and if even that fails, the message says what to
  change and offers a button that does it.
- **A reopened Weave project keeps its last layer the way you set it.** A job
  saved with a last layer you typed came back as Clayline's own automatic stop,
  which changed what the rim did once Z-blend was on.
- **Two warnings about the rim now say what happened to the clay** instead of
  using internal names.

## 0.2.0 — 2026-09-17

### New
- **Projects.** Save a whole job as one project file and open it again exactly
  as you left it: every drawing or model, every setting, the wave you shaped, and
  the photo you traced over. It works the same way in Draw in Clay and in Weave,
  from the File menu, and by double-clicking a project file in Finder.
- **A gallery of 98 example drawings inside the app**, sorted into folders by
  tradition: Celtic, Japanese & Chinese, Moroccan, Arabic & Andalusian, Indian &
  Tibetan, Victorian & Gothic, Animals, and more. **Browse the gallery** in the
  Design step, or **File → Open from Gallery…**, opens it.
- **Adding a drawing starts somewhere useful.** Until you have opened a drawing
  from a folder of your own it starts in the gallery; after that it starts in
  your folder, and it no longer jumps to wherever you last saved a print file.
- **A user guide** at <https://peterkatz.github.io/clayline/>: installing, both
  modes, printing, calibration, troubleshooting, safety, and a glossary.

### Fixed
- The 0.1.0 download could unpack as a damaged app when the zip was opened by
  double-click. The release zip is now built without the hidden attribute
  entries that caused it, and every release is unpacked the way a person does
  it and checked before it is published.
- The window shows the name you saved your project under, and an undo that
  moves a model on the bed no longer leaves the project pointing at the old
  placement.

### For developers
- `examples/gallery-manifest.json` maps the flat example folders to the app's
  gallery folders; `tools/build_gallery.py` validates and builds them, the
  packager places them in `Contents/Resources/Gallery`, and
  `scripts/verify_macos_app.py` audits the result.
- `tools/notarize_app.sh` zips with `--norsrc --noextattr --noqtn --noacl`,
  refuses AppleDouble entries, and verifies the Archive Utility extraction.
- Version strings live in `pyproject.toml`, `src/clayline/__init__.py`,
  `uv.lock`, and `app/ClaylineMac/Info.plist`; bump all four together.

## 0.1.0 — 2026-09-16

First public release: Draw in Clay and Weave, the work-surface height setting,
the per-job start charge, and a signed, notarized download for Apple silicon
Macs.
