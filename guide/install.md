# Install

## What you need

- A Mac with Apple silicon (M1 or later).
- macOS 14 or later.
- A clay paste printer that takes standard print files. Clayline is verified on the PotterBot 10 XL and ships starting settings for several other machines.

Clayline does not need an internet connection, an account, or anything else installed.

## Get it running

1. Download the latest version from the [Releases page](https://github.com/peterkatz/clayline/releases/latest). It arrives as a zip file.
2. Double-click the zip. A **Clayline** app appears next to it.
3. Drag **Clayline** into your Applications folder.
4. Open it. It starts in a moment and opens the studio in its own window.

To update, download the new version and drag it over the old one. Your settings stay.

## The studio at a glance

The top bar has two buttons that switch modes: **Draw in Clay** for line drawings and tiles, and **Weave · mesh** for 3D models. Next to them, **mm / in** chooses how sizes are shown to you. Files always stay in millimetres inside.

Each mode is laid out the same way:

- **Left**: the workflow, numbered from 01 downward. Work through it top to bottom.
- **Middle**: the preview. **2D plan** looks at the bed from above; **3D toolpath** shows every move at its real height. Drag to orbit, scroll to zoom.
- **Right**: **Before you print**, the inspection panel. It fills in after you slice: how long the print takes, how much clay it uses, how many separate strokes and travels there are, and anything worth a look before printing.

The **Slice** button at the bottom of the workflow builds the toolpath. Nothing prints from there. It only prepares the file.

## Choose your printer

Open **06 Printer** in either mode and pick your machine from the list.

**PotterBot 10 XL · verified** means every fact in that profile, from the size of the bed to the commands that start and end a print, was checked against a real print on that machine.

The others are marked **community specs**: their bed sizes and speeds come from published specifications, not from a print. If you use one of them, compare its numbers with your own printer before running a file, and start with a small test.

The printer choice sets the bed size you see in the preview, the print speeds, the nozzle sizes offered, and the commands at the start and end of every file.

## Getting a file to the printer

After you slice, **Download G-code** in the right-hand panel saves the print file through the normal Mac save window. **File → Export G-code…** (Command-S) does the same, and **File → Open…** (Command-O) loads drawings or models. Give the file a name under **07 Export**, or leave the box blank to name it after your design.

Copy the file to your printer the way you already do for any print. Clayline never sends anything to the machine itself.
