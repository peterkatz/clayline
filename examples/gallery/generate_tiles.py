#!/usr/bin/env python3
"""Digitize Pete's three hand-built coil tiles into idealized SVG line-work.

Design space is 200x200; SVGs emit at 6x6 in / 152.4 mm (SVG_SIZE_MM).
Also renders PIL previews + side-by-side composites against the photos.
"""
import math
from PIL import Image, ImageOps, ImageDraw

MM = 200.0            # tile size in mm
PX = 3.0              # preview px per mm
BEAD = 6.0            # stroke width (visual bead), mm
CLAY = (139, 125, 116)

# ---------- geometry primitives ----------

def circle(cx, cy, r):
    return ('circle', cx, cy, r)

def teardrop(cx, cy, angle_deg, a, b, w):
    """Teardrop petal radiating from tile-ish center (cx,cy).
    Tip at distance a along angle, round bulb apex at distance b, half-width w.
    Returns sampled closed polyline (list of points) + bezier spec for SVG."""
    L = b - a
    # control net in local coords: +y outward, x sideways
    tip = (0, a)
    apex = (0, b)
    c1 = (-w, a + 0.30 * L); c2 = (-w, b - 0.38 * L)      # side out
    c3 = (-w, b - 0.06 * L); c4 = (-0.55 * w, b)          # round bulb
    left = [('M', tip), ('C', c1, c2, (-w * 0.92, b - 0.30 * L)),
            ('C', c3, c4, apex)]
    # mirror for right side (reverse direction back to tip)
    m = lambda p: (-p[0], p[1])
    right = [('C', m(c4), m(c3), m((-w * 0.92, b - 0.30 * L))),
             ('C', m(c2), m(c1), tip)]
    segs = left + right
    th = math.radians(angle_deg)

    def xform(p):
        x, y = p
        # rotate local +y to angle direction, translate to center
        return (cx + x * math.cos(th + math.pi / 2) + y * math.cos(th),
                cy + x * math.sin(th + math.pi / 2) + y * math.sin(th))
    return ('path', segs, xform)

# ---------- tile definitions ----------

def rings_grid():
    """IMG_3074: 4x4 grid, 12 perimeter rings, central 8-petal rosette + hub."""
    els = []
    cell = MM / 4.0
    R = 25.8
    for i in range(4):
        for j in range(4):
            if i in (0, 3) or j in (0, 3):
                els.append(circle(cell * (i + 0.5), cell * (j + 0.5), R))
    els.append(circle(100, 100, 10))
    for k in range(4):   # axial teardrops, kiss the mid-edge rings
        els.append(teardrop(100, 100, 90 * k, 10.5, 52, 9.5))
    for k in range(4):   # diagonal petals, reach the corner rings
        els.append(teardrop(100, 100, 45 + 90 * k, 10.5, 80, 12.0))
    return els

def rosette():
    """IMG_3073: 3x3 majors; corners+center wreaths (inner ring internally
    tangent), edge-mids plain; 4 interstitial small rings."""
    els = []
    P = [36, 100, 164]
    RC, RE, RI, RS = 35, 30.5, 24, 12.5
    RCC = 37   # center wreath slightly larger
    for i in (0, 2):
        for j in (0, 2):
            cx, cy = P[i], P[j]
            els.append(circle(cx, cy, RC))
            # inner ring internally tangent, offset toward tile center
            th = math.atan2(100 - cy, 100 - cx)
            d = RC - RI
            els.append(circle(cx + d * math.cos(th), cy + d * math.sin(th), RI))
    els.append(circle(100, 100, RCC))
    els.append(circle(100, 100 + (RCC - RI), RI))     # center wreath, inner low
    for cx, cy in [(100, 36), (100, 164), (36, 100), (164, 100)]:
        els.append(circle(cx, cy, RE))
    for cx in (68, 132):
        for cy in (68, 132):
            els.append(circle(cx, cy, RS))
    return els

def petal_flower():
    """IMG_3071: border of small rings (7/side), central 8-petal rosette with
    hub, 8 inter-petal gap rings, 4 diagonal corner fillers."""
    els = []
    inset, n, RB = 16, 7, 14.3
    step = (MM - 2 * inset) / (n - 1)
    for k in range(n):
        t = inset + k * step
        for cx, cy in [(t, inset), (t, MM - inset)]:
            els.append(circle(cx, cy, RB))
        if 0 < k < n - 1:
            for cx, cy in [(inset, t), (MM - inset, t)]:
                els.append(circle(cx, cy, RB))
    els.append(('spiral', 100, 100, 5.0, 11.0, 1.6))   # coiled hub
    for k in range(4):
        els.append(teardrop(100, 100, 90 * k, 11.5, 69.5, 12))   # axial, kiss border
    for k in range(4):
        els.append(teardrop(100, 100, 45 + 90 * k, 11.5, 74, 12))  # diagonal, kiss corner filler
    for k in range(8):   # inter-petal gap rings
        th = math.radians(22.5 + 45 * k)
        els.append(circle(100 + 56 * math.cos(th), 100 + 56 * math.sin(th), 10))
    for sx in (-1, 1):   # diagonal corner fillers
        for sy in (-1, 1):
            els.append(circle(100 + sx * 59.5, 100 + sy * 59.5, 10))
    return els

# ---------- output: SVG ----------

def bez_sample(p0, c1, c2, p1, n=24):
    pts = []
    for i in range(1, n + 1):
        t = i / n
        u = 1 - t
        pts.append(tuple(u**3 * a + 3 * u * u * t * b + 3 * u * t * t * c + t**3 * d
                         for a, b, c, d in zip(p0, c1, c2, p1)))
    return pts

def spiral_pts(cx, cy, r0, r1, turns, n=120):
    pts = []
    for i in range(n + 1):
        t = i / n
        th = 2 * math.pi * turns * t - math.pi / 2
        r = r0 + (r1 - r0) * t
        pts.append((cx + r * math.cos(th), cy + r * math.sin(th)))
    return pts

SVG_SIZE_MM = 152.4          # physical tile size: 6 x 6 inches

def to_svg(els, fname, title):
    sc = SVG_SIZE_MM / MM     # design space is 200x200; emit scaled to 6"
    W = MM * sc
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{W}mm" '
           f'viewBox="0 0 {W:g} {W:g}">',
           f'  <title>{title}</title>',
           f'  <g fill="none" stroke="rgb{CLAY}" stroke-width="{BEAD*sc:.3f}" '
           'stroke-linecap="round" stroke-linejoin="round">']
    for el in els:
        if el[0] == 'circle':
            _, cx, cy, r = el
            out.append(f'    <circle cx="{cx*sc:.3f}" cy="{cy*sc:.3f}" r="{r*sc:.3f}"/>')
        elif el[0] == 'spiral':
            _, cx, cy, r0, r1, turns = el
            pts = spiral_pts(cx, cy, r0, r1, turns)
            d = 'M ' + ' L '.join(f'{x*sc:.3f} {y*sc:.3f}' for x, y in pts)
            out.append(f'    <path d="{d}"/>')
        else:
            _, segs, xf = el
            d = []
            for seg in segs:
                if seg[0] == 'M':
                    x, y = xf(seg[1]); d.append(f'M {x*sc:.3f} {y*sc:.3f}')
                else:
                    (x1, y1), (x2, y2), (x3, y3) = (xf(p) for p in seg[1:])
                    d.append(f'C {x1*sc:.3f} {y1*sc:.3f} {x2*sc:.3f} {y2*sc:.3f} {x3*sc:.3f} {y3*sc:.3f}')
            d.append('Z')
            out.append(f'    <path d="{" ".join(d)}"/>')
    out += ['  </g>', '</svg>', '']
    open(fname, 'w').write('\n'.join(out))

# ---------- output: PIL preview ----------

def render(els, fname):
    S = int(MM * PX)
    im = Image.new('RGB', (S, S), (244, 241, 236))
    dr = ImageDraw.Draw(im)
    wpx = int(BEAD * PX)
    for el in els:
        if el[0] == 'circle':
            _, cx, cy, r = el
            bb = [(cx - r) * PX, (cy - r) * PX, (cx + r) * PX, (cy + r) * PX]
            dr.ellipse(bb, outline=CLAY, width=wpx)
        elif el[0] == 'spiral':
            _, cx, cy, r0, r1, turns = el
            pts = spiral_pts(cx, cy, r0, r1, turns)
            dr.line([(x * PX, y * PX) for x, y in pts], fill=CLAY,
                    width=wpx, joint='curve')
        else:
            _, segs, xf = el
            pts, cur = [], None
            for seg in segs:
                if seg[0] == 'M':
                    cur = xf(seg[1]); pts.append(cur)
                else:
                    c1, c2, p1 = (xf(p) for p in seg[1:])
                    pts += bez_sample(cur, c1, c2, p1)
                    cur = p1
            pts.append(pts[0])
            dr.line([(x * PX, y * PX) for x, y in pts], fill=CLAY,
                    width=wpx, joint='curve')
    im.save(fname)
    return im

def composite(photo, crop_frac, render_im, fname):
    im = ImageOps.exif_transpose(Image.open(photo))
    W, H = im.size
    l, t, r, b = crop_frac
    tile = im.crop((int(l * W), int(t * H), int(r * W), int(b * H)))
    h = render_im.height
    tile = tile.resize((int(tile.width * h / tile.height), h))
    canvas = Image.new('RGB', (tile.width + render_im.width + 12, h), 'white')
    canvas.paste(tile, (0, 0))
    canvas.paste(render_im, (tile.width + 12, 0))
    canvas.save(fname, quality=88)

TILES = [
    ('rings-grid',   rings_grid(),   '../../docs/reference/IMG_3074.jpg', (0.06, 0.20, 0.92, 0.86)),
    ('rosette',      rosette(),      '../../docs/reference/IMG_3073.jpg', (0.02, 0.14, 0.90, 0.80)),
    ('petal-flower', petal_flower(), '../../docs/reference/IMG_3071.jpg', (0.07, 0.16, 0.90, 0.80)),
]

import sys, os
outdir = sys.argv[1] if len(sys.argv) > 1 else '.'
for name, els, photo, crop in TILES:
    to_svg(els, os.path.join(outdir, f'{name}.svg'), f'clayline tile: {name}')
    im = render(els, os.path.join(outdir, f'{name}.png'))
    composite(photo, crop, im, os.path.join(outdir, f'compare-{name}.jpg'))
    print(name, 'done,', len(els), 'elements')
