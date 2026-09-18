<div class="cl-hero" markdown>

![](assets/clayline-mark.svg){ .cl-hero-mark alt="" }

# Clayline Toolpath Studio

<p class="cl-promise">Drawings and 3D models in.<br>Print files for clay paste printers out.</p>

<div class="cl-hero-actions" markdown>
[Download for Mac](https://github.com/peterkatz/clayline/releases/latest){ .md-button .md-button--primary }
[Read the guide](install.md){ .cl-quiet }
</div>

<p class="cl-fineprint">For Apple silicon Macs running macOS 14 or later. Free and open source.</p>

</div>

<figure class="cl-demo" markdown>

![Clayline's studio with a drawing on the bed and its finished toolpath](assets/clayline-demo.gif)

<figcaption>A drawing on the bed, and the path the nozzle will follow through it.</figcaption>
</figure>

## Two ways to work

<div class="cl-cards" markdown>

<div class="cl-card cl-card--draw" markdown>

![A drawn pattern standing up in coils of clay](images/tiles-3d.png)

### Draw in Clay

Draw a pattern as lines, either in Clayline itself or in any vector drawing app saved as an SVG, or start from the gallery of 98 example drawings that comes with the app. Clayline turns every line into a coil of clay, joins lines where they meet, and repeats the design pass after pass to build height. Print it flat as a tile, or let the coil drape from a raised nozzle for open lacework.

</div>

<div class="cl-card cl-card--weave" markdown>

![A vessel sliced into rings of woven wall](images/weave-sliced.png)

### Weave

Open a 3D model of a tumbler or vessel. Clayline slices it into rings and prints the wall as one continuous thread of clay, with a wave pattern you shape yourself: ribs, spirals, crisp edges, or a texture traced from a real print.

</div>

</div>

Both modes show you the exact path the printer will follow, in 2D and 3D, and a **Before you print** panel that lists everything worth a look before you commit clay.

## Start from a drawing

<div class="cl-gallery" markdown>

![Celtic triquetra](assets/gallery/celtic-triquetra.svg)

![Rosette](assets/gallery/rosette.svg)

![Flower of life](assets/gallery/flower-of-life.svg)

![Alhambra lattice](assets/gallery/alhambra-lattice.svg)

![Petal flower](assets/gallery/petal-flower-155mm.svg)

![Moorish lattice](assets/gallery/moorish-lattice.svg)

</div>

<p class="cl-fineprint">Six of the 98 drawings that come with the app. Open one, redraw it, or bring your own.</p>

## Where to start

- [Install](install.md): get the app running and pick your printer.
- [Draw in Clay](tiles.md): from a line drawing to a printed tile.
- [Weave](weave.md): from a 3D model to a woven vessel.
- [Printing](printing.md): what the printer does with the file, and the three settings that decide how the first layer lands.
- [Troubleshooting](troubleshooting.md): the first layer scraped, the start blob is huge, the model loads sideways.

## Built for real printing

Clayline was built around a PotterBot 10 XL and shaped by real prints. Everything runs on your Mac: no account, no cloud, no internet connection needed. Nothing ever prints from the app itself. It writes a file, you look it over, and you take it to the printer.

!!! warning "Printer files move real machinery"
    Clayline checks every file against the printer's limits, not against your actual printer, clay, nozzle, or the space around it. Look the file over, keep the emergency stop within reach, and stay with the printer. Read [Safety](safety.md) before your first run.
