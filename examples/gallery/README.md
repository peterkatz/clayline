# Tile gallery — every design in one place

All 68 tile designs — SVG + preview PNG pairs — live in this one directory,
with `proof-sheet.jpg` showing everything on a single page. Unless noted, tiles
are **6 × 6 in (152.4 × 152.4 mm)**, mm units, stroked centerlines, designed
**tangency-first** so the kiss-hop planner fuses each tile into as few strokes
as physically possible.

The parametric sources live here too — **edit the generators, not the SVGs**:

- `generate_tiles.py` — the three photo tracings (production test fixtures)
- `generate_variations.py` — Moroccan/Arabic/Andalusian set + shared primitives
- `generate_variations2.py` — Indian/Tibetan set (adds `swirl()` and `billiard()`)
- `generate_variations3.py` — set 3: Celtic, Art Deco, Japanese, Persian, Norse, Islamic-star & sacred geometry
- `generate_variations4.py` — set 4: Aztec, Scandinavian folk, Ottoman Iznik, Byzantine, Chinese, Roman, atomic age & more

Run them from this directory (they write into the current directory, or pass
an output directory as the first argument):

```sh
cd examples/gallery
python3 generate_tiles.py && python3 generate_variations.py && python3 generate_variations2.py && python3 generate_variations3.py && python3 generate_variations4.py
```

The Mac app ships these drawings, together with `examples/clayline-tiles` and
`examples/clayline-zoo-tiles`, sorted into folders by tradition. The sorting lives
in [`../gallery-manifest.json`](../gallery-manifest.json): every SVG in the three
folders must be listed there exactly once, and `python3 tools/build_gallery.py
--check` (run by the tests and the packager) fails when one is missing. Add a new
tile to the manifest in the same change that adds the tile.

## Photo tracings — Pete's hand tiles, digitized

Idealized SVG line-work digitized directly from the three reference photos
(`docs/reference/IMG_3074/3073/3071.jpg`), authored side-by-side against them
(see `compare-*.jpg`, photo left / tracing right). These are the canonical
production fixtures copied into `tests/fixtures/svg/` (Pete approved the swap
2026-07-15; verified in `docs/verification/M7/STATUS.md`). The rosette's inner
wreath rings are internally tangent to their outers, so each tile fuses into
as few strokes as physically possible.

| Tile | Photo | Strokes / travels (`--kiss --layers 1`) | PRD §9.2 target |
|---|---|---|---|
| `rings-grid.svg` | IMG_3074 | **1** / 0 | 1 ✓ |
| `rosette.svg` | IMG_3073 | **1** / 0 | 1 ✓ — resolved the former M7 blocker |
| `petal-flower.svg` | IMG_3071 | **2** / 1 | ≤ 2 ✓ — the coiled hub spiral is an open stroke, deliberately |

## Variations, set 1 — Moroccan, Arabic & Andalusian

Measured with this repo's planner, `--kiss --layers 1 --z-mode drape`, 2026-07-15.

| Tile | Influence | Strokes / travels | Notes |
|---|---|---|---|
| `khatam-star.svg` | Moroccan khatam | **1** / 1 | two woven rounded squares, hub rosette, dots off every star point |
| `zellige-rosette.svg` | Fez zellige | **1** / 1 | 8-petal sunburst inside a 20-lobe multifoil border |
| `alhambra-lattice.svg` | Alhambra | **1** / 1 | 4×4 deeply overlapping circle weave (laps deliberate — drape mode) |
| `quatrefoil-grid.svg` | Sevillian azulejo | **1** / 1 | 2×2 quatrefoils with ring connectors |
| `octagon-cross.svg` | zellige star-and-cross | **1** / 1 | four rounded octagons, center diamond, edge rings |
| `multifoil-medallion.svg` | Córdoba multifoil | **5** / 13 | medallion is 1 stroke; 4 open spiral tendrils by design (each ≤0.2 mm from the body — fuses in clay) |
| `mudejar-weave.svg` | Mudéjar lacería | **1** / 1 | concentric square/circle/square/circle weave stitched by four petals |
| `andalus-vine.svg` | Andalusian arabesque | **5** / 13 | rosette is 1 stroke; 4 open spiral tendrils kiss the diagonal petals |
| `fez-medallion.svg` | Fez medallion | **1** / 1 | three concentric bands fused through tucked rings |
| `granada-sunburst.svg` | Granada | **1** / 1 | 16 alternating rays, corner rings threaded onto the long diagonals |

## Variations, set 2 — Indian & Tibetan

Planner-verified 2026-07-15, same flags.

| Tile | Influence | Strokes / travels | Notes |
|---|---|---|---|
| `lotus-mandala.svg` | Indian/Tibetan lotus | **1** / 1 | two petal rings threaded on binding circles |
| `endless-knot.svg` | Tibetan shrivatsa | **1** / 1 | the whole tile is ONE closed line weaving over itself |
| `gankyil.svg` | Tibetan wheel of joy | **1** / 1 | three swirled commas in a ring, lotus surround |
| `kolam-weave.svg` | South Indian kolam | **1** / 1 | one looping line threading a field of nine dots |
| `paisley-quartet.svg` | Indian boteh | **1** / 1 | large + small paisleys clustering around a hub |
| `dharma-wheel.svg` | Tibetan | **1** / 1 | eight lens spokes through the rim, eight dots |
| `yantra-star.svg` | Indian yantra | **1** / 1 | two woven rounded triangles bound by a circle |
| `marigold-mandala.svg` | Indian garland | **1** / 1 | 12 long petals threading two multifoil rings |
| `conch-mandala.svg` | shankha | **2** / 4 | grand open spiral (by design) inside a multifoil ring |
| `padma-gate.svg` | Tibetan mandala palace | **1** / 1 | square walls, four gates, lotus wheel inside |

## Variations, set 3 — Celtic, Art Deco, Japanese, Persian, Norse & sacred geometry

Planner-verified 2026-07-25, `--kiss --layers 1 --z-mode drape`; every tile PASSes and
prints as **one carried drape stroke** (a single real travel).

| Tile | Influence | Kiss-components | Notes |
|---|---|---|---|
| `celtic-triquetra.svg` | Celtic | **1** | three vesica lobes woven through a ring |
| `celtic-shield-knot.svg` | Celtic | 2 | two woven rounded squares, corner rings, hub |
| `celtic-triskele.svg` | Celtic | 5 | three spirals from a hub in a ring (spirals open by design) |
| `celtic-cross.svg` | Celtic | 2 | ringed cross, bold bars through a nimbus |
| `deco-sunburst.svg` | Art Deco | **1** | alternating rays over a stepped band |
| `deco-fan-scallop.svg` | Art Deco | 12 | overlapping fans in offset rows |
| `deco-chevron-medallion.svg` | Art Deco | 12 | nested octagons with radiating spokes |
| `seigaiha-waves.svg` | Japanese | 30 | blue-sea half-circle waves (open arcs, drape-carried) |
| `kamon-kikyo.svg` | Japanese kamon | 2 | five-petal bellflower crest |
| `kamon-tomoe.svg` | Japanese kamon | 2 | mitsudomoe swirling commas |
| `asanoha-field.svg` | Japanese | 22 | hemp-leaf star tessellation |
| `persian-eight-star.svg` | Persian | 2 | two woven squares, octagon, rosette |
| `persian-boteh.svg` | Persian | **1** | four botehs around a hub |
| `islamic-twelve-star.svg` | Islamic | 14 | three woven squares with tucked rings |
| `girih-hex.svg` | Islamic girih | **1** | hexagonal tessellation with rosette |
| `norse-valknut.svg` | Norse | 2 | three interlocked triangles in a ring |
| `norse-vegvisir.svg` | Norse | 33 | runic compass with ticked staves |
| `greek-key.svg` | Greek | 3 | meander border around a rosette |
| `flower-of-life.svg` | sacred geometry | 2 | seven overlapping circles |
| `metatron.svg` | sacred geometry | 3 | hexagon, hexagram, vertex rings |

Kiss-component counts above 1 are woven/lapped constructions (asanoha, vegvisir,
seigaiha): the planner joins them with CARRY moves in drape mode, so each still
prints as one continuous carried bead.

## Variations, set 4 — Aztec, Scandinavian, Ottoman, Byzantine, Chinese, Roman & atomic age

Generated by `generate_variations4.py`.

| Tile | Tradition | Design |
|---|---|---|
| `aztec-sun.svg` | Aztec | sun-stone with stepped rays |
| `aztec-stepped.svg` | Aztec | stepped-fret medallion |
| `rosemaling-heart.svg` | Scandinavian folk | rosemaling heart with C-scrolls |
| `nordic-star.svg` | Scandinavian folk | eight-point selburose |
| `kurbits-rosette.svg` | Swedish kurbits | kurbits rosette |
| `iznik-tulip.svg` | Ottoman Iznik | tulip spray |
| `iznik-saz.svg` | Ottoman Iznik | saz-leaf medallion |
| `byzantine-cross.svg` | Byzantine | cross-in-square |
| `byzantine-medallion.svg` | Byzantine | pearl roundel |
| `chinese-lattice.svg` | Chinese | window lattice |
| `chinese-shou.svg` | Chinese | longevity roundel |
| `roman-guilloche.svg` | Roman mosaic | guilloche braid |
| `roman-wave.svg` | Roman mosaic | running-wave scroll |
| `atomic-starburst.svg` | Mid-century | atomic starburst |
| `atomic-orbits.svg` | Mid-century | atomic-age orbits |
| `honeycomb.svg` | Sacred geometry | seven-cell honeycomb |
| `gothic-rose.svg` | Gothic | rose window |
| `moorish-lattice.svg` | Moorish | pointed-arch lattice |
| `lotus-wheel.svg` | Tibetan | eight-petal lotus wheel |
| `sun-wheel.svg` | Sacred geometry | spoked sun wheel with pearls |

## From Pete's collection

| Tile | Source | Strokes / travels | Notes |
|---|---|---|---|
| `heart-mandala.svg` | Pete's painted mandala panel (`docs/reference/IMG_3151.jpg`) | **1** / 1 | four-heart clover hub with eye-dot rings docked on the lobes, 20-lobe scallop band, 12 petals threading a concentric ring to the outer circle — 28 fuses, 84 laps. Prints as raised weave in drape or true over-under in calibrated (lap hops). |
| `rosette-155mm.svg`, `rings-grid-155mm.svg`, `petal-flower-155mm.svg` | Pete's hand-authored SVGs | — | distinct designs, not copies of the tracings; kept as-drawn (hairline strokes — cosmetic only, Clayline reads centerlines). `petal-flower-155mm` is a 160 mm document despite the name. |

## Backing tiles

| Tile | Source | Strokes / travels | Notes |
|---|---|---|---|
| `serpentine-back.svg` | Pete's marker sketch (`docs/reference/IMG_3043.jpg`) | **1** / 1 | ONE closed line: vertical and horizontal serpentines joined at two corners (per Pete) — zero open ends, zero travels, 25 laps; made as a stack-mode base page under other tiles |

## Design rules used throughout

The endless knot and kolam are built with the `billiard()` construction — a
single closed line bouncing at 45° inside a box (3:4 and 4:5 ratios); their
crossings are the woven-over look and count as **laps** in the Construction
stats — raised weave in drape mode. The `swirl()` transform rotates each point
in proportion to its radius, which is why gankyil commas and paisleys keep
their hub/ring kisses after bending.

Minimum arc radius ≥ 2× a 5 mm nozzle, deliberate 15–25 % bead overlaps at
every intended fuse (Clayline counts these as **fuse points** in the
Construction stats — never warnings), everything inside a 3 mm bed margin, and
no closed loop left floating (a disconnected loop is a separate piece after
firing). The open spirals are the one exception to single-stroke: they cost
one travel each and are placed within a bead-width of the body so they fuse
physically even though the planner honestly counts them as separate strokes.

One practical gotcha found while building these: the kiss detector operates on
the default fuse tolerance (1 mm), and a designed gap of *exactly* 1.00 mm sits
on the boundary — sometimes merging, sometimes not. Design fuses at ≤0.8 mm gap
or as real overlaps, never at exactly the tolerance.

## Refreshing the proof sheet

`proof-sheet.jpg` is a 6-column contact sheet of every PNG in this directory
(rendered clay-on-paper; Pete's hairline SVGs are restyled to coil weight for
preview only). After adding or changing designs, re-run the generators above,
re-render any hand-authored SVGs, and rebuild the sheet (see repo history for
the small PIL script).
