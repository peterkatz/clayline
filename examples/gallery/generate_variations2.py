#!/usr/bin/env python3
"""Ten more coil-tile variations — Indian & Tibetan influences.

Same rules as generate_variations.py: design space 200x200 emitted at 6x6 in, tangency-first, closed loops fuse,
spirals/knot-lines may be open by design, crossings are drape-mode features.
New tricks: swirl() bends teardrops into gankyil commas and paisley boteh
(rotation-per-radius preserves radial tangencies); billiard() traces the
single closed weaving line behind endless knots and kolam loops.
"""
import math, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generate_variations as V

MM, C = V.MM, 100.0
circle, teardrop, spiral, rpoly, chain_ring = (
    V.circle, V.teardrop, V.spiral, V.rpoly, V.chain_ring)

def swirl(el, k_deg, r_ref, cx=C, cy=C):
    """Rotate each point about (cx,cy) by k_deg * (radius/r_ref).
    Radial distances are preserved, so radial kisses survive."""
    pts = V.el_pts(el)
    out = []
    for x, y in pts:
        dx, dy = x - cx, y - cy
        r = math.hypot(dx, dy)
        a = math.radians(k_deg) * (r / r_ref)
        ca, sa = math.cos(a), math.sin(a)
        out.append((cx + dx*ca - dy*sa, cy + dx*sa + dy*ca))
    closed = el[0] == 'circle' or (el[0] == 'poly' and el[2])
    return ('poly', out, closed)

def comma(angle_deg, a, b, w, k_deg):
    """Gankyil comma / paisley boteh: swirled teardrop."""
    return swirl(teardrop(C, C, angle_deg, a, b, w), k_deg, b)

def billiard(p, q, x0, y0, w, h, rounds=3):
    """Closed 45-degree billiard weave in a box: the endless-knot/kolam line.
    Vertices at wall bounces, then Chaikin-rounded. Returns closed poly."""
    tri = lambda u: abs(2*(u - math.floor(u + 0.5)))
    fx, fy = 0.031, 0.0     # phase keeps bounces off the exact corners
    ts = sorted({(k/2 - fx) / p % 1.0 for k in range(2*p)} |
                {(k/2 - fy) / q % 1.0 for k in range(2*q)})
    pts = [(x0 + w*tri(p*t + fx), y0 + h*tri(q*t + fy)) for t in ts]
    for _ in range(rounds):                     # closed Chaikin
        nxt = []
        for i in range(len(pts)):
            a_, b_ = pts[i], pts[(i+1) % len(pts)]
            nxt.append((0.75*a_[0]+0.25*b_[0], 0.75*a_[1]+0.25*b_[1]))
            nxt.append((0.25*a_[0]+0.75*b_[0], 0.25*a_[1]+0.75*b_[1]))
        pts = nxt
    pts.append(pts[0])
    return ('poly', pts, True)

def fit_ring(els, cx, cy, overlap=0.6, rmin=5.0, rmax=14.0):
    """Ring centered at (cx,cy) sized to just cross the nearest geometry."""
    d = min(math.dist((cx, cy), p) for e in els for p in V.el_pts(e))
    r = d + overlap
    return circle(cx, cy, r) if rmin <= r <= rmax else None

# ---------------- the ten tiles ----------------

def lotus_mandala():
    """Indian/Tibetan lotus mandala: two petal rings between binding circles."""
    els = [circle(C, C, 11)]
    for k in range(8):
        els.append(teardrop(C, C, 45*k, 12, 46, 10))
    els.append(circle(C, C, 45.5))
    for k in range(16):
        els.append(teardrop(C, C, 11.25 + 22.5*k, 46.2, 84, 9))
    els.append(circle(C, C, 82))
    return els

def endless_knot():
    """Tibetan shrivatsa: one closed line weaving over itself."""
    return [billiard(3, 4, 25, 25, 150, 150)]   # the whole tile is ONE line

def gankyil():
    """Tibetan wheel of joy: three commas in a ring, lotus surround."""
    els = [circle(C, C, 12)]
    for k in range(3):
        els.append(comma(120*k, 12.7, 59.5, 14, 60))
    els.append(circle(C, C, 60))
    for k in range(12):
        els.append(teardrop(C, C, 30*k + 15, 60.7, 88, 9))
    return els

def kolam_weave():
    """South Indian kolam: one looping line threading a field of dots."""
    els = [billiard(4, 5, 16, 16, 168, 168)]
    for i in range(4):
        for j in range(5):
            cx = 16 + 168/4 * (i + 0.5)
            cy = 16 + 168/5 * (j + 0.5)
            r = fit_ring(els, cx, cy, rmin=6.0, rmax=11)
            if r: els.append(r)
    return els

def paisley_quartet():
    """Indian boteh: four paisleys swirling around a hub."""
    els = [circle(C, C, 13)]
    for k in range(4):
        els.append(comma(90*k, 13.7, 78, 15, 32))          # large boteh
    for k in range(4):
        els.append(comma(45 + 90*k, 13.7, 48, 9, 32))      # small boteh between
    for k in range(8):                                     # dots in the gaps
        th = math.radians(22.5 + 45*k + 24)
        r = fit_ring(els, C + 62*math.cos(th), C + 62*math.sin(th), rmax=15)
        if r: els.append(r)
    return els

def dharma_wheel():
    """Tibetan dharma wheel: hub, eight spokes through the rim, eight dots."""
    els = [circle(C, C, 12)]
    for k in range(8):
        els.append(teardrop(C, C, 45*k, 12.7, 76, 9))
    els.append(circle(C, C, 72))
    for k in range(8):
        th = math.radians(22.5 + 45*k)
        els.append(circle(C + 81.5*math.cos(th), C + 81.5*math.sin(th), 10))
    return els

def yantra_star():
    """Indian yantra: two woven rounded triangles, bound by a circle."""
    els = [rpoly(C, C, 70, 3, 90, 14), rpoly(C, C, 70, 3, -90, 14),
           circle(C, C, 61), circle(C, C, 12)]
    for k in range(6):
        els.append(teardrop(C, C, 30 + 60*k, 13, 38, 8))
    return els

def marigold_mandala():
    """Indian marigold garland: long petals threading two multifoil rings."""
    els = [circle(C, C, 10)]
    for k in range(12):
        els.append(teardrop(C, C, 30*k, 11, 76, 10))
    els += chain_ring(C, C, 58, 12, phase=math.radians(15))
    els += chain_ring(C, C, 84, 24)
    return els

def conch_mandala():
    """Shankha: a grand spiral in a ring, multifoil surround (spiral open)."""
    els = [circle(C, C, 66)]
    els += chain_ring(C, C, 80, 16)
    els.append(spiral(C, C, 8, 65.5, 3.2))
    return els

def padma_gate():
    """Tibetan mandala palace: walls, four gates, lotus wheel inside."""
    els = [rpoly(C, C, 125, 4, 45, 20), circle(C, C, 76), circle(C, C, 11)]
    ap = 125 * math.cos(math.pi/4)             # wall apothem = 88.39
    ap -= 2.0
    for cx, cy in ((C, C-ap), (C, C+ap), (C-ap, C), (C+ap, C)):
        els.append(rpoly(cx, cy, 14, 4, 45, 5))
    for k in range(4):
        els.append(teardrop(C, C, 90*k, 12, 90, 10))       # axials reach gates
    for k in range(4):
        els.append(teardrop(C, C, 45 + 90*k, 12, 80, 10))  # diagonals
    for cx, cy in ((17, 17), (183, 17), (17, 183), (183, 183)):
        r = fit_ring(els, cx, cy, rmin=4.5, rmax=12)
        if r: els.append(r)
    return els


def rounded_loop(pts, r):
    """Closed polyline with quadratic-rounded corners at every vertex."""
    n = len(pts)
    out = []
    for k in range(n):
        p, v, q = pts[(k-1) % n], pts[k], pts[(k+1) % n]
        lp = math.dist(v, p); lq = math.dist(v, q)
        d = min(r, 0.45 * lp, 0.45 * lq)
        A = (v[0] + (p[0]-v[0]) * d/lp, v[1] + (p[1]-v[1]) * d/lp)
        B = (v[0] + (q[0]-v[0]) * d/lq, v[1] + (q[1]-v[1]) * d/lq)
        out.append(A)
        for i in range(1, 13):
            t = i / 12.0; u = 1 - t
            out.append((u*u*A[0] + 2*u*t*v[0] + t*t*B[0],
                        u*u*A[1] + 2*u*t*v[1] + t*t*B[1]))
    out.append(out[0])
    return ('poly', out, True)

def serpentine_back():
    """Pete's marker sketch (docs/reference/IMG_3043.jpg), closed form: the
    vertical and horizontal serpentines are connected at two corners
    (bottom-right, top-left) so the whole backing is ONE closed line —
    no open ends, no travels. 5x5 woven grid, turns rounded."""
    G = [25 + 37.5*k for k in range(5)]
    cyc = []
    # vertical serpentine: col1 down ... col5 down
    for k, x in enumerate(G):
        if k % 2 == 0:
            cyc += [(x, 10), (x, 190)]
        else:
            cyc += [(x, 190), (x, 10)]
    # bottom-right connector: 45-degree diagonal into the horizontal pass
    # horizontal serpentine climbing from the bottom: row5 left ... row1 left
    for j, y in enumerate(reversed(G)):
        if j % 2 == 0:
            cyc += [(190, y), (10, y)]
        else:
            cyc += [(10, y), (190, y)]
    # top-left: the loop closes on a matching diagonal back to (25, 10)
    # drop consecutive duplicates introduced by the pattern joins
    dedup = [cyc[0]]
    for p in cyc[1:]:
        if p != dedup[-1]:
            dedup.append(p)
    return [rounded_loop(dedup, 15)]


def heart(cx, cy, angle_deg, tip_r, height, width):
    """Closed heart loop: tip at tip_r from (cx,cy) along angle, lobes outward.

    Classic parametric heart (16 sin^3 t), scaled to height/width, rotated so
    the tip points back toward the tile center — four of these make the
    clover hub of Pete's painted mandala (docs/reference/IMG_3151.jpg).
    """
    pts = []
    for i in range(120):
        t = 2.0 * math.pi * i / 120.0
        hx = 16.0 * math.sin(t) ** 3
        hy = 13.0 * math.cos(t) - 5.0 * math.cos(2 * t) - 2.0 * math.cos(3 * t) - math.cos(4 * t)
        pts.append((hx / 32.0 * width, (hy + 17.0) / 29.0 * height))
    th = math.radians(angle_deg)
    out = []
    for x, y in pts:
        yy = y + tip_r
        out.append((cx + x * math.cos(th + math.pi / 2) + yy * math.cos(th),
                    cy + x * math.sin(th + math.pi / 2) + yy * math.sin(th)))
    out.append(out[0])
    return ('poly', out, True)


def heart_mandala():
    """Pete's painted mandala panel (docs/reference/IMG_3151.jpg): four-heart
    clover hub, eye-dot ring, multifoil scallop band, petal corona threading
    a concentric ring, bound by an outer circle."""
    els = [V.circle(C, C, 7)]
    for k in range(4):
        els.append(heart(C, C, 45 + 90 * k, 5, 43, 40))
    for k in range(12):
        th = math.radians(30 * k)  # rings sit on the heart lobes (30/60/...) and fuse the hub cluster outward
        els.append(V.circle(C + 54 * math.cos(th), C + 54 * math.sin(th), 7.5))
    els += V.chain_ring(C, C, 68, 20)
    for k in range(12):
        els.append(V.teardrop(C, C, 30 * k, 70, 95, 7))
    els.append(V.circle(C, C, 84))
    els.append(V.circle(C, C, 94))
    return els


TILES2 = [
    ('heart-mandala', heart_mandala, 'four-heart clover mandala — from Pete\'s painted panel'),
    ('serpentine-back', serpentine_back, 'woven crosshatch backing — from Pete\'s marker sketch'),
    ('lotus-mandala', lotus_mandala, 'Indian/Tibetan lotus mandala, two petal rings'),
    ('endless-knot', endless_knot, 'Tibetan shrivatsa — one closed weaving line'),
    ('gankyil', gankyil, 'Tibetan wheel of joy with lotus surround'),
    ('kolam-weave', kolam_weave, 'South Indian kolam loop threading dots'),
    ('paisley-quartet', paisley_quartet, 'Indian boteh paisleys around a hub'),
    ('dharma-wheel', dharma_wheel, 'Tibetan eight-spoked wheel'),
    ('yantra-star', yantra_star, 'Indian yantra hexagram weave'),
    ('marigold-mandala', marigold_mandala, 'Indian marigold garland mandala'),
    ('conch-mandala', conch_mandala, 'shankha spiral in a multifoil ring'),
    ('padma-gate', padma_gate, 'Tibetan mandala palace with four gates'),
]

if __name__ == '__main__':
    from PIL import Image, ImageDraw
    outdir = sys.argv[1] if len(sys.argv) > 1 else '.'
    thumbs = []
    for name, fn, desc in TILES2:
        els = [e for e in fn() if e]
        V.to_svg(els, os.path.join(outdir, f'{name}.svg'),
                 f'clayline tile: {name} — {desc}')
        im, lo, hi = V.render(els, os.path.join(outdir, f'{name}.png'))
        flag = '' if 2.0 <= lo and hi <= 198.0 else f'  ** BOUNDS {lo:.1f}..{hi:.1f}'
        print(f'{name:20s} {len(els):3d} elements{flag}')
        thumbs.append((name, im))
    tw = 360
    cols = 4 if len(thumbs) <= 12 else 5
    rows = (len(thumbs) + cols - 1) // cols
    sheet = Image.new('RGB', (tw*cols + 24, (tw + 26)*rows + 8), 'white')
    dr = ImageDraw.Draw(sheet)
    for i, (name, im) in enumerate(thumbs):
        x, y = (i % cols) * (tw + 4) + 4, (i // cols) * (tw + 26) + 4
        sheet.paste(im.resize((tw, tw)), (x, y))
        dr.text((x + 4, y + tw + 4), name, fill='black')
    sheet.save(os.path.join(outdir, 'contact-sheet-2.jpg'), quality=88)
    print('contact sheet written')
