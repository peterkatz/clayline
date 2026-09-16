# Printing

What the printer does with a Clayline file, and the three settings that decide how the first layer lands. Written for the PotterBot 10 XL, the printer Clayline is verified on. Other printers run their own start and end routines from their profiles.

## What happens when you run the file

1. **Home.** The printer finds its zero on every axis.
2. **Move to the centre of the bed**, 20 mm up.
3. **Start charge.** The extruder pushes out a good-sized blob of clay right there, about 7 cc with the standard setting, so the barrel is under pressure before the first line. On a machine that has been sitting, this is what keeps the first layer from printing dry.
4. **Print.** The first layer runs at 30 mm per second, everything after it at 40. Travels between strokes run at the same 40, because faster travels tear the thread.
5. **Finish.** The nozzle lifts 150 mm, the extruder backs off a little to stop oozing, and the head parks at the front of the bed.

The blob and the lifted finish are part of every file. Plan a spot for the blob, or turn it off with the start charge setting below.

## The three first-layer settings

All three live in the workflow. In Draw in Clay they're under 03 Layers and 06 Printer; in Weave under 02 Slice and 06 Printer.

**Work surface above Z zero.** If you print on a board, a canvas, or a slab rather than the bare bed, tell Clayline how high that surface sits above the printer's zero. Every height in the file is raised by this amount. Leave it at 0 for the bare bed. If your first layer scrapes or ploughs into the surface no matter what else you change, this is usually the setting that was missing.

**First layer height.** The nozzle height for the first pass only, above the work surface. It sets how hard the first coil is pressed down. Clayline starts it equal to the layer height, 1.5 mm for a 5 mm nozzle, which presses the coil to less than a third of its width. That grips well on a clean bed. On a soft canvas or with a stiff clay, a higher first layer, 3 or 4 mm, lets the coil sit up instead of smearing. It never changes the spacing of later layers.

**Start charge.** How much clay the printer pushes out over the bed centre before the first line, in the printer's own units. Blank uses the printer's normal amount, 3000 for the PotterBot. A smaller number makes a smaller blob. 0 skips it entirely, which is right when the barrel is already primed from the previous print. The setting is separate for the two modes.

## Building height

In Draw in Clay, height comes from repeating passes. Each pass prints once and rises one layer height above the last. In Weave, the model's own height decides the layer count. **Stack height** in Before you print always tells you how tall the finished piece will be.

## Printing part of a pot

In Weave, **Print selected layers** under 02 Slice prints a band of the wall on its own, moved down to sit on the bed. Use it to test a pattern with a few layers before committing to the whole form, or to reprint a section.

## Pausing between passes

In Draw in Clay, **Pause between passes** under 02 Passes holds the printer for that many seconds after every pass except the last. Give yourself enough time for whatever you do between passes, and check the pause in the preview readout.

## While it prints

Stay with the printer. Watch the first layer land, watch the clearance between the nozzle and the growing piece, and watch the travels, where the thread stops and restarts. Ceramic printers and clay vary from one print to the next, so some trial and error is normal; adjust speed and flow on the machine as you go.
