# Glossary

Words as Clayline uses them, in the order you're likely to meet them.

**Coil, bead.** The rope of clay the nozzle lays down. Its width starts equal to the nozzle opening. If a test line comes out wider or narrower, you can enter the measured width.

**Pass.** One run through a design. In Draw in Clay, each row in the Passes list prints once, and repeating a pass builds the piece up one tier at a time.

**Layer height.** How far the nozzle rises for each pass. Clayline starts it at 30% of the nozzle opening, so a 5 mm nozzle gives 1.5 mm layers.

**First layer height.** The nozzle height for the very first pass only. It sets how hard the first coil is pressed onto the bed and never changes the spacing of later passes.

**Work surface above Z zero.** How high the surface you print on sits above the printer's own zero, when you print on a board, canvas, or slab. Every height in the file is raised by this amount.

**Squish.** How much the coil is flattened as it's laid. The Layers readout shows it for your current nozzle and heights.

**Calibrated.** The nozzle rides at layer height and steps up precisely each pass. The default mode.

**Drape.** The nozzle rides high above the work and the coil falls onto the canvas. The open lacework technique.

**Stroke.** One continuous run of clay without lifting. Clayline joins your lines into as few strokes as it can.

**Travel.** A move with no clay flowing, between one stroke and the next. Fewer is better: every travel is a place where the thread stops and restarts.

**Join, weld.** Where two line ends close together are treated as the same point, so a slightly rough hand-drawn corner still prints as one stroke.

**Draw touching rings in one stroke.** Where closed rings touch, the stroke hops across the touching point and keeps flowing. A grid of tangent rings prints as one continuous stroke with no travels.

**Side-by-side join.** How deeply two coils that run next to each other press into one another, as a percentage of the coil width. 20% of a 5 mm coil is 1 mm.

**Clay flow.** A multiplier on how much clay is pushed per millimetre of line. Above 1.00 lays a fatter coil, below it a leaner one.

**Start charge.** The push of clay the printer makes over the centre of the bed before printing, so the barrel is under pressure when the first line starts. Measured in the printer's own units, called E.

**E.** The printer's unit for how far the extruder has pushed. The PotterBot's normal start charge is 3000 E.

**Print file, G-code.** The text file the printer reads: one line per move. Clayline writes it, you take it to the machine.

**SVG.** The file type for line drawings from apps such as Illustrator, Inkscape, or Affinity Designer. Clayline reads the lines in it, not filled shapes.

**Mesh, 3D model.** The file for a solid form: STL, OBJ, PLY, or 3MF. In Weave mode, Clayline cuts it into rings.

**Ring.** One horizontal slice of the model's wall. Each ring becomes one layer of coil.

**Seam.** The point on a ring where a layer starts. Chained keeps starts near each other; Scatter spreads them out; Pinned holds them in one place.

**Vase mode.** The wall climbs in one continuous coil with no layer seams at all.

**Amplitude.** In Weave, how far the wall moves in and out from the original form.

**Wavelength.** The distance from one crest of the wave to the next, in millimetres.

**Twist.** How much the pattern turns from one layer to the next. Zero stacks crests into ribs; half a cycle alternates them into a weave; a small value makes a rising spiral.

**Before you print.** The inspection panel on the right. Print time, clay volume, wet weight, strokes, travels, and everything worth a look, grouped by cause.
