# Safety

A print file moves a real machine. Everything on this page is about the gap between what Clayline can check and what only you can see.

## What Clayline checks, and what it doesn't

Before a file reaches you, Clayline checks it against the printer's limits: the size of the bed, the commands the machine accepts, the numbers in the file's own header. A file that passes is consistent with the printer profile.

That is not the same as safe. Clayline cannot see your actual printer, the clay in the barrel, the nozzle you fitted, the board or canvas on the bed, the space around the machine, or where the emergency stop is. Those are yours.

## Before every print

- **Look the file over.** The 3D preview is drawn from the exact path the printer will follow. Scrub through it. Watch where the nozzle travels between strokes and how high it rides.
- **Read Before you print.** Anything Clayline noticed is listed there, grouped by cause. Click a row to see the spot in the preview.
- **Check the first layer.** The three settings that decide where the first coil lands are described in [Printing](printing.md). A first layer set too low scrapes the bed; too high and the coil never sticks.
- **Keep the emergency stop within reach, and stay with the printer.**

## Drape mode is not a prediction

In drape mode the nozzle rides high and the coil falls onto the work. The preview shows where the nozzle goes, not where a soft, stretching coil will land, how earlier coils will deform under it, or how quickly the growing piece rises toward the nozzle. Start conservatively and watch the clearance the whole time.

## Starting values are not calibration

Clayline starts every new job with reasonable numbers: a clay flow of 1.00, a coil width equal to the nozzle, a layer height of 30% of the nozzle. They are starting points. Your clay, your pressure, and your speed decide the real values. See [Calibration](calibration.md).

## Other printers

If your printer is one of the **community specs** profiles, its bed size, speeds, and start and end commands come from published specifications, not from a print. Compare every number with your own machine before running a file.
