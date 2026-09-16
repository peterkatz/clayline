# Calibration

Clayline's starting numbers are reasonable, not measured. Your clay, your pressure, and your speed decide the real ones. Three measurements get you most of the way.

## 1. Coil width

Print a single pass of a simple design, a straight line or a gallery tile at one pass, at your usual pressure and speed. Measure the laid coil with calipers in a few places.

If it's wider or narrower than the nozzle opening, tell Clayline. In Draw in Clay, open **Advanced** under 03 Layers, choose **Measured**, and enter the width. In Weave, enter it as **Coil width** under Advanced in 02 Slice. The side-by-side spacing, the join depth, and the clay estimate all follow from this number.

## 2. Clay flow

If the coil looks starved (thin, broken, ragged edges) raise **Clay flow** under 06 Printer above 1.00. If it piles up and smears, lower it. Change it a little at a time, 0.05 or 0.10, and reprint the same test.

Clay flow only changes how much clay is pushed per millimetre of line. It doesn't change the spacing of lines, so a design that was drawn for a 5 mm coil stays laid out for a 5 mm coil.

## 3. First layer

Print the first pass only and look at it. A coil that's smeared flat and dragged means the first layer is too low: raise **First layer height**, or if you're printing on a board or canvas, set **Work surface above Z zero** first. A coil that sits up round and doesn't grip means it's too high.

## Layer height

Clayline starts layer height at 30% of the nozzle. Once the coil width is measured and the flow looks right, this is the number to adjust for how tall each pass builds. Lower gives a tighter, stronger wall; higher builds faster and shows more coil.

## What's still provisional

Clayline's standard join depth of 20% and its starting flow of 1.00 have not yet been confirmed by a full accepted tile print on the PotterBot. Treat them as starting points, not results. The formal calibration prints that Clayline can generate, a flow ladder, a closed ring, and a pair of touching rings, are not in the app yet; they're available to people who run Clayline from its source code.
