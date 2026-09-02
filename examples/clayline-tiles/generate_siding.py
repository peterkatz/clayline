#!/usr/bin/env python3
"""Coil tiles derived from Pete's roofing / siding / ornamental-woodwork photos
(../ SidingBasedReference). Same idealized-centerline language, primitives and
emit style as the gallery generators — this file loads them by path and reuses
circle/teardrop/spiral/rpoly/chain_ring/swirl/comma/billiard/rounded_loop.

Design space 200x200, emitted at 6x6 in / 152.4 mm; tangency-first so the
kiss-hop planner fuses each tile into as few strokes as physically possible.
Two families:
  * BACKINGS — full-field repeats meant to print UNDER other tiles (stack mode):
    fish-scale, pantile waves, Dijon diamonds, rope lattice, shield shingles.
  * ORNAMENTS — centerpieces from the carved woodwork and laser-cut screens.
"""
import importlib.util
import math
import os
import sys

GALLERY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "gallery")


def _load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(GALLERY, f"{name}.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


V2 = _load("generate_variations2")          # pulls in generate_variations as V
V = V2.V
circle, teardrop, spiral, rpoly, chain_ring = (
    V.circle, V.teardrop, V.spiral, V.rpoly, V.chain_ring)
comma, swirl, billiard, rounded_loop = (
    V2.comma, V2.swirl, V2.billiard, V2.rounded_loop)
C = 100.0

# ------------------------- backing helpers -------------------------


def path(pts):
    """Open centerline stroke."""
    return ("path", list(pts))


def sine_row(y, x0, x1, amp, wavelen, phase=0.0):
    span = x1 - x0
    steps = max(8, int(span / wavelen * 20))
    return [(x0 + span * i / steps,
             y + amp * math.sin(2 * math.pi * (x0 + span * i / steps - x0) / wavelen + phase))
            for i in range(steps + 1)]


def tri_row(y, x0, x1, amp, period, up_first=True):
    span = x1 - x0
    ncell = max(2, round(span / period))
    pts = []
    for i in range(2 * ncell + 1):
        x = x0 + span * i / (2 * ncell)
        up = (i % 2 == 0) == up_first
        pts.append((x, y + (-amp if up else amp)))
    return pts


def serpentine(rows, closed=True):
    """Snake a list of left-to-right rows into ONE stroke (reverse odd rows,
    concat). Closed adds the loop-closing segment; open leaves clean ends and
    avoids a diagonal cutting back across the field."""
    loop = []
    for k, row in enumerate(rows):
        loop += row if k % 2 == 0 else row[::-1]
    if closed:
        loop.append(loop[0])
        return ("poly", loop, True)
    return ("path", loop)


def vridge(cx, y0, y1, amp, waves, n=24):
    """Gentle vertical S-ridge — a barrel roof-tile centerline."""
    return [(cx + amp * math.sin(2 * math.pi * waves * i / n), y0 + (y1 - y0) * i / n)
            for i in range(n + 1)]


# ------------------------- backings -------------------------


def fish_scale_back():
    """Overlapping scallop scales — club-roof fish-scale + pattern-7516979 +
    the weathered scallop shingles. Offset rows of tangent circles read as the
    classic scale field; all fuse."""
    els = []
    r, step = 13.0, 22.0
    ys = [22 + step * j for j in range(8)]            # 8 rows 22..176
    for j, y in enumerate(ys):
        off = 0.0 if j % 2 == 0 else step / 2
        x = 22 + off
        while x <= 178.001:
            els.append(circle(x, y, r))
            x += step
    return els


def pantile_wave_back():
    """Smooth S-curve pantile ridges — the red / pink pantile roofs. Stacked
    in-phase sine ridges snaked into one closed line."""
    rows = [sine_row(25 + 25 * k, 14, 186, 8.0, 43.0) for k in range(7)]
    return [serpentine(rows, closed=False)]


def dijon_diamond_back():
    """Burgundy polychrome diamond roof (Dijon). Stacked triangle waves whose
    peaks meet the next row's troughs form a clean harlequin diamond net; one
    closed snaking line, crossings are drape-mode weave."""
    amp, period = 15.0, 30.0
    rows = []
    for k in range(6):                                # y = 20,50,...,170
        y = 20 + 30 * k
        rows.append(tri_row(y, 20, 180, amp, period, up_first=(k % 2 == 0)))
    return [serpentine(rows, closed=False)]


def rope_lattice_back():
    """Circle-in-diamond siding — the terracotta rope network (aadsfasdfadsf).
    A clean diamond net with a ring tucked into every cell so it reads as rope
    joints threaded through rings; the net is one stroke, rings fuse to it."""
    amp, period, x0, x1 = 18.0, 36.0, 20.0, 182.0
    ys = [24 + 36 * k for k in range(5)]              # 5 rows -> 4 cell bands
    rows = [tri_row(y, x0, x1, amp, period, up_first=(k % 2 == 0)) for k, y in enumerate(ys)]
    els = [serpentine(rows, closed=False)]
    span = x1 - x0
    ncell = max(2, round(span / period))
    for k in range(len(ys) - 1):                       # a ring threaded in each cell
        cy = ys[k] + amp
        for i in range(2, 2 * ncell, 2):               # even samples = cell centres
            cx = x0 + span * i / (2 * ncell)
            els.append(circle(cx, cy, 12.5))           # laps the net (drape carries between)
    return els


def shield_shingle_back():
    """Point-down shield shingles — the weathered pentagon/home-plate tiles
    (weathered-tile-pattern-stockcake). Offset rows of tangent pentagons."""
    els = []
    R, sx, sy = 22.0, 33.0, 27.0                       # overlap so shingles fuse
    ys = [28 + sy * j for j in range(6)]              # 6 rows
    for j, y in enumerate(ys):
        off = 0.0 if j % 2 == 0 else sx / 2
        x = 24 + off
        while x <= 176.001:
            els.append(rpoly(x, y, R, 5, 90, 6))      # vertex at bottom
            x += sx
    return els


# ------------------------- ornaments -------------------------


def asanoha_star():
    """Japanese hemp-leaf (asanoha) screen — imafdffges laser-cut lattice. Two
    nested hexagons and the six diameters through the centre make the six-fold
    star; every line shares the hub and vertices, so they fuse."""
    R = 86.0
    els = [rpoly(C, C, R, 6, 0, 4), rpoly(C, C, R * math.cos(math.radians(30)), 6, 30, 4)]
    for k in range(3):                                # long diagonals (vertex-vertex)
        th = math.radians(60 * k)
        els.append(path([(C + R * math.cos(th), C + R * math.sin(th)),
                         (C - R * math.cos(th), C - R * math.sin(th))]))
    rm = R * math.cos(math.radians(30))
    for k in range(3):                                # short diameters (edge midpoints)
        th = math.radians(30 + 60 * k)
        els.append(path([(C + rm * math.cos(th), C + rm * math.sin(th)),
                         (C - rm * math.cos(th), C - rm * math.sin(th))]))
    return els


def leaf_burst():
    """Radiating leaf/petal burst — imaasdsssges laser-cut screen. Dense rings
    of pointed leaves exploding from a hub, bound by an outer ring."""
    els = [circle(C, C, 9)]
    for k in range(12):
        els.append(teardrop(C, C, 30 * k, 8, 44, 6))          # inner ring crosses r40
    els.append(circle(C, C, 40))
    for k in range(12):
        els.append(teardrop(C, C, 30 * k + 15, 38, 82, 6))    # outer ring crosses r40 & r80
    els.append(circle(C, C, 80))
    for k in range(24):
        els.append(teardrop(C, C, 15 * k, 78, 94, 3))         # fringe crosses r80
    return els


def rose_relief():
    """Carved rose relief — the sandstone flower panel (yyyyy) and the copper
    ornament. Five broad petals with a spiral heart, a leaf-scroll corona, and
    corner scrolls."""
    els = [circle(C, C, 9), spiral(C, C, 3, 8, 1.4)]
    for k in range(5):
        els.append(teardrop(C, C, 72 * k, 10, 40, 17))        # broad petals
    els.append(circle(C, C, 41))
    for k in range(5):
        els.append(comma(36 + 72 * k, 42, 74, 11, 40))        # leaf-scroll corona
    for sx in (-1, 1):                                        # corner scroll accents
        for sy in (-1, 1):
            rot = math.atan2(sy, sx)
            els.append(spiral(C + sx * 66, C + sy * 66, 4, 12, 1.2, rot))
    return els


def acanthus_corner():
    """Carved acanthus corner scroll — the wood corbel / bracket / copper panel
    (imaffsdsdsdges, imghsdffdages, pngtree). A diagonal S-stem between two
    volutes with acanthus leaves branching off; volutes are open by design."""
    els = []
    a = (48, 152)                       # foot volute (lower-left)
    b = (152, 48)                       # crown volute (upper-right)
    els.append(spiral(a[0], a[1], 5, 24, 1.7, math.radians(200)))
    els.append(spiral(b[0], b[1], 5, 19, 1.4, math.radians(20)))
    stem = V.bez((66, 150), (92, 150), (108, 92), (150, 66))   # sweeping S-stem
    els.append(path([(66, 150)] + stem))
    leaves = [(0.20, 150, 44, 8), (0.44, 200, 40, 9),
              (0.66, 150, 42, 8), (0.86, 210, 34, 8)]
    for t, ang, blen, w in leaves:                    # acanthus leaves along the stem
        i = max(1, min(len(stem) - 1, int(t * len(stem))))
        px, py = stem[i]
        els.append(_place(comma(ang, 4, blen, w, 46), px, py))
    els.append(circle(a[0], a[1], 6))                 # volute eyes
    els.append(circle(b[0], b[1], 5))
    return els


def _place(el, cx, cy):
    """Translate a centered element so its origin sits at (cx,cy)."""
    pts = [(x - C + cx, y - C + cy) for x, y in V.el_pts(el)]
    return ("poly", pts + [pts[0]], True)


def eave_roundel():
    """Chinese temple eave — roof-temple-chinese-style. A top cloud-scroll
    frieze, a band of barrel-tile ridges, a row of circular end-cap roundels,
    and pendant drop tiles hanging between them."""
    els = []
    caps = [25 + 150 / 7 * k for k in range(8)]        # 8 eave end-caps, 25..175
    els.append(path(sine_row(30, 16, 184, 6.0, 21.0)))  # top cloud frieze band
    for cx in caps:                                    # barrel ridges: touch frieze + cap
        els.append(path(vridge(cx, 28, 151, 3.0, 1.0)))
    for cx in caps:                                    # roundel end caps (overlap -> chain)
        els.append(circle(cx, 151, 11.2))
    for k in range(7):                                 # pendant drops touch the caps above
        cx = (caps[k] + caps[k + 1]) / 2
        els.append(teardrop(cx, 152, 180, 6, 26, 8))
    return els


# ------------- Victorian / gold-leaf / fleur-de-lis -------------


def _mirror_x(pts):
    return [(2 * C - x, y) for x, y in pts]


def xform(el, cx, cy, s=1.0, ang_deg=0.0):
    """Scale about C, rotate, translate a single element to (cx,cy)."""
    th = math.radians(ang_deg)
    ca, sa = math.cos(th), math.sin(th)
    out = []
    for x, y in V.el_pts(el):
        dx, dy = (x - C) * s, (y - C) * s
        out.append((cx + dx * ca - dy * sa, cy + dx * sa + dy * ca))
    closed = el[0] == "circle" or (el[0] == "poly" and el[2])
    return ("poly", out, True) if closed else ("path", out)


def fleur(cx=C, cy=C, s=1.0, ang=0.0):
    """A fleur-de-lis pointing up, centred at C: central lancet lobe, two
    out-curling side lobes, a binding band and a flared foot — every part
    touches the band, so it fuses. Transformed to (cx,cy,s,ang) if given."""
    tip = (C, C - 80)
    rside = V.bez(tip, (C + 19, C - 56), (C + 23, C - 20), (C + 5, C - 6))
    lobe = [tip] + rside + [(C, C - 2)] + _mirror_x(list(reversed(rside))) + [tip]
    rl = [(C + 3, C - 8)]
    rl += V.bez((C + 3, C - 8), (C + 27, C - 6), (C + 47, C - 27), (C + 41, C - 55))
    rl += V.bez((C + 41, C - 55), (C + 31, C - 41), (C + 16, C - 24), (C + 6, C - 14))
    rl.append((C + 3, C - 8))
    els = [
        ("poly", lobe, True),                              # central lobe, pointed
        ("poly", rl, True),                                # right side lobe, curling up-out
        ("poly", _mirror_x(rl), True),                     # left side lobe
        rounded_loop([(C - 29, C - 9), (C + 29, C - 9), (C + 29, C + 1), (C - 29, C + 1)], 3),
        teardrop(C, C - 8, 90, 6, 34, 10),                 # flared foot drop (tip up into band)
    ]
    if (cx, cy, s, ang) != (C, C, 1.0, 0.0):
        els = [xform(e, cx, cy, s, ang) for e in els]
    return els


def fleur_de_lis():
    """The single fleur-de-lis emblem — French lily, Victorian heraldry."""
    return fleur()


def fleur_diaper():
    """Fleur-de-lis diaper — the repeating heraldic wallpaper/tile field. Small
    fleurs alternating up/down on a light diamond trellis that links them."""
    amp, period, x0, x1 = 20.0, 42.0, 14.0, 186.0
    ys = [22 + 39 * k for k in range(5)]
    rows = [tri_row(y, x0, x1, amp, period, up_first=(k % 2 == 0)) for k, y in enumerate(ys)]
    els = [serpentine(rows, closed=False)]
    for j in range(4):
        for i in range(4):
            cx = 35 + 43 * i
            cy = 41 + 39 * j
            els += fleur(cx, cy, s=0.42, ang=0.0 if j % 2 == 0 else 180.0)
    return els


def anthemion():
    """Greek/Victorian anthemion (honeysuckle palmette): a fan of petals from a
    base cluster, flanked by two volutes."""
    base = (C, C + 52)
    els = [circle(base[0], base[1], 8)]
    for ang_off, length in [(-72, 40), (-46, 54), (-22, 64), (0, 70),
                            (22, 64), (46, 54), (72, 40)]:
        els.append(teardrop(base[0], base[1], -90 + ang_off, 5, length, 7))
    els.append(spiral(C - 34, C + 52, 4, 13, 1.3, math.radians(150)))
    els.append(spiral(C + 34, C + 52, 4, 13, 1.3, math.radians(30)))
    return els


def gilt_scroll_crest():
    """Symmetric gold-leaf crest: a central palmette shell over two acanthus
    volutes sweeping out and down — a gilded frame crest."""
    els = [circle(C, C - 30, 8)]
    for ang_off, length in [(-32, 30), (-16, 40), (0, 46), (16, 40), (32, 30)]:
        els.append(teardrop(C, C - 30, -90 + ang_off, 6, length, 7))  # top palmette fan
    els.append(comma(38, 8, 70, 16, 66))                   # right acanthus scroll from centre
    els.append(comma(142, 8, 70, 16, -66))                 # left acanthus scroll (mirror)
    els.append(teardrop(C, C - 30, 90, 6, 34, 8))          # short pendant tying the scrolls
    return els


def guilloche_band():
    """Victorian guilloche — two braided running strands with dots in the eyes,
    stacked into a molding-border field."""
    x0, x1 = 12.0, 188.0
    ys = [26 + 37 * k for k in range(5)]
    a = serpentine([sine_row(y, x0, x1, 12, 44, phase=0.0) for y in ys], closed=False)
    b = serpentine([sine_row(y, x0, x1, 12, 44, phase=math.pi) for y in ys], closed=False)
    els = [a, b]
    ncell = max(2, round((x1 - x0) / 44))
    for y in ys:                                            # dots in the braid eyes
        for m in range(ncell):
            els.append(circle(x0 + (x1 - x0) * (m + 0.5) / ncell, y, 3.5))
    return els


def gothic_quatrefoil():
    """Gothic Revival quatrefoil — Minton encaustic tile: four lobes in a square
    frame with corner cusps and a central boss."""
    els = [rpoly(C, C, 95, 4, 45, 14)]                      # square frame
    for k in range(4):
        th = math.radians(90 * k)
        els.append(circle(C + 34 * math.cos(th), C + 34 * math.sin(th), 30))
    els.append(circle(C, C, 12))                            # central boss
    for k in range(4):                                      # corner cusps touch frame + lobes
        th = math.radians(45 + 90 * k)
        els.append(circle(C + 62 * math.cos(th), C + 62 * math.sin(th), 12))
    return els


def trefoil_tracery():
    """Gothic trefoil window tracery: three lobes in a ring with cusps."""
    els = []
    for k in range(3):
        th = math.radians(-90 + 120 * k)
        els.append(circle(C + 42 * math.cos(th), C + 42 * math.sin(th), 36))
    els.append(circle(C, C, 76))                            # outer ring crosses the lobes
    els.append(circle(C, C, 11))                            # central node
    for k in range(3):                                      # cusps between lobes
        th = math.radians(30 + 120 * k)
        els.append(circle(C + 54 * math.cos(th), C + 54 * math.sin(th), 10))
    return els


def victorian_cartouche():
    """Rococo cartouche: an oval frame with a top palmette crest, a bottom
    pendant, and four C-scroll volutes — all touching the oval."""
    oval = V.bez((C, C - 58), (C + 42, C - 58), (C + 42, C + 58), (C, C + 58))
    oval += V.bez((C, C + 58), (C - 42, C + 58), (C - 42, C - 58), (C, C - 58))
    els = [("poly", oval, True), circle(C, C, 9)]
    for k in range(6):                                      # central rosette crosses the oval
        els.append(teardrop(C, C, 60 * k, 10, 35, 8))
    for ang_off, length in [(-26, 18), (0, 24), (26, 18)]:  # top crest
        els.append(teardrop(C, C - 58, -90 + ang_off, 4, length, 6))
    els.append(teardrop(C, C + 52, 90, 6, 30, 8))           # bottom pendant touches the oval
    for sx in (-1, 1):                                      # shoulder + hip C-scrolls
        els.append(spiral(C + sx * 31, C - 38, 3, 12, 1.2, math.radians(0 if sx > 0 else 180)))
        els.append(spiral(C + sx * 31, C + 38, 3, 12, 1.2, math.radians(0 if sx > 0 else 180)))
    return els


def damask_ogee():
    """Damask ogee: an onion-arch frame enclosing a fleur — the repeating
    wallpaper motif."""
    top, bot = (C, C - 90), (C, C + 90)
    right = V.bez(top, (C + 48, C - 66), (C + 40, C - 8), (C + 36, C))
    right += V.bez((C + 36, C), (C + 32, C + 8), (C + 44, C + 66), bot)
    ogee = [top] + right + [bot] + _mirror_x(list(reversed(right))) + [top]
    els = [("poly", ogee, True)]
    els += fleur(C, C + 8, s=0.92, ang=0.0)                 # fleur fills & touches the ogee
    return els


def ceiling_rose():
    """Victorian ceiling rose: concentric petal, acanthus and fringe rings."""
    els = [circle(C, C, 10), spiral(C, C, 3, 9, 1.3)]
    for k in range(8):
        els.append(teardrop(C, C, 45 * k, 11, 40, 11))      # inner petals cross r41
    els.append(circle(C, C, 41))
    for k in range(16):
        els.append(comma(11.25 + 22.5 * k, 42, 72, 8, 30))  # acanthus swirl ring
    els.append(circle(C, C, 73))
    for k in range(24):
        els.append(teardrop(C, C, 15 * k, 74, 92, 5))       # outer fringe crosses r73
    els.append(circle(C, C, 90))
    return els


TILES = [
    ("fish-scale-back", fish_scale_back, "overlapping scallop scales — club-roof / weathered fish-scale"),
    ("pantile-wave-back", pantile_wave_back, "S-curve pantile ridges — red/pink pantile roofs"),
    ("dijon-diamond-back", dijon_diamond_back, "harlequin diamond net — Dijon polychrome roof"),
    ("rope-lattice-back", rope_lattice_back, "interlaced rope network with node rings — terracotta siding"),
    ("shield-shingle-back", shield_shingle_back, "point-down shield shingles — weathered pentagon tiles"),
    ("asanoha-star", asanoha_star, "hemp-leaf six-fold star screen — laser-cut lattice"),
    ("leaf-burst", leaf_burst, "radiating leaf burst — laser-cut petal screen"),
    ("rose-relief", rose_relief, "carved rose with leaf-scroll corona — sandstone/copper panel"),
    ("acanthus-corner", acanthus_corner, "acanthus corner volute scroll — carved corbel/bracket"),
    ("eave-roundel", eave_roundel, "temple eave end-caps with pendant drops — Chinese roof"),
    ("fleur-de-lis", fleur_de_lis, "the fleur-de-lis emblem — French lily / Victorian heraldry"),
    ("fleur-diaper", fleur_diaper, "repeating fleur-de-lis diaper on a diamond trellis"),
    ("anthemion", anthemion, "honeysuckle palmette fan with volutes — Greek/Victorian"),
    ("gilt-scroll-crest", gilt_scroll_crest, "symmetric gold-leaf acanthus crest"),
    ("guilloche-band", guilloche_band, "braided running-circle guilloche — Victorian molding"),
    ("gothic-quatrefoil", gothic_quatrefoil, "Gothic Revival quatrefoil — Minton encaustic tile"),
    ("trefoil-tracery", trefoil_tracery, "Gothic trefoil window tracery"),
    ("victorian-cartouche", victorian_cartouche, "rococo cartouche oval with scroll flourishes"),
    ("damask-ogee", damask_ogee, "damask ogee arch enclosing a fleur-de-lis"),
    ("ceiling-rose", ceiling_rose, "Victorian ceiling-rose rosette, concentric rings"),
]


if __name__ == "__main__":
    from PIL import Image, ImageDraw
    outdir = sys.argv[1] if len(sys.argv) > 1 else "."
    thumbs = []
    for name, fn, desc in TILES:
        els = [e for e in fn() if e]
        V.to_svg(els, os.path.join(outdir, f"{name}.svg"), f"clayline tile: {name} — {desc}")
        im, lo, hi = V.render(els, os.path.join(outdir, f"{name}.png"))
        flag = "" if lo is not None and lo >= 2.0 and hi <= 198.0 else f"  ** BOUNDS {lo:.1f}..{hi:.1f}"
        print(f"{name:22s} {len(els):3d} elements{flag}")
        thumbs.append((name, im))
    tw, cols = 360, 5
    rows = (len(thumbs) + cols - 1) // cols
    sheet = Image.new("RGB", (tw * cols + 24, (tw + 26) * rows + 8), "white")
    dr = ImageDraw.Draw(sheet)
    for i, (name, im) in enumerate(thumbs):
        x, y = (i % cols) * (tw + 4) + 4, (i // cols) * (tw + 26) + 4
        sheet.paste(im.resize((tw, tw)), (x, y))
        dr.text((x + 4, y + tw + 4), name, fill="black")
    sheet.save(os.path.join(outdir, "contact-sheet.jpg"), quality=88)
    print("contact sheet written")
