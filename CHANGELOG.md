# Changelog

What changed in each release of Clayline, newest first. Dates are release dates.

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
