# Troubleshooting

## At the printer

**The first layer scrapes the surface or ploughs into it, whatever I set.**
You're printing on something above the bare bed. Set **Work surface above Z zero** to the height of your board, canvas, or slab. Every height in the file is raised by that amount. Then adjust **First layer height**.

**The first layer prints dry, or nothing comes out for the first while.**
The barrel wasn't under pressure when the first line started. Leave **Start charge** blank so the printer's full charge runs, and check that the previous print didn't leave the barrel empty. The PotterBot's normal charge is 3000; a much smaller number starts most jobs dry.

**The blob at the start is huge, or it's in the way.**
That's the start charge. Type a smaller number under 06 Printer, or 0 to skip it when the barrel is already primed from the last print.

**The thread tears or breaks between strokes.**
Every travel is a stop and restart. Fewer travels is the real fix: draw joins as real overlaps, keep gaps under about 0.8 mm, and turn on **Draw touching rings in one stroke**. **Protect the thread** under 04 Path adds clay where the thread starts, ends, and bridges. Check **Travels** in Before you print after each change.

**The coil is thin and ragged, or fat and smeared.**
Clay flow. See [Calibration](calibration.md).

## In Draw in Clay

**My drawing loads but parts of it are missing.**
Those parts were filled shapes, not lines. Clayline reads lines only and lists what it dropped in Warnings. Redraw them as lines.

**The design is tiny or enormous on the bed.**
The file wasn't saved at real size in millimetres. Set **Size** in its row under 02 Passes, or fix the drawing and load it again.

**Warnings says lines run too close together.**
Two separate lines sit closer than the coil can keep apart, so they'll smear into one. Space them out, or let them touch fully so they fuse. **Show me** jumps to the spot.

**Seamless spiral won't turn on.**
It needs Calibrated mode and every stroke closed into a loop. An open line anywhere in the design disables it.

**Settle into valleys says there's nothing below.**
It needs stacked passes. Add a second pass with **Repeat pass**.

**Nothing changes in the preview when I edit.**
The preview is showing **Sliced**, the checked path from the last slice. Slice again after an edit, or switch to **Draw** to see the editable drawing.

## In Weave

**The sliced rings look like a tangled contour map instead of stacked walls.**
The model's up axis is wrong. Change **Up axis** under 01 Model. Rhino exports are usually Y up.

**The model loads at the wrong size.**
Clayline assumes one unit in the file is one millimetre. Type the real height on the size line under 01 Model and the whole form scales with it.

**Solid or Infill can't be chosen.**
Vase mode is on. Turn it off under 03 Bottom first.

**Export is greyed out.**
It unlocks after the final path passes every check. Look at Warnings in Before you print for what's holding it.

**I want to reprint exactly what I printed last month.**
Drop the print file Clayline saved on the box under 01 Model, or use **Restore from G-code…** under 07 Export. Every setting and the pattern come back. Keep the model file next to it.

## The app

**It won't open, or macOS says it can't be opened.**
Clayline needs a Mac with Apple silicon running macOS 14 or later. On an Intel Mac or an older system it won't run.

**My settings went back to the defaults.**
The round arrow at the top of the workflow resets settings for that mode. Each mode's reset leaves the other mode alone. **Undo** at the top of the window steps back through settings changes.

**Something else.**
Report it at [github.com/peterkatz/clayline](https://github.com/peterkatz/clayline) under Issues, with the drawing or model and the settings you used.
