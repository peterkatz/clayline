#!/usr/bin/env python3
"""Zoo-animal coil tiles for Clayline, in the same idealized-centerline language
as the gallery/siding tiles. Loads the gallery primitives (circle, teardrop,
spiral, rpoly, chain_ring, comma, rounded_loop, bez) from the repo so emit
scale, bead width and clay colour match exactly.

Design space 200x200, emitted at 6x6 in / 152.4 mm; tangency-first so parts fuse
into as few strokes as possible; figurative, so a few open strokes (whiskers,
legs, antennae) are deliberate. Every tile is checked for floating pieces.
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


V2 = _load("generate_variations2")
V = V2.V
circle, teardrop, spiral, rpoly, chain_ring = (
    V.circle, V.teardrop, V.spiral, V.rpoly, V.chain_ring)
comma, rounded_loop = V2.comma, V2.rounded_loop
C = 100.0


def path(pts):
    return ("path", list(pts))


def smooth(points, closed=True, k=1.0):
    """Catmull-Rom through points -> smooth closed loop or open path."""
    pts = list(points)
    n = len(pts)
    out = []
    idx = range(n) if closed else range(n - 1)
    for i in idx:
        p0 = pts[(i - 1) % n] if closed else pts[max(i - 1, 0)]
        p1 = pts[i]
        p2 = pts[(i + 1) % n]
        p3 = pts[(i + 2) % n] if closed else pts[min(i + 2, n - 1)]
        c1 = (p1[0] + (p2[0] - p0[0]) * k / 6, p1[1] + (p2[1] - p0[1]) * k / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) * k / 6, p2[1] - (p3[1] - p1[1]) * k / 6)
        seg = V.bez(p1, c1, c2, p2)
        if not out:
            out.append(p1)
        out += seg
    if closed:
        out.append(out[0])
    return ("poly", out, True) if closed else ("path", out)


def spts(points, closed=False, k=1.0):
    return V.el_pts(smooth(points, closed, k))


# ------------------------- the animals -------------------------


def lion():
    """Lion face — mane of rays around a face medallion."""
    els = []
    for k in range(16):
        els.append(teardrop(C, C, 22.5 * k, 33, 72, 12))            # outer mane
    for k in range(16):
        els.append(teardrop(C, C, 22.5 * k + 11.25, 30, 58, 10))    # inner mane
    els.append(circle(C, C, 35))                                    # face binds the mane
    for sx in (-1, 1):
        els.append(circle(C + sx * 27, C - 30, 7))                 # ears (touch mane)
        els.append(circle(C + sx * 13, C - 8, 5))                  # eyes
    els.append(teardrop(C, C + 2, 90, 3, 13, 8))                    # nose
    els.append(path(spts([(C - 14, C - 8), (C, C + 5), (C + 14, C - 8)])))  # brow through eyes to nose
    els.append(path([(C, C + 14), (C, C + 33)]))                   # chin line ties face to ring
    return els


def elephant():
    """Elephant head-on — big ears, central trunk, tusks."""
    els = [smooth([(C, C - 54), (C + 38, C - 44), (C + 34, C + 6),
                   (C, C + 22), (C - 34, C + 6), (C - 38, C - 44)], closed=True)]  # domed head
    for sx in (-1, 1):
        els.append(smooth([(C + sx * 30, C - 44), (C + sx * 66, C - 40),
                           (C + sx * 70, C + 6), (C + sx * 40, C + 20),
                           (C + sx * 28, C + 4)], closed=True))    # big flapping ear
        els.append(circle(C + sx * 15, C - 20, 5))                # eyes
        els.append(path(spts([(C + sx * 12, C + 22), (C + sx * 20, C + 50), (C + sx * 10, C + 68)])))  # tusks
    els.append(path(spts([(C - 15, C - 20), (C, C + 15), (C + 15, C - 20)])))  # brow ties eyes down to trunk
    trunk = smooth([(C, C + 14), (C - 9, C + 40), (C + 9, C + 64),
                    (C - 6, C + 86), (C + 8, C + 96), (C + 18, C + 88)], closed=False)
    els.append(trunk)                                             # trunk centerline (touches brow at top)
    return els


def owl():
    """Owl face — two great eyes, beak, ear tufts, wings."""
    els = [circle(C, C + 4, 58)]                                   # body/face
    for sx in (-1, 1):
        els.append(circle(C + sx * 23, C - 12, 23))               # eye disc (meets its twin at centre)
        els.append(circle(C + sx * 23, C - 12, 7))                # pupil
        els.append(teardrop(C + sx * 22, C - 46, -90 + sx * 16, 4, 26, 9))  # ear tuft (crosses head rim)
        els.append(teardrop(C + sx * 46, C + 14, -90 + sx * 108, 8, 44, 13))  # wing
    els.append(teardrop(C, C - 14, 90, 2, 18, 7))                  # beak (tip at the eye discs)
    for k in range(7):                                            # belly feather scallops
        els.append(circle(C - 30 + 10 * k, C + 46, 6))
    return els


def peacock():
    """Peacock — an upward fan of eye-spotted tail feathers over a small body."""
    els = [circle(C, C + 66, 12), circle(C, C + 30, 9)]            # body, head
    els.append(path(spts([(C, C + 54), (C - 3, C + 42), (C, C + 30)])))  # neck
    for ao in (-16, 0, 16):                                       # crest
        els.append(path(spts([(C, C + 22), (C + ao * 0.4, C + 14), (C + ao, C + 6)])))
    for k in range(-5, 6):
        ang = -90 + k * 16
        L = 80
        els.append(teardrop(C, C + 42, ang, 8, L, 7))            # feather
        ex = C + (L - 5) * math.cos(math.radians(ang))
        ey = C + 42 + (L - 5) * math.sin(math.radians(ang))
        els.append(circle(ex, ey, 6))                            # eye-spot
    return els


def butterfly():
    """Butterfly — symmetric wings with spots, body and antennae."""
    els = [smooth([(C, C - 44), (C + 4, C), (C, C + 46), (C - 4, C)], closed=True)]  # body
    els.append(circle(C, C - 46, 5))                              # head
    for sx in (-1, 1):
        els.append(path(spts([(C, C - 48), (C + sx * 10, C - 60), (C + sx * 22, C - 66)])))  # antenna
        els.append(teardrop(C, C - 14, -90 + sx * 52, 6, 66, 28))  # upper wing
        els.append(teardrop(C, C + 14, -90 + sx * 130, 6, 52, 22))  # lower wing
        els.append(circle(C + sx * 44, C - 30, 8))               # upper spot
        els.append(circle(C + sx * 34, C + 30, 6))               # lower spot
    return els


def turtle():
    """Turtle from above — patterned shell with head, legs and tail poking out."""
    els = [circle(C, C, 60), rpoly(C, C, 29, 6, 0, 6)]            # shell + central scute (meets ring)
    for k in range(6):
        th = math.radians(60 * k)
        els.append(rpoly(C + 42 * math.cos(th), C + 42 * math.sin(th), 20, 5, 90 + 60 * k, 5))  # scutes tessellate
    els.append(teardrop(C, C, -90, 54, 86, 13))                   # head (up)
    els.append(circle(C, C - 78, 3))                             # eye-ish
    for k in range(4):
        els.append(teardrop(C, C, 45 + 90 * k, 54, 82, 12))      # four legs
    els.append(teardrop(C, C, 90, 54, 74, 7))                     # tail (down)
    return els


def snake():
    """Coiled snake — a spiral body with a head and flicking tongue."""
    els = [spiral(C, C, 8, 60, 3.0)]                              # coil, ends at right (C+60,C)
    ex, ey = C + 60, C                                            # spiral outer end
    els.append(teardrop(ex - 3, ey, 0, 2, 26, 12))              # head, overlaps the coil end
    els.append(circle(ex + 16, ey - 4, 2.5))                     # eye
    els.append(path([(ex + 24, ey), (ex + 34, ey - 5)]))         # forked tongue
    els.append(path([(ex + 24, ey), (ex + 34, ey + 5)]))
    return els


def giraffe():
    """Giraffe — long-necked side silhouette with spot patches."""
    outline = [
        (58, 40), (66, 34), (72, 40), (74, 58),           # head + ossicone side
        (82, 92), (92, 128), (150, 150), (168, 150),      # neck down to back
        (170, 176), (160, 176), (152, 156),               # back leg
        (128, 154), (120, 176), (110, 176), (104, 152),   # belly + front leg
        (86, 120), (74, 84), (66, 60), (58, 52),          # chest up the neck front
    ]
    els = [smooth(outline, closed=True, k=0.8)]
    els.append(circle(60, 32, 4))                         # ossicone knobs on the head
    els.append(circle(71, 32, 4))
    els.append(circle(66, 44, 2.5))                       # eye
    # spot patches — an overlapping chain down the neck, ends touching the silhouette
    for cx, cy in [(80, 76), (90, 96), (100, 116), (114, 132), (140, 140), (150, 118)]:
        els.append(circle(cx, cy, 10))
    return els


def penguin():
    """Penguin front-on — body, belly patch, flippers, feet, beak."""
    body = [(C, C - 74), (C + 36, C - 38), (C + 42, C + 22),
            (C + 22, C + 68), (C - 22, C + 68), (C - 42, C + 22), (C - 36, C - 38)]
    els = [smooth(body, closed=True)]
    belly = [(C, C - 34), (C + 26, C + 6), (C + 16, C + 60), (C - 16, C + 60), (C - 26, C + 6)]
    els.append(smooth(belly, closed=True))
    for sx in (-1, 1):
        els.append(circle(C + sx * 12, C - 48, 4))               # eyes
        els.append(teardrop(C + sx * 34, C + 4, -90 + sx * 108, 8, 46, 9))  # flippers (touch body)
        els.append(teardrop(C + sx * 13, C + 68, 90 - sx * 22, 4, 20, 8))   # feet
    els.append(teardrop(C, C - 42, 90, 2, 12, 6))                 # beak
    els.append(path([(C - 12, C - 48), (C + 12, C - 48)]))        # brow ties the eyes
    return els


def flamingo():
    """Flamingo — the iconic S-neck side silhouette on long legs."""
    els = [smooth([(118, 96), (152, 104), (152, 132), (118, 138), (100, 116)], closed=True)]  # body
    els.append(smooth([(120, 104), (104, 82), (124, 60), (114, 38), (128, 28)],
                      closed=False, k=1.1))                # long S-neck
    els.append(circle(133, 26, 7))                        # head
    els.append(circle(135, 24, 2))                        # eye
    els.append(path(spts([(139, 30), (150, 36), (145, 44)])))  # down-hooked beak
    els.append(teardrop(150, 122, 25, 4, 22, 8))          # tail tuft
    els.append(path([(126, 134), (122, 170), (132, 178)]))  # front leg, bent
    els.append(path([(140, 132), (143, 176)]))            # back leg
    return els


TILES = [
    ("lion", lion, "lion face with a mane of rays"),
    ("elephant", elephant, "elephant head-on — ears, trunk, tusks"),
    ("giraffe", giraffe, "long-necked giraffe silhouette with spots"),
    ("owl", owl, "owl face — great eyes, ear tufts, wings"),
    ("peacock", peacock, "peacock tail-fan of eye-spots"),
    ("butterfly", butterfly, "symmetric butterfly with wing spots"),
    ("turtle", turtle, "patterned turtle shell from above"),
    ("snake", snake, "coiled snake with head and tongue"),
    ("penguin", penguin, "front-on penguin"),
    ("flamingo", flamingo, "S-necked flamingo on long legs"),
]


if __name__ == "__main__":
    from PIL import Image, ImageDraw
    outdir = sys.argv[1] if len(sys.argv) > 1 else "."
    thumbs = []
    for name, fn, desc in TILES:
        els = [e for e in fn() if e]
        V.to_svg(els, os.path.join(outdir, f"{name}.svg"), f"clayline zoo tile: {name} — {desc}")
        im, lo, hi = V.render(els, os.path.join(outdir, f"{name}.png"))
        flag = "" if lo is not None and lo >= 1.0 and hi <= 199.0 else f"  ** BOUNDS {lo:.1f}..{hi:.1f}"
        print(f"{name:12s} {len(els):3d} elements{flag}")
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
