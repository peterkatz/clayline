# Changelog

What changed in each release of Clayline, newest first. Dates are release dates.

## 0.14.0 — 2026-11-12

### Supports that follow the form
- **Supports** is a new Mesh Mode step. Add a reinforced base, choose a number of
  radial curtains, or pick local attachments on the wall. Curtains stay outside the
  piece and follow its contour beneath outward overhangs. Clayline sizes them from
  **Allowable overhang (%)**; placement and dimension overrides are under **Advanced**.
- The overhang check uses the piece profile without Weaves. Intentional drips and
  ripples do not raise warnings or make automatic supports grow. A lower allowable
  percentage asks for more contact with the clay underneath.
- Bases and curtains each have independent **Weaves** and **Images** switches. Their
  patterns ease where needed to keep the added clay connected and clear of other
  paths. The original sculpture wall stays complete at each curtain attachment.
- The preview shows the actual support clay in blue. **Span warnings** in the preview
  legend and **Show span warnings (red dots)** in the inspection panel switch the
  markers on or off without rebuilding the path. The choice survives a restart.
- The final check distinguishes supported attachment targets from spans still needing
  support between curtains. A route without a verified foundation or clearance cannot
  be exported, and its inspection points to the failed support segment.
- Projects retain support placement and appearance. Supported G-code can restore its
  editable job when the original model is supplied. Printed-coil OBJ exports include
  the supports; Designed surface exports remain the sculpture's surface.
- Larger decorated support jobs fit the bounded session cache, and completed checks
  release planning data they no longer need. Complex jobs can take several minutes
  to check before Download becomes available.

The percentage describes nominal geometric contact, not a guarantee about wet clay.
Check the final path and test the material and flow for the intended print.

## 0.13.6 — 2026-11-11

### The wall stands on the base again
- With **Vase mode** on and bottom layers that take turns, the first turn of wall that
  climbs now stands on the clay under it. Since 0.13.3 the turns under it were laid flat
  on their own layer's outline, and the bottom beside it stopped at where that turn
  started; on a foot that flares out, the turn's far side leaned out past both, over
  nothing, and a tall piece could fail there. Now the flat turns keep the same path round
  as the turns that climb, so every turn steps out from the one under it as the turns
  above do, and the top bottom layer reaches out under the first climbing turn.
- The same goes for a bottom whose layers do not take turns: its first layer reaches out
  under the wall's first turn as it climbs off the bed.
- **Form from a print file** reads a Vase print whose bottom layers take turns, however
  many there are, where before it read two at most; one with a weave still makes no
  form. A print made by 0.13.3 to 0.13.5 with those flat turns may now not make one.

## 0.13.5 — 2026-11-11

### Every bottom laid the new way
- The **Rim in, centre out** switch is gone. Every bottom is laid that way now: each
  layer ends beside its wall, and where the layers can take turns, the whole base is one
  unbroken line. A job saved before lays its bottom this way when you slice it again.
- **Alternate bottom direction** is off for a new job, so a new job's bottom layers take
  turns. Turn it on for rows that cross the layer below.

## 0.13.4 — 2026-11-11

### Bottoms a weave pinches
- Where weaves loop tightly enough to poke sharp points into a bottom, that bottom still
  goes in as one spiral inside the wall. Before, the points could cut a turn of the
  spiral in two, and that layer fell back to the form's outline, showing outside the
  wall.

## 0.13.3 — 2026-11-11

### Mesh Mode bottoms that take turns
- **Rim in, centre out** replaces Spiral in and back out, under Inside and floor, on for
  a new job. The bottom layers take turns: one goes from the wall in to the centre, the
  next from the centre back out to the wall, and the top one always ends at the wall,
  where the wall carries on up. A layer laid from the wall in puts its turn of wall down
  first and starts right where that turn ends. So each layer starts where the one below
  ended, and the whole base is one unbroken line with no lift and no line printed
  through a floor.
- With **Vase mode** on, the wall's turns under the base are now laid level, each
  stepping up a layer where it starts. Only the turn on the top bottom layer climbs, as
  every turn above it does. The small gap that sat under the first turn, where it
  climbed off the bed, moves up under that top turn.
- This needs every bottom layer to be one plain spiral: **Alternate bottom direction**
  off, one piece, and no hole through the bottom; with Vase mode on, it also needs a top
  that does not split into pieces for **Z-blend** to follow, and with Vase mode off, a seam
  that is not scattered. A pattern fitted with profile blend, which rides the wall up and
  down, must leave the wall under the base level. Alternate bottom direction is on for a
  new job. Otherwise each layer ends beside its own wall, and the nozzle lifts to reach the
  next one; where Clayline can say why, it does. Past a short step the nozzle lifts rather
  than print a line through clay.
- A project saved with Spiral in and back out on opens with Rim in, centre out on. An
  older Clayline cannot open a project saved with it on.

### Every bottom laid inside its wall
- Each bottom layer is now laid inside the wall as it actually prints, not to the form's
  outline. Where a weave swings the wall in and out, the edge of the floor follows it:
  no floor shows outside the wall, and the gap that opened where the wall swings out is
  closed. This is always on. A woven job saved before lays its bottom inside its wall
  when you slice it again; a wall with no weave prints exactly as before.
- Where a weave loops too tightly at a sharp hollow for the floor to follow it, that
  layer stops at the form's outline where the wall swings out, still inside the wall.
  Where even that cannot be done, the layer keeps the outline, and Clayline says so.

## 0.13.1 — 2026-11-10

### Mesh Mode bottoms with nothing crossing them
- **Spiral in and back out**, a new switch under Inside and floor, on for a new job. A
  bottom spiral now goes in to the centre and comes back out between its own rings, so
  it starts and ends beside the wall. Before, it ended at the centre and the nozzle
  printed a line back out to the wall, at the same height, through the spiral it had
  just laid.
- The rings of such a spiral are joined along one line that runs in from where the
  wall starts to the centre. You will see that line in the floor.
- Each ring is left open where it is joined, and what closes those openings is the
  width of the lines either side. Clayline measures each layer and lays the spiral only
  where it covers the floor as well as a spiral laid the old way, to within about a
  square millimetre. With Fill overlap near 50% that is nearly every round bottom. With
  less it is some layers and not others: about half of them at the 20% a new job starts
  with, and none under 10%.
- Any other layer is laid from the centre outward instead, and the nozzle lifts and
  crosses to the centre over the layer already finished, before any of the new layer is
  down. A bottom with a hole through it always is. So, usually, is one whose wall starts
  well outside the bottom's edge, or on a corner when Fill overlap is under 40%.
- Where every bottom layer is laid in and back out, which needs **Alternate bottom
  direction** off, and **Vase mode** is on, the nozzle steps straight from the wall into
  the next bottom layer. The whole base and the wall above it are then one unbroken line
  with no lift. With Vase mode off the nozzle lifts once per layer, in place, to step up.
- Where the pattern swings the wall's start a little outside the bottom, the bottom
  now joins it with a short step instead of lifting.
- With **Alternate bottom direction** on, only the first bottom layer is a spiral. The
  rows above it are laid in whichever direction ends nearer the wall. The nozzle still
  lifts to reach them and to leave them, rather than print across them.
- A job or print file saved before this release opens with the switch off and prints
  the bottom it always did. Turn the switch on to change it.

## 0.12.2 — 2026-11-05

### Plainer words
- If Layer height, First layer height or Ripple length is empty, Slice waits and the
  note says which box to fill in.
- Any other number Clayline can't use now names the box as you see it, such as "Join
  ends that nearly touch must be at least 0 mm."
- Warnings say which pass they're on, and say in plain words when a shape was left out
  and why.

## 0.12.1 — 2026-11-05

### Shapes and drawings that were turned away now print
- Many plain cylinders were turned away at the final check because of a tiny
  measuring slip at the very end of the line. They now slice and print. Shapes that
  already worked come out exactly as they did.
- Some busy drawings, such as floor plans, were turned away because a line came back
  past clay it had just laid. Clayline now lifts those short stretches and checks
  again. If it still can't pass, you see the same note as before.

### Lines from a drawing
- If the coil width box is empty when you add a drawing, the note under its pass asks
  for a coil width. Type one and the lines start, with nothing else to press.
- If you change saved lines in another program, your change stays. It's no longer lost
  the next time you change the size or coil width. **Use original** isn't offered for
  a file changed this way.
- A shape with no line now says what to do, such as "To print this circle, give it a
  line in your drawing program."

## 0.12.0 — 2026-11-04

### Drawings made of filled shapes now print
- Add a logo, some lettering or a drawing from Illustrator, and Clayline makes
  lines from what it shows when the file arrives. They appear over a faded copy of
  the drawing before anything prints, and real lines in the file are kept as drawn.
- **Use original** puts the file back on its pass, and **Make lines again** makes
  them afresh. Saving lines always asks where and makes a new file, so the file you
  added is never written over. The original travels inside the saved lines.
- The note under a pass says what it needs, such as a bigger size so small gaps stay
  open. A photo offers **Trace over it**, which opens it in Draw.
- Lines size themselves to fit the bed unless you type a size. A typed size stays,
  including when saved lines are added again.
- Drawings that already hold lines print exactly as they did.
- A drawing too short to print now says so in words.

### Mesh Mode
- **Lay flat…** sets any surface of the model on the bed: rest the pointer on a
  surface and click. Undo turns it back.
- A line under the model's name says when its base is tilted and by how much, and
  **Flatten base** sets the nearest flat base down.
- **Remove** takes the model off the bed without restarting. Undo brings it back.
- **Upload image…** now lets you choose pictures in the Mac app: PNG, JPEG, TIFF,
  WebP, BMP, HEIC and Photoshop, up to 17 MB and 16 million pixels. A file over the
  limit gets a plain sentence.
- Changing a slice setting during a slice now ends that slice cleanly, so an old
  result can't land under the new setting.

## 0.11.0 — 2026-11-02

- Rename the mesh workspace **Mesh Mode**, keeping **Weave** as the waveform effect.
- Organize both modes into independent, locally remembered accordion sections.
- Type precise values beside sliders, including between drag increments, with
  Enter/blur to apply, Escape to cancel, range feedback, and one Undo per edit.
- Add **Invert wave** and **Reverse wave** for the selected Weave's saved curve.
- Default new repeating Images to proportional **Pattern size** with whole-copy
  seamless fitting. Keep **Set repeats & height** for deliberate stretching and
  preserve the appearance of existing patterns and projects.
- Offer **Printed coils** and **Designed surface** OBJ exports. The new surface
  export preserves the whole placed source, bakes supported geometric effects,
  checks cross-section agreement, and explains unsupported designs.
- Enter exact one-based move numbers in the preview scrubber.
- Check first-layer links between separate fill pockets against the actual
  material. An unproved link now uses the existing safe travel and warning;
  contained joins and ordinary print paths retain their exact bytes.
- Align release checks with the current layer, metadata, and continuity
  contracts while preserving historical machine evidence. Explicitly deferred
  Revision 3 acceptance remains separately runnable.

## 0.10.0 — 2026-11-01

### New
- **Images on Mesh walls.** Add up to three Images alongside the three Weaves.
  Choose from 80 original 16-bit relief maps, including the corrected 1970s
  paisleys numbered 61–80, or upload grayscale, color, or transparent artwork.
  Middle gray preserves the wall, lighter tones push outward, and darker tones
  pull inward. Transparent areas leave the wall and clay flow unchanged.
- **A visual Image gallery.** Browse thumbnails with each design's number and
  name, search the catalogue, or filter to the paisleys. Choosing artwork keeps
  the selected Image's placement, depth, and clay-flow settings.
- **Repeat around or Place once.** Repeat a whole field around the vessel, with
  rotation and spacing fitted automatically to close the artwork join. Place
  a single stencil in millimeters along the original surface, including across
  that join. Resize, reposition, rotate, flip, invert, or feather the Image.
  Blend edges previews a reversible repeat for uploads with mismatched edges.
- **Each Image has the familiar Weave controls.** Wave depth, Clay along the
  wall, an editable Extrusion track with Ridge boost and Trough boost, Phase,
  and Skip layers all belong to the selected Image. Images and Weaves combine
  on the original exterior; Scatter and Pinned print starts leave artwork in
  place. Vase mode samples the continuously rising surface.
- **Fade in and Fade out for Images and Weaves.** Ease an effect's relief and
  extrusion together over a chosen number of layers, at each active run or
  at the beginning and end of the wall. Zero preserves the existing switch.
- **Portable artwork.** Saved patterns, projects, and restorable Clayline print
  files retain uploaded artwork and every Image's settings.
- **Print-file surfaces keep their relief once.** When a print file becomes
  the loaded model, its Images are parked alongside its Weaves. Choosing the
  original model restores the original effects and their enable switches.

### Changed
- Patterns and projects using Images or nonzero fades need Clayline 0.10.0 or
  later. Existing Weave-only jobs with zero fades retain their toolpaths.
- The website and help now explain drawing, Mesh patterns, Images, portable
  projects, and the preview-to-print workflow.

## 0.9.0 — 2026-10-21

### New
- **Up to three weaves on one wall.** Shape Weave 1 as before, then click
  **Add weave** at the top of the Pattern section to lay another wave over it,
  and a third if you like. Each weave has its own shape, amplitude,
  wavelength, twist, extrusion track, wave depth, Clay along the wall and skip
  layers, so one long, slow wave can carry a fine one. Click a weave's name to
  work on it: presets and Noise change only that weave, and so does a texture
  on Weave 2 or 3. On Weave 1 a texture sets the whole wall as it always has,
  vase mode and Weave 1's Clay along the wall included. **Use this weave**
  leaves a weave out of the print but keeps its settings, so you can compare,
  and **Remove** takes Weave 2 or 3 off; Undo brings it back. The Pattern preview shows the weaves together,
  vase mode climbs with all of them in its one coil, and **Save pattern**,
  **Load pattern** and **Restore pattern from G-code…** carry every weave.
- **Every weave is checked.** Each weave says when its wave is too fine, and
  with more than one weave the line under Wavelength names the layers where
  each weave's wave count steps on a taper. A line says how far all the
  weaves swing together, and the largest pinch-free swing turns every weave
  down by the same share. Where the weaves' extrusion tracks and Clay along
  the wall together would push too little or too much clay, Clayline keeps it
  between a quarter and three times a plain coil, and a warning names the
  weave and the layers.
- **Keep the same number of waves.** Each weave has this switch right under
  its Wavelength, off until you switch it on. It fits the weave's waves where
  each part of the form is widest and keeps that number all the way up, so
  the ridges stack up a taper instead of stepping; the waves sit closer where
  the form narrows, and a note names any layers where they crowd closer than
  your coil.
- **File → Open Recent.** The last ten projects you opened or saved, and
  models, drawings and print files you opened, newest first, as in other Mac
  apps; choose one to open it again.
- **A print file brings back its form.** Drop a print file Clayline saved on
  the Form box with no model loaded, and every setting comes back with a form
  made from the print file's printed surface, pattern and all, at the size and
  angle it printed. Every weave is switched off so the pattern isn't laid on
  twice. A button under the form's name swaps in the original model when you
  have it, placed as it printed, and switches the weaves back on. A print made
  with Stack pieces, one whose form splits or joins up the way, and often one
  woven in vase mode give no form; for those, the middle of the window names
  the model the print file was sliced from, with a button to choose it.

### Changed
- **A file with more than one weave, with Weave 1 switched off, or with Keep
  the same number of waves on, needs Clayline 0.9.0 or later.** An earlier
  Clayline can't open a pattern or project that carries Weave 2 or 3, has
  Weave 1 switched off, or keeps the same number of waves on any weave, and
  can't bring the settings back from such a print file. A job with only Weave 1,
  switched on and with Keep the same number of waves off, prints exactly as
  it did in 0.8.3, and its pattern and project still open there.
- **The guide** now says that Clay along the wall pauses on its weave's plain
  layers when that weave skips layers. On Weave 1 it always has.

### Fixed
- **Load pattern lets you choose a saved pattern again in the Mac app.** Its
  window offered only models, projects and print files, so a pattern file was
  greyed out. It now opens a window of saved patterns.

## 0.8.3 — 2026-10-07

### New
- **A 3Dconnexion 3D mouse moves the 3D view.** Slide the cap to pan, push
  or pull to zoom, and tilt or twist it to turn the view, the same way it
  works in Refab. It only moves your view of the piece, never the piece on the
  bed, and it doesn't add undo steps. It needs 3Dconnexion's own driver
  installed.

## 0.8.2 — 2026-10-07

### Fixed
- **Fewer crossings where the form is one piece.** Where a layer's fill comes
  in separate parts, the line now joins them in the order that crosses least,
  and a step onto a rib end in an inward corner of the wall is no longer
  refused by a hair. On a head with a split near the top, the short crossings
  that stacked up layer after layer on the upper shoulder are gone. Nothing is
  printed twice and no new clay is laid over open fill; where the parts of the
  fill are more than a coil apart, the nozzle still crosses.
- **Stack pieces no longer waits five seconds between a piece's layers,** so
  a small piece stacks several layers in a row instead of taking turns one
  layer at a time.
- **A new Weave job starts with a flat pattern,** not a sine wave.
- **Weave's settings are in a new order:** Form, Printer and coil, Wall,
  Pattern, Inside and floor, then Print. Each setting sits with what it
  changes: the printer, nozzle and clay flow together near the top, the
  pattern right after the wall, the bottom with the inside, and Print selected
  layers and Stack pieces at the end. Nothing works differently.

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
