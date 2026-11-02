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

To update, save any job you want to continue as a **Clayline project**, quit the app, then download the new version and drag it over the old one. Your saved projects and source files stay where you saved them. Open a project to bring back its design and settings. Images and effect fades are available in Clayline 0.10.0 and later.

## The studio at a glance

The top bar has two buttons that switch modes: **Draw in Clay** for line drawings, filled areas and layered tiles, and **Mesh Mode** for 3D models shaped with Weaves and image relief. Next to them, **mm / in** chooses how sizes are shown to you. Files always stay in millimetres inside.

Each mode is laid out the same way:

- **Left**: the workflow, numbered from 01 downward. Work through it top to bottom.
- **Middle**: the preview. **2D plan** looks at the bed from above; **3D toolpath** shows every move at its real height. Drag to orbit, scroll to zoom.
- **Right**: **Before you print**, the inspection panel. It fills in after you slice: how long the print takes, how much clay it uses, how many separate strokes and travels there are, and anything worth a look before printing.

A 3Dconnexion 3D mouse moves the 3D view if 3Dconnexion's driver is installed: slide the cap to pan, push or pull to zoom, tilt or twist to turn. It never moves the piece itself.

The **Slice** button at the bottom of the workflow builds the toolpath. Nothing prints from there. It only prepares the file.

## Try an example first

Clayline comes with a gallery of 98 example drawings. In **Draw in Clay**, press **Browse the gallery** under 01 Design, open a folder, and choose a drawing. Press **Slice job** and look around: the plan, the 3D toolpath, and Before you print. Nothing reaches a printer until you save a file and take it there yourself.

## Try Images on a model

1. Switch to **Mesh Mode**, load an STL, OBJ, PLY or 3MF, check its size, then press **Slice form**.
2. In **05 Images**, press **Add image**. Choose a depth map from the 80-image catalogue, or **Upload image…** for your own grayscale or color artwork.
3. Use **Repeat around** to cover the wall, or **Place once** for a single stamp. Move, resize or rotate it; the preview and fitted-repeat readout show the result.
4. Adjust **Amplitude**, clay flow and active layers. Add **Fade in** or **Fade out** to ease the effect in and out. You can also add Weaves in **04 Weaves**, with independent settings.
5. Inspect the final path and save a project before exporting the print file. The project includes your model and uploaded artwork.

The catalogue includes soft fields, Truchet patterns, botanical motifs and 20 paisley designs. See [Images](weave.md#05-images) for placement, seamless repeats, edge blending and the shared flow controls.

## Choose your printer

In **Draw in Clay**, open **06 Printer**; in **Mesh Mode**, open **02 Printer and coil**. Pick your machine from the list.

**PotterBot 10 XL · verified** means every fact in that profile, from the size of the bed to the commands that start and end a print, was checked against a real print on that machine.

The others are marked **community specs**: their bed sizes and speeds come from published specifications, not from a print. If you use one of them, compare its numbers with your own printer before running a file, and start with a small test.

The printer choice sets the bed size you see in the preview, the print speeds, the nozzle sizes offered, and the commands at the start and end of every file.

## Getting a file to the printer

After you slice, **Download G-code** in the right-hand panel saves the print file through the normal Mac save window. **File → Export G-code…** (Shift-Command-E) does the same, **File → Export Mesh…** offers Printed coils with layer lines after slicing, or a Designed surface with geometric effects and no layer lines, and **File → Open…** (Command-O) loads drawings or models. Command-S is the whole job, not the print file: see Saving your project in [Draw in Clay](tiles.md) and [Mesh Mode](weave.md). The file is named after your design, and the save window is where you can change that.

Copy the file to your printer the way you already do for any print. Clayline never sends anything to the machine itself.
