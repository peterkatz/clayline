# Clayline tiles — roofing, siding, woodwork & Victorian ornament

Twenty coil tiles drawn from Pete's reference photos one directory up (`../`), in
the same idealized-centerline language as the gallery tiles. All are **6 × 6 in
(152.4 × 152.4 mm)**, mm units, stroked centerlines, designed tangency-first so
the kiss-hop planner fuses each into as few strokes as possible. Parametric
source: `generate_siding.py` (it loads the gallery's primitives — circle,
teardrop, spiral, rpoly, chain_ring, swirl, comma, billiard, rounded_loop, bez —
from `../gallery`, so the emit scale,
bead width and clay colour match exactly). Edit the generator, not the SVGs.
`proof-sheet.jpg` shows all twenty; `contact-sheet.jpg` is the raw dump.

```sh
cd examples/clayline-tiles
python3 generate_siding.py .
```

## How to read the counts

The tables list **kiss-components / real drape travels**. Every tile was
planner-verified `--kiss --layers 1` and prints as **one continuous carried
bead in drape mode** (a single real travel — the inter-component gaps become
CARRY moves that extrude a clay bridge, so nothing fires as a loose piece; each
tile was checked for genuinely floating loops and has none). A tile with more
than one kiss-component simply weaves through more crossings; in *calibrated*
mode those become lap-hop travels, exactly like the gallery's multi-part tiles.

## Roofing & siding backings — print under other tiles (stack mode)

| Tile | Reference photo(s) | Components / travels | Notes |
|---|---|---|---|
| `fish-scale-back` | club-roof fish-scale, `pattern-7516979`, weathered scallop | **1** / 1 | offset rows of overlapping scale circles |
| `pantile-wave-back` | red & pink S-curve pantile roofs | **1** / 1 | one snaking line of horizontal ridges |
| `dijon-diamond-back` | Dijon polychrome diamond roof | **1** / 1 | one snaking line; crossings are the harlequin diamonds |
| `rope-lattice-back` | terracotta circle-in-diamond siding (`aadsfasdfadsf`) | 13 / **1** | diamond net with a ring threaded in each cell |
| `shield-shingle-back` | weathered pentagon/home-plate shingles | **1** / 1 | overlapping point-down shields fuse into one sheet |

## Ornamental centerpieces — carved woodwork & laser-cut screens

| Tile | Reference photo(s) | Components / travels | Notes |
|---|---|---|---|
| `asanoha-star` | hemp-leaf laser-cut lattice (`imafdffges`) | 7 / **1** | nested hexagons + six diameters make the six-fold star |
| `leaf-burst` | laser-cut petal screen (`imaasdsssges`) | **1** / 1 | three staggered rings of pointed leaves, two binding circles |
| `rose-relief` | sandstone flower (`yyyyy`) + copper panel | 6 / **1** | five petals, spiral heart, leaf-scroll corona, corner scrolls |
| `acanthus-corner` | carved corbel/bracket + copper panel | 7 / **1** | diagonal S-stem between two volutes with acanthus leaves |
| `eave-roundel` | Chinese temple eave | 10 / **1** | cloud frieze, barrel ridges, roundel end-caps, pendant drops |

## Victorian, gold-leaf & fleur-de-lis

| Tile | Influence | Components / travels | Notes |
|---|---|---|---|
| `fleur-de-lis` | French lily / Victorian heraldry | **1** / 1 | pointed central lobe, curling side lobes, band, foot drop |
| `fleur-diaper` | heraldic wallpaper/tile field | **1** / 1 | fleurs alternating up/down on a linking diamond trellis |
| `damask-ogee` | Victorian damask wallpaper | **1** / 1 | onion-arch ogee frame enclosing a fleur-de-lis |
| `anthemion` | Greek/Victorian palmette | **1** / 1 | honeysuckle fan springing from a base with two volutes |
| `gilt-scroll-crest` | gold-leaf frame crest | 2 / **1** | palmette shell over a symmetric interlaced acanthus scroll |
| `guilloche-band` | Victorian molding border | **1** / 1 | two braided running strands with dots in the eyes |
| `gothic-quatrefoil` | Minton encaustic tile | 6 / **1** | four lobes in a square frame with corner bosses |
| `trefoil-tracery` | Gothic window tracery | 4 / **1** | three lobes in a ring with cusps |
| `victorian-cartouche` | rococo cartouche | 6 / **1** | oval medallion: rosette, top crest, C-scrolls, pendant |
| `ceiling-rose` | Victorian ceiling medallion | **1** / 1 | concentric petal, acanthus and fringe rings |

## Design rules used throughout

Same as the gallery set: minimum arc radius ≥ 2× a 5 mm nozzle, deliberate bead
overlaps at every intended fuse (Clayline counts these as **fuse points**, never
warnings), everything inside a ~3 mm bed margin, and no closed loop left
floating — every tile was checked for that with a segment-intersection
connectivity test, not just by eye. Crossings that read as woven-over texture
count as **laps** (raised weave in drape, true over-under in calibrated with lap
hops). Backings are one continuous stroke wherever possible, because a base page
wants as few thread starts as it can get. The `fleur-diaper`, `dijon`, `rope`
and `guilloche` fields can be scaled or tiled at ingest without redrawing.
