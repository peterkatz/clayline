# Changelog

What changed in each release of Clayline, newest first. Dates are release dates.

## 0.8.1 — 2026-10-06

### New
- **Stack pieces ★ Experimental.** A new switch in Weave's Slice section,
  right under Nozzle opening, off by default. Where a form stands in separate
  pieces, the nozzle prints a few layers of one piece before it crosses to the
  next, so it crosses less often. It only goes ahead as far as no part of the
  nozzle can reach the taller piece: measure how far your nozzle sticks out
  below the adapter and type it in **Nozzle sticks out** (10 mm until you do).
  A piece's next layer never starts within 5 seconds of the one below it, and
  pieces that join higher up both reach the joining layer first. Not checked:
  how fast your clay firms up, or how well a layer sticks after waiting, so
  watch the first print closely.

## 0.8.0 — 2026-10-06

### New
- **Undo that works.** Command-Z, the Undo button and Edit › Undo take back
  exactly your last change, every time: moving, turning or sizing the model on
  the bed, a number you typed, a choice from a list, loading another model,
  Reset, and bringing back settings from a print file. Undo back to a form you
  had already sliced and its slice comes straight back, without slicing again.
- **Keep clay flowing on crossings.** A new switch in Weave's Printer section,
  on by default. The printer keeps pushing clay at the print rate while the
  nozzle lifts, crosses and comes back down, so the next line starts at full
  pressure instead of thin, and lines start and end at full flow. It uses more
  clay where the nozzle crosses. Switch it off to stop the push on every
  crossing as before. Print files saved before this release still print
  exactly as they were saved.

### Fixed
- **Far fewer crossings on a form that splits for a few layers.** A filled
  form that stands in two pieces somewhere now prints every stretch where it is
  one piece as one unbroken line. Before, a split anywhere made the nozzle lift
  and cross the piece on every layer of the whole form. Where the line can't
  reach the next part of the fill along the clay, the nozzle crosses, and a
  warning says how often.
- **A click on the model no longer nudges it.** The model only moves once you
  drag it a few pixels.
- **iPhone photos** still open as reference photos; the app reads them with a
  smaller built-in reader.

## 0.7.2 — 2026-10-03

### Fixed
- **The layers above the layer slider are lighter still,** so the inside of a
  form shows through them more clearly while you scrub.

## 0.7.1 — 2026-10-03

### Fixed
- **Ignore hollows is where you'd look for it.** It now sits in the Interior
  section, right under Hollow, Solid and Infill, and changing it slices the
  form again by itself. When a model is hollow inside and the fill would stay
  in its wall, the section says so beside the switch.
- **The Interior section is easier to read.** Each choice is described in one
  short line, with the longer explanation in the tooltip, and nothing is said
  twice.
- **You can see inside while you scrub.** The layers above the layer slider
  are a little more see-through, so the inside of a form shows through them.

## 0.7.0 — 2026-10-03

### New
- **Ignore hollows.** A new switch in the Slice section. Switched on, each
  layer gets a wall around its outside only: a hollow inside the model, and
  places where its surface passes through itself, get no walls of their own,
  and a Solid or Infill interior runs straight across them. Use it for a model
  that was hollowed out, or whose surface crosses itself, when you want it
  printed as one piece of clay. Leave it off for cups, vases and anything meant
  to be open inside.

### Fixed
- **A small piece standing apart no longer cuts off the top of the form.** The
  print only stops before a split when the separate pieces carry on all the way
  to the top, like prongs or a crown of leaves. A piece that ends below the top
  prints with the rest, and a warning names the layers where the nozzle lifts
  and moves between the pieces. Vase mode still stops before any split.
- **A hollow inside the model is no longer mistaken for clay** where the
  model's outside surface crosses itself.

## 0.6.0 — 2026-10-03

### New
- **Pieces with tops.** Cap layers now lays a dense roof wherever the form
  has open air above it: the very top, a floor partway up (like the bottom of
  a bowl's hollow), or the layers of a dome as it closes in. Base layers does
  the same for floors. A wall that steps inward by more than half a coil gets
  dense fill under it too, so it lands on clay. The whole layer goes dense
  where part of it needs a roof. Ramp layers now tighten the ribs under every
  roof, not only the top one. Cap layers still starts at 0.
- **A warning when a wall lands over the gaps between ribs.** If a wall steps
  in past the wall below and has too little clay under it, Clayline names the
  layers and how far off it lands.

### Fixed
- **A short split no longer stops the print.** A form that splits into
  separate pieces for 3 layers or fewer, then joins again (a thin skirt beside
  a dish, for example), now prints whole. The message names the split's real
  layers. Vase mode still stops before any split.
- **Turning "Print selected layers" off now stays off** when you slice again.
- **A flat top prints to its full height.** A 30 mm form at 1.5 mm layers used
  to stop at 28.5 mm. Print files saved by earlier versions still open exactly
  as they were.
- **A piece standing inside another piece's hole gets its fill.** Before, the
  hole could be handed to the wrong piece and the whole layer printed as wall
  alone. One piece that can't be filled no longer empties the rest of its layer,
  and the warning only blames the surface pattern when the pattern is the cause.
- **Concentric says what it does.** Its description now says it stops and
  starts on every layer and that its rings shift where the form widens or
  narrows; for a roof, use Lines.

## 0.5.1 — 2026-10-01

### Fixed
- **A filled box no longer lifts between its fill and its outline.** The
  outline starts on a corner, a little over a coil width from where the fill
  ends, so the nozzle used to lift and come down once on every pass. Now the
  fill runs straight on into the outline whenever that step stays inside the
  area and clear of every other line.
- **A pass with nothing to print says so plainly.** A pass with no lines on
  it, or lines too short to lay a coil, used to stop Slice job with a
  technical error once it was turned or resized. Now it reads, for example,
  "Pass 2 has nothing to print: it has no lines to follow. Draw on it, or
  remove the pass."

## 0.5.0 — 2026-10-01

### New
- **Fill an area in Draw.** Draw the outline, then pick **Concentric** or
  **Straight rows** from the new **Fill** button and click inside the area,
  or rest the pointer in it and press **F** (Concentric, then Straight rows,
  then empty). Clayline lays the fill coil for you, the way a cup bottom is
  filled. Any area walled in by lines counts, including the pockets where a
  line crosses itself; if it isn't closed, Clayline says so and rings the
  open ends.
  - **Concentric** follows the area's own edge inward as one connected coil,
    so a triangle fills with nested triangles. **Straight rows** lay back and
    forth as one coil where the shape allows, and cross from pass to pass.
  - On the bed a filled area is only shaded, hatched for Straight rows and
    with nested outlines for Concentric. The real coil appears when you slice.
  - A fill follows the lines around it when you move or reshape them. If you
    open a gap it waits, with a dashed ring, and comes back when the gap is
    closed. Undo, saved projects and **Save SVG…** all keep fills.
  - A fill prints just before the lines of its pass and runs straight into
    them when they start close by; otherwise the nozzle lifts once.
  - Seamless spiral is unavailable while an area is filled, and Drape mode
    leaves fills out.

## 0.4.0 — 2026-09-21

### New
- **Stretch a Weave form along one axis.** Under **01 Model › Advanced**,
  **Width ×**, **Depth ×** and **Height ×** stretch the placed form along the
  bed's own axes, on top of the Scale factor. If a height is typed on the
  size line, that height wins outright and Height × resizes the footprint
  needed to reach it instead. 1 leaves an axis alone. The sliced rings stretch with it, the size line shows the
  stretched size, and a saved project or print file brings the stretch back.
  **Reset placement** sets all three back to 1.
- **Export the printed coils as a mesh.** **File → Export Mesh…** writes an
  OBJ, a shape file for a render or another program, of exactly what the
  slice window shows: every printed coil, bead width
  wide and layer height tall, in millimetres on the bed. Travels, the bed and
  the ghosted model are left out. It works in Draw in Clay and in Weave once
  the job is sliced, and the file is named after the print file with
  "-coils" so it never shadows the model it came from.
- **A print file opens as a job.** Drop a print file Clayline saved on the
  Model box, or open it with **File → Open…**, and every setting of that job
  comes back: placement, layers, range, pattern and printer. It then names
  the model it was sliced from; load that model and the job is rebuilt. The
  **Restore pattern from G-code…** button still takes only the pattern.
- **A print file from another slicer becomes a form.** Drop it on the Model
  box and Clayline reads its clay-laying moves, keeps each layer's outer
  wall, and rebuilds the form as a surface you can slice like any model.
  Its layer height becomes yours, the pattern starts plain because the
  file's own texture is already in the surface, and fill lines, extra
  perimeters and a skirt are counted and left out. A spiral file is read
  one revolution per layer. A file with no E axis is read as G1 lays clay
  and G0 travels, and says so.

### Changed
- **Vase mode has its own section.** **Vase mode · spiral rise**, **Z-blend**
  and **Finish with a level rim** moved out of **03 Bottom** into a new
  **04 Vase mode**. Interior, Weave pattern and Printer are now 05, 06 and 07.
  Nothing about how they print changed.

### Fixed
- **The Bottom layers box no longer balloons.** With Bottom layers at 0 or
  blank, the Fill overlap note beside it stretched both boxes to three times
  their height. The note still appears; the boxes keep their size.

## 0.3.1 — 2026-09-19

### Fixed
- **A Weave print no longer starts dry.** With the **Start charge (E)** box
  left blank, the print file skipped the printer's barrel charge, so the first
  layer or two went down with nothing coming out of the nozzle. Blank now means
  what the box says: the printer's own charge. Draw in Clay was not affected.
- **A Weave project saved by an earlier Clayline with that box blank comes back showing 0.**
  Clear the box, or type the charge you want, before you save the print file.

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
