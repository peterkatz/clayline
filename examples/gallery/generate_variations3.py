#!/usr/bin/env python3
"""Twenty more coil-tile variations — set 3: Celtic, Art Deco, Japanese
(kamon / seigaiha), Persian, Norse, Islamic-star and other geometric
traditions, in the same idealized-centerline language as sets 1 and 2.

Same rules: design space 200x200 emitted at 6x6 in, tangency-first (closed
loops kiss or overlap so the kiss-hop planner fuses them), spirals/open lines
are deliberate, crossings are drape-mode weave features. Everything here is
compass-and-ruler geometry — circles, tangencies, radial symmetry — which is
what a single thick clay coil renders best.
"""
import math, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generate_variations as V
import generate_variations2 as V2

MM, C = V.MM, 100.0
circle, teardrop, spiral, rpoly, chain_ring = (
    V.circle, V.teardrop, V.spiral, V.rpoly, V.chain_ring)
comma, swirl, billiard, rounded_loop, fit_ring, heart = (
    V2.comma, V2.swirl, V2.billiard, V2.rounded_loop, V2.fit_ring, V2.heart)


def poly(pts, closed=True):
    return ('poly', list(pts) + ([pts[0]] if closed else []), closed)


def arc_pts(cx, cy, r, a0, a1, n=32):
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def line(p, q):
    return ('poly', [p, q], False)


def ellipse(cx, cy, rx, ry, rot_deg=0.0, n=96):
    th = math.radians(rot_deg)
    pts = []
    for i in range(n + 1):
        a = 2 * math.pi * i / n
        x, y = rx * math.cos(a), ry * math.sin(a)
        pts.append((cx + x * math.cos(th) - y * math.sin(th),
                    cy + x * math.sin(th) + y * math.cos(th)))
    return ('poly', pts, True)


def petal(cx, cy, angle_deg, a, b, w):
    """A lens/vesica petal (symmetric pointed both ends) from radius a to b."""
    L = b - a
    th = math.radians(angle_deg)
    pts = []
    for i in range(41):
        t = i / 40
        s = a + L * t
        off = w * math.sin(math.pi * t)
        pts.append((s, off))
    for i in range(41):
        t = 1 - i / 40
        s = a + L * t
        off = -w * math.sin(math.pi * t)
        pts.append((s, off))
    out = [(cx + s * math.cos(th) - o * math.sin(th),
            cy + s * math.sin(th) + o * math.cos(th)) for s, o in pts]
    return ('poly', out + [out[0]], True)


# ---------------- the twenty tiles ----------------

def celtic_triquetra():
    """Celtic triquetra: three vesica lobes woven through a ring."""
    els = [circle(C, C, 60)]
    R = 40
    for k in range(3):
        th = math.radians(-90 + 120 * k)
        els.append(circle(C + R * math.cos(th), C + R * math.sin(th), 46))
    els.append(circle(C, C, 12))
    return els


def celtic_shield_knot():
    """Celtic shield knot: four interlaced loops in a square, corner rings."""
    els = [rpoly(C, C, 84, 4, 45, 22), rpoly(C, C, 84, 4, 0, 22)]
    for k in range(4):
        th = math.radians(45 + 90 * k)
        els.append(circle(C + 58 * math.cos(th), C + 58 * math.sin(th), 22))
    els.append(circle(C, C, 16))
    return els


def celtic_spiral_triskele():
    """Triskele: three spirals wound from a hub, bound by a ring."""
    els = [circle(C, C, 82), circle(C, C, 12)]
    for k in range(3):
        th = 2 * math.pi * k / 3
        els.append(spiral(C + 40 * math.cos(th), C + 40 * math.sin(th),
                          6, 36, 1.35, th + math.pi))
    return els


def celtic_cross():
    """Celtic ringed cross: bold cross bars through a nimbus ring."""
    els = [circle(C, C, 52), circle(C, C, 34), circle(C, C, 10)]
    for k in range(4):
        th = 90 * k
        els.append(teardrop(C, C, th, 12, 92, 12))
    return els


def deco_sunburst():
    """Art Deco sunburst: alternating long/short rays over a stepped half-ring."""
    els = [circle(C, C + 26, 16), circle(C, C + 26, 34)]
    for k in range(9):
        ang = -180 + 22.5 * k
        long = k % 2 == 0
        els.append(teardrop(C, C + 26, ang, 35, 96 if long else 70, 8 if long else 6))
    els.append(rounded_loop([(18, 128), (182, 128), (182, 142), (18, 142)], 5))
    return els


def deco_fan_scallop():
    """Art Deco fan-scallop field: overlapping fans in offset rows."""
    els = []
    step = 50
    for j in range(4):
        y = 52 + 38 * j
        off = 0 if j % 2 == 0 else step / 2
        x = 32 + off
        while x <= 170:
            els.append(('poly', arc_pts(x, y, 24, 180, 360, 24) + [(x + 24, y)], True))
            els.append(('poly', arc_pts(x, y, 12, 180, 360, 14) + [(x + 12, y)], True))
            x += step
    return els


def deco_chevron_medallion():
    """Deco stepped-chevron medallion: nested octagons with radiating spokes."""
    els = [rpoly(C, C, 84, 8, 22.5, 6), rpoly(C, C, 60, 8, 22.5, 5),
           rpoly(C, C, 36, 8, 22.5, 4), circle(C, C, 12)]
    for k in range(8):
        th = math.radians(22.5 + 45 * k)
        els.append(line((C + 12 * math.cos(th), C + 12 * math.sin(th)),
                        (C + 84 * math.cos(th), C + 84 * math.sin(th))))
    return els


def seigaiha_waves():
    """Japanese seigaiha: overlapping concentric half-circle 'blue-sea' waves."""
    els = []
    step = 52
    for j in range(5):
        y = 44 + 32 * j
        off = 0 if j % 2 == 0 else step / 2
        x = 32 + off
        while x <= 172:
            for r in (24, 12):
                els.append(('poly', arc_pts(x, y, r, 180, 360, 20), False))
            x += step
    return els


def kamon_kikyo():
    """Japanese kamon: five-petal bellflower crest in a ring."""
    els = [circle(C, C, 82), circle(C, C, 10)]
    for k in range(5):
        els.append(petal(C, C, -90 + 72 * k, 11, 78, 20))
    for k in range(5):
        th = math.radians(-90 + 72 * k + 36)
        els.append(circle(C + 44 * math.cos(th), C + 44 * math.sin(th), 7))
    return els


def kamon_tomoe():
    """Japanese mitsudomoe: three swirling commas in a ring."""
    els = [circle(C, C, 82), circle(C, C, 12)]
    for k in range(3):
        els.append(comma(120 * k, 12.7, 80, 22, 70))
    return els


def asanoha_field():
    """Asanoha hemp-leaf field: a tessellation of six-pointed stars."""
    els = []
    R = 34
    for cx, cy in [(C, C), (C + 2 * R * 0.866, C), (C - 2 * R * 0.866, C),
                   (C + R * 0.866, C - 1.5 * R), (C - R * 0.866, C - 1.5 * R),
                   (C + R * 0.866, C + 1.5 * R), (C - R * 0.866, C + 1.5 * R)]:
        els.append(rpoly(cx, cy, R, 6, 0, 3))
        for k in range(3):
            th = math.radians(60 * k)
            els.append(line((cx + R * math.cos(th), cy + R * math.sin(th)),
                            (cx - R * math.cos(th), cy - R * math.sin(th))))
    return els


def persian_eight_star():
    """Persian eight-point star: two woven squares, an octagon, and a rosette."""
    els = [rpoly(C, C, 84, 4, 0, 6), rpoly(C, C, 84, 4, 45, 6),
           rpoly(C, C, 50, 8, 22.5, 6), circle(C, C, 14)]
    for k in range(8):
        els.append(teardrop(C, C, 45 * k, 15, 48, 9))
    return els


def persian_boteh_field():
    """Persian boteh (paisley) field: four large botehs nested around a hub."""
    els = [circle(C, C, 16)]
    for k in range(4):
        els.append(comma(45 + 90 * k, 16.7, 84, 22, 40))
    return els


def islamic_twelve_star():
    """Twelve-point Islamic star: three woven squares, hub, tucked rings."""
    els = [rpoly(C, C, 84, 4, 0, 6), rpoly(C, C, 84, 4, 30, 6), rpoly(C, C, 84, 4, 60, 6),
           circle(C, C, 22)]
    for k in range(12):
        th = math.radians(15 + 30 * k)
        els.append(circle(C + 44 * math.cos(th), C + 44 * math.sin(th), 8))
    return els


def islamic_girih_hex():
    """Girih hexagonal tessellation with a central rosette."""
    els = [rpoly(C, C, 30, 6, 30, 4)]
    R = 30
    for k in range(6):
        th = math.radians(60 * k)
        els.append(rpoly(C + 2 * R * math.cos(math.radians(30)) * math.cos(th),
                         C + 2 * R * math.cos(math.radians(30)) * math.sin(th), R, 6, 30, 4))
    for k in range(6):
        els.append(teardrop(C, C, 30 + 60 * k, 8, 28, 7))
    els.append(circle(C, C, 8))
    return els


def norse_valknut():
    """Norse valknut: three interlocked rounded triangles."""
    els = []
    for k in range(3):
        th = math.radians(-90 + 120 * k)
        els.append(rpoly(C + 30 * math.cos(th), C + 30 * math.sin(th), 62, 3, -90, 10))
    els.append(circle(C, C, 92))
    return els


def norse_vegvisir():
    """Runic compass: eight staves from a hub with tick marks, in a ring."""
    els = [circle(C, C, 84), circle(C, C, 12)]
    for k in range(8):
        th = math.radians(45 * k)
        ux, uy = math.cos(th), math.sin(th)
        els.append(line((C + 12 * ux, C + 12 * uy), (C + 82 * ux, C + 82 * uy)))
        for r in (38, 60):
            px, py = C + r * ux, C + r * uy
            els.append(line((px - 9 * uy, py + 9 * ux), (px + 9 * uy, py - 9 * ux)))
        els.append(circle(C + 74 * ux, C + 74 * uy, 6))
    return els


def greek_key_border():
    """Greek key meander border around a central rosette."""
    els = [rpoly(C, C, 96, 4, 45, 6), rpoly(C, C, 76, 4, 45, 6), circle(C, C, 40)]
    for k in range(8):
        els.append(teardrop(C, C, 45 * k, 12, 40, 9))
    els.append(circle(C, C, 11))
    return els


def sacred_flower_of_life():
    """Flower of life: seven overlapping circles inside a bounding ring."""
    R = 30
    els = [circle(C, C, 3 * R), circle(C, C, R)]
    for k in range(6):
        th = math.radians(60 * k)
        els.append(circle(C + R * math.cos(th), C + R * math.sin(th), R))
    for k in range(6):
        th = math.radians(30 + 60 * k)
        els.append(circle(C + R * 1.732 * math.cos(th), C + R * 1.732 * math.sin(th), R))
    return els


def sacred_metatron():
    """Metatron-style: hexagon, inner hexagram, and vertex rings."""
    els = [rpoly(C, C, 82, 6, 0, 3), rpoly(C, C, 48, 3, 90, 3), rpoly(C, C, 48, 3, -90, 3),
           circle(C, C, 12)]
    for k in range(6):
        th = math.radians(60 * k)
        els.append(circle(C + 82 * math.cos(th), C + 82 * math.sin(th), 12))
    return els


TILES3 = [
    ('celtic-triquetra', celtic_triquetra, 'Celtic triquetra — three woven vesica lobes'),
    ('celtic-shield-knot', celtic_shield_knot, 'Celtic shield knot — four interlaced loops'),
    ('celtic-triskele', celtic_spiral_triskele, 'triskele — three spirals from a hub'),
    ('celtic-cross', celtic_cross, 'Celtic ringed cross'),
    ('deco-sunburst', deco_sunburst, 'Art Deco sunburst over stepped bands'),
    ('deco-fan-scallop', deco_fan_scallop, 'Art Deco fan-scallop field'),
    ('deco-chevron-medallion', deco_chevron_medallion, 'Deco nested-octagon medallion'),
    ('seigaiha-waves', seigaiha_waves, 'Japanese seigaiha blue-sea waves'),
    ('kamon-kikyo', kamon_kikyo, 'Japanese kikyo bellflower crest'),
    ('kamon-tomoe', kamon_tomoe, 'Japanese mitsudomoe crest'),
    ('asanoha-field', asanoha_field, 'asanoha hemp-leaf star field'),
    ('persian-eight-star', persian_eight_star, 'Persian eight-point star'),
    ('persian-boteh', persian_boteh_field, 'Persian boteh paisleys around a hub'),
    ('islamic-twelve-star', islamic_twelve_star, 'twelve-point Islamic star'),
    ('girih-hex', islamic_girih_hex, 'girih hexagonal tessellation'),
    ('norse-valknut', norse_valknut, 'Norse valknut — three interlocked triangles'),
    ('norse-vegvisir', norse_vegvisir, 'runic compass with eight staves'),
    ('greek-key', greek_key_border, 'Greek meander border with rosette'),
    ('flower-of-life', sacred_flower_of_life, 'flower of life — seven circles'),
    ('metatron', sacred_metatron, 'hexagon, hexagram and vertex rings'),
]


if __name__ == '__main__':
    from PIL import Image, ImageDraw
    outdir = sys.argv[1] if len(sys.argv) > 1 else '.'
    thumbs = []
    for name, fn, desc in TILES3:
        els = [e for e in fn() if e]
        V.to_svg(els, os.path.join(outdir, f'{name}.svg'), f'clayline tile: {name} — {desc}')
        im, lo, hi = V.render(els, os.path.join(outdir, f'{name}.png'))
        flag = '' if 2.0 <= lo and hi <= 198.0 else f'  ** BOUNDS {lo:.1f}..{hi:.1f}'
        print(f'{name:24s} {len(els):3d} elements{flag}')
        thumbs.append((name, im))
    tw, cols = 360, 5
    rows = (len(thumbs) + cols - 1) // cols
    sheet = Image.new('RGB', (tw * cols + 24, (tw + 26) * rows + 8), 'white')
    dr = ImageDraw.Draw(sheet)
    for i, (name, im) in enumerate(thumbs):
        x, y = (i % cols) * (tw + 4) + 4, (i // cols) * (tw + 26) + 4
        sheet.paste(im.resize((tw, tw)), (x, y))
        dr.text((x + 4, y + tw + 4), name, fill='black')
    sheet.save(os.path.join(outdir, 'contact-sheet-3.jpg'), quality=88)
    print('contact sheet written')
