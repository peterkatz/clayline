# Clayline zoo — animal coil tiles

Ten zoo-animal tiles for Clayline, in the same idealized-centerline language as
the gallery/siding sets. All **6 × 6 in (152.4 × 152.4 mm)**, mm units, stroked
centerlines, tangency-first. Parametric source: `generate_zoo.py` (it loads the
gallery primitives — circle, teardrop, spiral, rpoly, chain_ring, comma,
rounded_loop, bez — from `../gallery`,
so emit scale, bead width and clay colour match the other sets). It adds a
`smooth()` Catmull-Rom helper for the silhouettes. Edit the generator, not the
SVGs. `proof-sheet.jpg` shows all ten.

```sh
cd examples/clayline-zoo-tiles
python3 generate_zoo.py .
```

Unlike the geometric sets these are figurative, so each leans on the medium's
strengths a different way — radial **face medallions**, **symmetric** builds, a
**coiled** body, and a few **silhouettes** — and a few open strokes (legs,
tusks, antennae, tongue) are deliberate.

| Tile | Construction | Components / travels | Notes |
|---|---|---|---|
| `lion` | face medallion | 1 / 1 | mane of rays around a face; brow ties the eyes to the muzzle and ring |
| `elephant` | head-on, symmetric | 1 / 1 | domed head, big flapping ears, curling trunk, tusks |
| `giraffe` | side silhouette | 3 / 1 | long neck, ossicone knobs, a chain of spot-patches down the neck |
| `owl` | face medallion | 5 / 1 | two great eyes meeting at centre, beak, ear tufts, wings, belly feathers |
| `peacock` | radial fan | 1 / 1 | upward fan of eye-spotted tail feathers over a small body |
| `butterfly` | symmetric | 5 / 1 | four wings with spots, body, antennae |
| `turtle` | patterned shell | 3 / 1 | tessellated scutes in the shell; head, four legs and tail poke out |
| `snake` | coil | 2 / 1 | a spiral body with a head and forked tongue |
| `penguin` | front silhouette | 3 / 1 | body, belly patch, flippers, feet, beak |
| `flamingo` | side silhouette | 2 / 1 | S-neck, hooked beak, body on long legs |

## Reading the counts

`Components / travels`: each tile is planner-verified `--kiss --layers 1` and
prints as **one continuous carried bead in drape mode** (a single real travel —
the gaps between components become CARRY moves that extrude a clay bridge). A
handful of tiles carry more than one component: those are the small internal
features (a few sub-3 mm eye dots, butterfly/giraffe spots) that connect via
short drape carry-bridges rather than a designed contact. Every structural part
was wired to touch (checked with a segment-intersection connectivity test); the
only remaining "floaters" are those tiny eye dots, which bridge invisibly. In
*calibrated* mode the components become lap-hop travels, same as the gallery's
multi-part tiles.

Design rules match the other sets: minimum arc radius ≥ 2× a 5 mm nozzle,
deliberate bead overlaps at fuse points, everything inside a ~3 mm margin.
