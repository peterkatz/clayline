#!/usr/bin/env python3
"""Ten coil-tile variations for Clayline — Moroccan / Arabic / Andalusian
influences, in the same idealized-centerline language as the photo tracings.

Design space 200x200, emitted at 6x6 in / 152.4 mm (SVG_SIZE_MM); tangency-first (closed loops kiss or overlap so the
kiss-hop planner can fuse them); spirals are deliberate open strokes.
Crossings are deliberate weave features for drape-mode printing.
"""
import math
from PIL import Image, ImageDraw, ImageFont

MM, PX, BEAD = 200.0, 3.0, 6.0
CLAY = (139, 125, 116)
C = 100.0  # tile center

def circle(cx, cy, r):
    return ('circle', cx, cy, r)

def spiral(cx, cy, r0, r1, turns, rot=0.0):
    return ('spiral', cx, cy, r0, r1, turns, rot)

def spiral_pts(cx, cy, r0, r1, turns, rot=0.0, n=140):
    pts = []
    for i in range(n + 1):
        t = i / n
        th = rot + 2 * math.pi * turns * t
        r = r0 + (r1 - r0) * t
        pts.append((cx + r * math.cos(th), cy + r * math.sin(th)))
    return pts

def bez(p0, c1, c2, p1, n=22):
    out = []
    for i in range(1, n + 1):
        t = i / n; u = 1 - t
        out.append(tuple(u**3*a + 3*u*u*t*b + 3*u*t*t*c + t**3*d
                         for a, b, c, d in zip(p0, c1, c2, p1)))
    return out

def teardrop(cx, cy, angle_deg, a, b, w):
    """Closed teardrop: tip at distance a along angle, round bulb at b."""
    L = b - a
    tip, apex = (0.0, a), (0.0, b)
    c1, c2 = (-w, a + 0.30*L), (-w, b - 0.38*L)
    c3, c4 = (-w, b - 0.06*L), (-0.55*w, b)
    mid = (-w * 0.92, b - 0.30*L)
    m = lambda p: (-p[0], p[1])
    loc = [tip]
    loc += bez(tip, c1, c2, mid) + bez(mid, c3, c4, apex)
    loc += bez(apex, m(c4), m(c3), m(mid)) + bez(m(mid), m(c2), m(c1), tip)
    th = math.radians(angle_deg)
    pts = [(cx + x*math.cos(th + math.pi/2) + y*math.cos(th),
            cy + x*math.sin(th + math.pi/2) + y*math.sin(th)) for x, y in loc]
    return ('poly', pts, True)

def rpoly(cx, cy, R, n, rot_deg=0.0, corner=10.0):
    """Rounded regular polygon (circumradius R), quadratic-bezier corners."""
    rot = math.radians(rot_deg)
    V = [(cx + R*math.cos(rot + 2*math.pi*k/n), cy + R*math.sin(rot + 2*math.pi*k/n))
         for k in range(n)]
    side = math.dist(V[0], V[1])
    d = min(corner, side * 0.45)
    pts = []
    for k in range(n):
        p, v, q = V[(k-1) % n], V[k], V[(k+1) % n]
        f = lambda a, b, t: (a[0] + (b[0]-a[0])*t, a[1] + (b[1]-a[1])*t)
        A = f(v, p, d / side); B = f(v, q, d / side)
        pts.append(A)
        for i in range(1, 13):   # quadratic corner
            t = i / 12; u = 1 - t
            pts.append((u*u*A[0] + 2*u*t*v[0] + t*t*B[0],
                        u*u*A[1] + 2*u*t*v[1] + t*t*B[1]))
    pts.append(pts[0])
    return ('poly', pts, True)

def chain_ring(cx, cy, R, n, r=None, phase=0.0):
    """n mutually tangent circles on radius R (multifoil)."""
    r = r if r else R * math.sin(math.pi / n) * 1.02
    return [circle(cx + R*math.cos(phase + 2*math.pi*k/n),
                   cy + R*math.sin(phase + 2*math.pi*k/n), r) for k in range(n)]

# ---------------- the ten tiles ----------------

def khatam_star():
    """Moroccan khatam: two rounded squares woven into an 8-point star."""
    els = [rpoly(C, C, 62, 4, 45, 12), rpoly(C, C, 62, 4, 0, 12),
           circle(C, C, 14)]
    for k in range(4):   # tie the hub to the woven squares
        els.append(teardrop(C, C, 45 + 90*k, 14.5, 45, 8))
    els += chain_ring(C, C, 70, 8, r=13)   # dots off every star point
    for p in (30, 170):
        for q in (30, 170):
            els.append(circle(p, q, 15.5))
    return els

def zellige_rosette():
    """Fez zellige sunburst: hub, 8 petals, tucked rings, multifoil border ring."""
    els = [circle(C, C, 10)]
    for k in range(8):
        els.append(teardrop(C, C, 45*k, 11, 74, 12))
    els += chain_ring(C, C, 58, 8, r=12, phase=math.radians(22.5))
    els += chain_ring(C, C, 83, 20)
    return els

def alhambra_lattice():
    """Alhambra breath: 4x4 deeply overlapping circle weave + corner dots."""
    els = []
    step = (167.0 - 33.0) / 3
    for i in range(4):
        for j in range(4):
            els.append(circle(33 + step*i, 33 + step*j, 30))
    return els

def quatrefoil_grid():
    """Sevillian azulejo: 2x2 quatrefoils, ring connectors."""
    els = []
    for qx in (50, 150):
        for qy in (50, 150):
            for dx, dy in ((22, 0), (-22, 0), (0, 22), (0, -22)):
                els.append(circle(qx + dx, qy + dy, 22))
            els.append(circle(qx, qy, 9))
    for cx, cy in ((100, 50), (100, 150), (50, 100), (150, 100)):
        els.append(circle(cx, cy, 7.5))
    return els

def octagon_cross():
    """Zellige star-and-cross: 4 rounded octagons + center diamond + edge rings."""
    els = []
    for p in (52, 148):
        for q in (52, 148):
            els.append(rpoly(p, q, 38, 8, 22.5, 8))
    els.append(rpoly(C, C, 34, 4, 45, 6))
    for cx, cy in ((100, 34), (100, 166), (34, 100), (166, 100)):
        els.append(circle(cx, cy, 15))
    return els

def multifoil_medallion():
    """Cordoba multifoil: hub, petals, 12-lobe chain, corner spirals."""
    els = [circle(C, C, 12)]
    for k in range(8):
        els.append(teardrop(C, C, 45*k, 13, 40, 9))
    els += chain_ring(C, C, 52, 12)
    for sx in (-1, 1):
        for sy in (-1, 1):
            rot = math.atan2(sy, sx)
            els.append(spiral(C + sx*53.2, C + sy*53.2, 5, 15, 1.5, rot))
    for cx, cy in ((100, 22), (100, 178), (22, 100), (178, 100)):
        els.append(circle(cx, cy, 12.5))
    return els

def mudejar_weave():
    """Mudéjar lacería: concentric square/circle/square/circle weave."""
    return [rpoly(C, C, 92, 4, 0, 16), circle(C, C, 72),
            rpoly(C, C, 92, 4, 45, 16), circle(C, C, 47),
            circle(C, C, 12),
            teardrop(C, C, 45, 12.7, 76, 9), teardrop(C, C, 135, 12.7, 76, 9),
            teardrop(C, C, 225, 12.7, 76, 9), teardrop(C, C, 315, 12.7, 76, 9)]

def andalus_vine():
    """Arabesque tendrils: central rosette, diagonal petals, corner spirals."""
    els = [circle(C, C, 10)]
    for k in range(4):
        els.append(teardrop(C, C, 90*k, 10.7, 58, 11))
    for k in range(4):
        els.append(teardrop(C, C, 45 + 90*k, 10.7, 42, 8))
    for sx in (-1, 1):
        for sy in (-1, 1):
            rot = math.atan2(-sy, -sx)
            els.append(spiral(C + sx*45.3, C + sy*45.3, 4, 22, 2.0, rot))
    for cx, cy in ((100, 33), (100, 167), (33, 100), (167, 100)):
        els.append(circle(cx, cy, 15))
    return els

def fez_medallion():
    """Fez medallion: hub, 8 petals, 8 tucked rings, 20-lobe multifoil rim."""
    els = [circle(C, C, 11)]
    for k in range(8):
        els.append(teardrop(C, C, 45*k, 12, 54, 12.5))
    els += chain_ring(C, C, 60, 8, r=13, phase=math.radians(22.5))
    els += chain_ring(C, C, 80, 20)
    return els

def granada_sunburst():
    """Granada sunburst: 16 alternating rays + corner rings."""
    els = [circle(C, C, 12)]
    for k in range(16):
        long = (k % 2 == 0)
        els.append(teardrop(C, C, 22.5*k, 12.7, 74 if long else 50,
                             7.5 if long else 6.5))
    for p in (40, 160):
        for q in (40, 160):
            els.append(circle(p, q, 13))
    return els

TILES = [
    ('khatam-star', khatam_star, 'two woven rounded squares — Moroccan khatam 8-point star'),
    ('zellige-rosette', zellige_rosette, 'Fez zellige sunburst with multifoil border'),
    ('alhambra-lattice', alhambra_lattice, 'Alhambra overlapping-circle weave'),
    ('quatrefoil-grid', quatrefoil_grid, 'Sevillian azulejo quatrefoils'),
    ('octagon-cross', octagon_cross, 'zellige star-and-cross octagons'),
    ('multifoil-medallion', multifoil_medallion, 'Cordoba multifoil medallion with corner spirals'),
    ('mudejar-weave', mudejar_weave, 'Mudéjar lacería concentric weave'),
    ('andalus-vine', andalus_vine, 'Andalusian arabesque tendrils'),
    ('fez-medallion', fez_medallion, 'Fez triple-ring medallion'),
    ('granada-sunburst', granada_sunburst, 'Granada 16-ray sunburst'),
]

# ---------------- output ----------------

def el_pts(el):
    k = el[0]
    if k == 'circle':
        _, cx, cy, r = el
        return [(cx + r*math.cos(2*math.pi*i/96), cy + r*math.sin(2*math.pi*i/96))
                for i in range(97)]
    if k == 'spiral':
        return spiral_pts(*el[1:])
    return el[1]

SVG_SIZE_MM = 152.4          # physical tile size: 6 x 6 inches

def to_svg(els, fname, title):
    sc = SVG_SIZE_MM / MM     # design space is 200x200; emit scaled to 6"
    W = MM * sc
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{W}mm" '
           f'viewBox="0 0 {W:g} {W:g}">', f'  <title>{title}</title>',
           f'  <g fill="none" stroke="rgb{CLAY}" stroke-width="{BEAD*sc:.3f}" '
           'stroke-linecap="round" stroke-linejoin="round">']
    for el in els:
        if el[0] == 'circle':
            _, cx, cy, r = el
            out.append(f'    <circle cx="{cx*sc:.3f}" cy="{cy*sc:.3f}" r="{r*sc:.3f}"/>')
        else:
            pts = el_pts(el)
            closed = el[0] == 'poly' and el[2]
            d = 'M ' + ' L '.join(f'{x*sc:.3f} {y*sc:.3f}' for x, y in pts) + (' Z' if closed else '')
            out.append(f'    <path d="{d}"/>')
    out += ['  </g>', '</svg>', '']
    open(fname, 'w').write('\n'.join(out))

def render(els, fname):
    S = int(MM * PX)
    im = Image.new('RGB', (S, S), (244, 241, 236))
    dr = ImageDraw.Draw(im)
    w = int(BEAD * PX)
    lo = hi = None
    for el in els:
        pts = el_pts(el)
        for x, y in pts:
            lo = min(lo, x, y) if lo is not None else min(x, y)
            hi = max(hi, x, y) if hi is not None else max(x, y)
        dr.line([(x*PX, y*PX) for x, y in pts], fill=CLAY, width=w, joint='curve')
    im.save(fname)
    return im, lo, hi

import os, sys
if __name__ == '__main__':
    outdir = sys.argv[1] if len(sys.argv) > 1 else '.'
    thumbs = []
    for name, fn, desc in TILES:
        els = fn()
        to_svg(els, os.path.join(outdir, f'{name}.svg'), f'clayline tile: {name} — {desc}')
        im, lo, hi = render(els, os.path.join(outdir, f'{name}.png'))
        flag = '' if 2.5 <= lo and hi <= 197.5 else f'  ** BOUNDS {lo:.1f}..{hi:.1f}'
        print(f'{name:22s} {len(els):3d} elements{flag}')
        thumbs.append((name, im))
    # contact sheet 5 x 2
    tw = 360
    sheet = Image.new('RGB', (tw*5 + 24, tw*2 + 60), 'white')
    dr = ImageDraw.Draw(sheet)
    for i, (name, im) in enumerate(thumbs):
        x, y = (i % 5) * (tw + 4) + 4, (i // 5) * (tw + 26) + 4
        sheet.paste(im.resize((tw, tw)), (x, y))
        dr.text((x + 4, y + tw + 4), name, fill='black')
    sheet.save(os.path.join(outdir, 'contact-sheet.jpg'), quality=88)
    print('contact sheet written')
