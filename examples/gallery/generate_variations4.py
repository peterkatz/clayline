#!/usr/bin/env python3
"""Twenty more coil-tile variations — set 4: Aztec/Mesoamerican, Scandinavian
folk (rosemaling / hearts), Ottoman-Iznik, Byzantine, Chinese lattice, Roman
mosaic, mid-century atomic and Nordic star traditions. Same idealized-
centerline, compass-and-ruler language as sets 1-3: design space 200x200
emitted at 6x6 in, tangency-first, spirals/open lines deliberate, crossings
are drape-mode weave features.
"""
import math, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generate_variations as V
import generate_variations2 as V2
import generate_variations3 as V3

MM, C = V.MM, 100.0
circle, teardrop, spiral, rpoly, chain_ring = (
    V.circle, V.teardrop, V.spiral, V.rpoly, V.chain_ring)
comma, swirl, billiard, rounded_loop, fit_ring, heart = (
    V2.comma, V2.swirl, V2.billiard, V2.rounded_loop, V2.fit_ring, V2.heart)
arc_pts, line, ellipse, petal = V3.arc_pts, V3.line, V3.ellipse, V3.petal


def stepped_diamond(cx, cy, R, steps=3, rot=0.0):
    """Aztec stepped-fret diamond: a staircase-edged rhombus."""
    pts = []
    for q in range(4):
        base = math.radians(rot + 90 * q)
        for i in range(steps + 1):
            t = i / steps
            r = R * (1 - t)
            a = base + (math.pi / 2) * t
            pts.append((cx + r * math.cos(base) + (R * t) * math.cos(base + math.pi / 2),
                        cy + r * math.sin(base) + (R * t) * math.sin(base + math.pi / 2)))
    return ('poly', pts + [pts[0]], True)


# ---------------- the twenty tiles ----------------

def aztec_sun():
    """Aztec sun-stone: hub, ring, stepped rays."""
    els = [circle(C, C, 14), circle(C, C, 40), circle(C, C, 66)]
    for k in range(8):
        els.append(teardrop(C, C, 45 * k, 41, 92, 10))
    for k in range(8):
        th = math.radians(22.5 + 45 * k)
        els.append(circle(C + 53 * math.cos(th), C + 53 * math.sin(th), 8))
    return els


def aztec_stepped():
    """Aztec stepped-fret medallion: nested stepped diamonds + hub."""
    return [rpoly(C, C, 90, 4, 45, 6), rpoly(C, C, 66, 4, 45, 5),
            rpoly(C, C, 42, 4, 45, 4), rpoly(C, C, 42, 4, 0, 4), circle(C, C, 12)]


def rosemaling_heart():
    """Scandinavian rosemaling: a heart wreathed by C-scroll tendrils."""
    els = [heart(C, C + 62, -90, 4, 80, 76)]
    for sx in (-1, 1):
        rot = math.atan2(-1, sx)
        els.append(spiral(C + sx * 62, C - 40, 5, 22, 1.5, rot))
        els.append(spiral(C + sx * 70, C + 30, 5, 18, 1.4, rot + math.pi))
    els.append(circle(C, C - 6, 12))
    for k in range(6):
        els.append(teardrop(C, C - 6, -90 + 60 * k, 13, 34, 8))
    return els


def nordic_star():
    """Nordic eight-point star (selburose): woven diamond lattice."""
    els = [rpoly(C, C, 88, 4, 0, 6), rpoly(C, C, 88, 4, 45, 6),
           rpoly(C, C, 44, 4, 0, 4), rpoly(C, C, 44, 4, 45, 4), circle(C, C, 12)]
    return els


def dala_horse_rosette():
    """Dala-style kurbits rosette: bulbous petals in two crowns."""
    els = [circle(C, C, 12)]
    for k in range(6):
        els.append(teardrop(C, C, 60 * k, 13, 52, 16))
    els.append(circle(C, C, 52))
    for k in range(6):
        els.append(teardrop(C, C, 30 + 60 * k, 53, 88, 12))
    return els


def iznik_tulip():
    """Ottoman Iznik tulip: one bold tulip bloom on a stem, two leaves, vase mound."""
    els = [circle(C, C + 76, 20), line((C, C + 56), (C, C - 10))]
    els.append(teardrop(C, C - 10, -90, 0, 66, 22))               # bloom
    for sx in (-1, 1):                                            # outer petals
        els.append(teardrop(C, C - 10, -90 + sx * 30, 0, 52, 12))
        els.append(comma(-90 + sx * 62, 30, 78, 12, 26 * sx))     # leaves
    return els


def iznik_saz():
    """Iznik saz-leaf medallion: long serrated leaves swirling around a hub."""
    els = [circle(C, C, 14)]
    for k in range(6):
        els.append(comma(60 * k, 14.7, 88, 14, 55))
    els.append(circle(C, C, 88))
    return els


def byzantine_cross():
    """Byzantine cross-in-square: cross, four corner circles, bounding square."""
    els = [rpoly(C, C, 96, 4, 45, 10), circle(C, C, 16)]
    for k in range(4):
        els.append(teardrop(C, C, 90 * k, 16.7, 62, 14))
    for sx in (-1, 1):
        for sy in (-1, 1):
            els.append(circle(C + sx * 52, C + sy * 52, 18))
    return els


def byzantine_medallion():
    """Byzantine roundel: concentric rings with a chain of pearls."""
    els = [circle(C, C, 88), circle(C, C, 66), circle(C, C, 22)]
    els += chain_ring(C, C, 77, 20)
    for k in range(8):
        els.append(teardrop(C, C, 45 * k, 23, 64, 10))
    return els


def chinese_lattice():
    """Chinese window lattice: a bold cracked-ice / square-knot grid."""
    els = [rpoly(C, C, 98, 4, 45, 6)]
    for v in (-46, 0, 46):
        els.append(line((C + v, 31), (C + v, 169)))
        els.append(line((31, C + v), (169, C + v)))
    for sx in (-1, 1):
        for sy in (-1, 1):
            els.append(circle(C + sx * 23, C + sy * 23, 14))
    return els


def chinese_shou():
    """Chinese longevity roundel: nested rounded squares in a ring, dot cross."""
    els = [circle(C, C, 88), rpoly(C, C, 60, 4, 45, 14), rpoly(C, C, 34, 4, 0, 8),
           circle(C, C, 10)]
    for k in range(4):
        th = math.radians(90 * k)
        els.append(circle(C + 74 * math.cos(th), C + 74 * math.sin(th), 10))
    return els


def roman_guilloche():
    """Roman mosaic guilloche: two braided sine bands with eye rings."""
    els = []
    for phase in (0.0, math.pi):
        pts = [(14 + 172 * i / 80, C + 30 * math.sin(2 * math.pi * 2 * i / 80 + phase))
               for i in range(81)]
        els.append(('poly', pts, False))
    for k in range(2):
        els.append(circle(14 + 172 * (k + 0.5) / 2, C, 12))
    for k in range(3):
        els.append(circle(14 + 172 * k / 2, C, 7))
    return els


def roman_wave_scroll():
    """Roman running-wave (Vitruvian scroll): a row of spirals on a baseline."""
    els = [line((10, 128), (190, 128))]
    for k in range(5):
        cx = 26 + 37 * k
        els.append(spiral(cx, 96, 5, 22, 1.5, math.radians(90)))
    els.append(line((10, 72), (190, 72)))
    return els


def atomic_starburst():
    """Mid-century atomic starburst: rays of varied length tipped with dots."""
    els = [circle(C, C, 10)]
    for k in range(16):
        th = math.radians(22.5 * k)
        L = 84 if k % 4 == 0 else (66 if k % 2 == 0 else 46)
        els.append(line((C + 10 * math.cos(th), C + 10 * math.sin(th)),
                        (C + L * math.cos(th), C + L * math.sin(th))))
        els.append(circle(C + (L + 7) * math.cos(th), C + (L + 7) * math.sin(th), 6))
    return els


def atomic_orbits():
    """Atomic-age orbits: three tilted ellipses around a nucleus."""
    els = [circle(C, C, 12)]
    for rot in (0, 60, 120):
        els.append(ellipse(C, C, 84, 30, rot))
    for rot in (0, 60, 120):
        th = math.radians(rot)
        els.append(circle(C + 84 * math.cos(th), C + 84 * math.sin(th), 7))
    return els


def hex_honeycomb():
    """Honeycomb: seven fused hexagons with a centre dot."""
    R = 30
    els = [rpoly(C, C, R, 6, 30, 3), circle(C, C, 8)]
    for k in range(6):
        th = math.radians(60 * k)
        els.append(rpoly(C + 2 * R * 0.866 * math.cos(th), C + 2 * R * 0.866 * math.sin(th),
                         R, 6, 30, 3))
    return els


def gothic_rose():
    """Gothic rose window: 12 petal lobes between two rings + tracery spokes."""
    els = [circle(C, C, 88), circle(C, C, 60), circle(C, C, 16)]
    for k in range(12):
        th = math.radians(30 * k)
        els.append(circle(C + 74 * math.cos(th), C + 74 * math.sin(th), 13))
    for k in range(6):
        els.append(teardrop(C, C, 60 * k, 17, 58, 12))
    return els


def moorish_lattice():
    """Moorish window: pointed-arch tessellation of overlapping circles."""
    els = []
    step = 44
    for j in range(4):
        y = 44 + 38 * j
        off = 0 if j % 2 == 0 else step / 2
        x = 34 + off
        while x <= 168:
            els.append(circle(x, y, 22))
            x += step
    return els


def tibetan_lotus_wheel():
    """Eight-petal lotus wheel: petals kissing a rim ring, hub rosette."""
    els = [circle(C, C, 88), circle(C, C, 12)]
    for k in range(8):
        els.append(teardrop(C, C, 45 * k, 13, 86, 16))
    for k in range(8):
        th = math.radians(22.5 + 45 * k)
        els.append(circle(C + 40 * math.cos(th), C + 40 * math.sin(th), 7))
    return els


def sun_wheel():
    """Sun wheel: hub, spokes, rim, and a ring of tucked pearls."""
    els = [circle(C, C, 88), circle(C, C, 62), circle(C, C, 14)]
    for k in range(12):
        th = math.radians(30 * k)
        els.append(line((C + 14 * math.cos(th), C + 14 * math.sin(th)),
                        (C + 62 * math.cos(th), C + 62 * math.sin(th))))
    els += chain_ring(C, C, 75, 16)
    return els


TILES4 = [
    ('aztec-sun', aztec_sun, 'Aztec sun-stone with stepped rays'),
    ('aztec-stepped', aztec_stepped, 'Aztec stepped-fret medallion'),
    ('rosemaling-heart', rosemaling_heart, 'Scandinavian rosemaling heart with C-scrolls'),
    ('nordic-star', nordic_star, 'Nordic eight-point selburose'),
    ('kurbits-rosette', dala_horse_rosette, 'Swedish kurbits rosette'),
    ('iznik-tulip', iznik_tulip, 'Ottoman Iznik tulip spray'),
    ('iznik-saz', iznik_saz, 'Iznik saz-leaf medallion'),
    ('byzantine-cross', byzantine_cross, 'Byzantine cross-in-square'),
    ('byzantine-medallion', byzantine_medallion, 'Byzantine pearl roundel'),
    ('chinese-lattice', chinese_lattice, 'Chinese window lattice'),
    ('chinese-shou', chinese_shou, 'Chinese longevity roundel'),
    ('roman-guilloche', roman_guilloche, 'Roman mosaic guilloche braid'),
    ('roman-wave', roman_wave_scroll, 'Roman running-wave scroll'),
    ('atomic-starburst', atomic_starburst, 'mid-century atomic starburst'),
    ('atomic-orbits', atomic_orbits, 'atomic-age orbits'),
    ('honeycomb', hex_honeycomb, 'seven-cell honeycomb'),
    ('gothic-rose', gothic_rose, 'Gothic rose window'),
    ('moorish-lattice', moorish_lattice, 'Moorish pointed-arch lattice'),
    ('lotus-wheel', tibetan_lotus_wheel, 'eight-petal lotus wheel'),
    ('sun-wheel', sun_wheel, 'spoked sun wheel with pearls'),
]


if __name__ == '__main__':
    from PIL import Image, ImageDraw
    outdir = sys.argv[1] if len(sys.argv) > 1 else '.'
    thumbs = []
    for name, fn, desc in TILES4:
        els = [e for e in fn() if e]
        V.to_svg(els, os.path.join(outdir, f'{name}.svg'), f'clayline tile: {name} — {desc}')
        im, lo, hi = V.render(els, os.path.join(outdir, f'{name}.png'))
        flag = '' if 2.0 <= lo and hi <= 198.0 else f'  ** BOUNDS {lo:.1f}..{hi:.1f}'
        print(f'{name:22s} {len(els):3d} elements{flag}')
        thumbs.append((name, im))
    tw, cols = 360, 5
    rows = (len(thumbs) + cols - 1) // cols
    sheet = Image.new('RGB', (tw * cols + 24, (tw + 26) * rows + 8), 'white')
    dr = ImageDraw.Draw(sheet)
    for i, (name, im) in enumerate(thumbs):
        x, y = (i % cols) * (tw + 4) + 4, (i // cols) * (tw + 26) + 4
        sheet.paste(im.resize((tw, tw)), (x, y))
        dr.text((x + 4, y + tw + 4), name, fill='black')
    sheet.save(os.path.join(outdir, 'contact-sheet-4.jpg'), quality=88)
    print('contact sheet written')
