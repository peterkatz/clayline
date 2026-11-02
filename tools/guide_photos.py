"""Crop, colour-correct and shrink photographs of printed pieces for the guide.

Usage:
    python tools/guide_photos.py SOURCE_DIR guide/images/prints

SOURCE_DIR holds the camera files as N.png (N is the number in the table).
Every output is sRGB JPEG with no camera metadata, cropped to the frame the
page uses, gently white-balanced where the piece sat on a white bed, and
sharpened once after shrinking.

Each entry: source number, output name, aspect (w/h), focus box (normalised
x0,y0,x1,y1 the crop should contain, centred on it), long-edge pixels, white
balance strength (0 = leave the light as it was) and an optional list of
rectangles to patch over with bed from an offset.
"""
import io, os, sys
from PIL import Image, ImageCms, ImageDraw, ImageFilter, ImageOps

SRC, OUT = sys.argv[1], sys.argv[2]
SRGB = ImageCms.createProfile("sRGB")

PHOTOS = [
    # home cards (16:10)
    (19, "rosette-tile-printing",   1.6,  (0.02, 0.24, 1.00, 0.78), 1200, 0.6, []),
    (10, "ribs-and-spirals",        1.6,  (0.00, 0.05, 1.00, 0.95), 1200, 0.4, []),
    # home grid (square)
    (8,  "spiral-bowl-glazed",      1.0,  (0.14, 0.00, 0.92, 1.00),  900, 0.3, []),
    (3,  "spiral-star-bowl",        1.0,  (0.05, 0.38, 0.95, 0.88),  900, 0.0, []),
    (24, "pinwheel-blue",           1.0,  (0.12, 0.20, 0.66, 0.86),  900, 0.0, []),
    (23, "pulse-spiral-green",      1.0,  (0.05, 0.38, 0.58, 1.00),  900, 0.0, []),
    (17, "drape-tile-glazed",       1.0,  (0.10, 0.08, 0.92, 0.96),  900, 0.5, []),
    (28, "rosette-tile-glazed",     1.0,  (0.08, 0.12, 0.96, 0.74),  900, 0.3, []),
    # home closing figure (3:2)
    (7,  "seven-pieces",            1.5,  (0.00, 0.05, 1.00, 0.95), 1600, 0.4, []),
    # tiles page
    (21, "rosette-tile-greenware",  1.0,  (0.10, 0.15, 0.92, 0.70), 1000, 0.5, []),
    (38, "tile-flag",               1.6,  (0.00, 0.08, 1.00, 0.90), 1600, 0.5, []),
    (22, "endless-knot-draped",     1.0,  (0.08, 0.22, 0.92, 0.84), 1000, 0.5, []),
    # weave page
    (16, "spiral-vessel-greenware", 0.8,  (0.00, 0.05, 1.00, 0.99), 1000, 0.5, []),
    (30, "woven-vase-greenware",    0.8,  (0.10, 0.03, 0.90, 0.73), 1000, 0.5, []),
    (46, "twisted-bottle",          0.7,  (0.08, 0.04, 0.87, 0.89), 1000, 0.6, []),
    # printing page
    (43, "bottle-neck-printing",    0.8,  (0.00, 0.00, 1.00, 0.94), 1000, 0.6, []),
]

def to_srgb(im):
    icc = im.info.get("icc_profile")
    if icc:
        im = ImageCms.profileToProfile(im, ImageCms.ImageCmsProfile(io.BytesIO(icc)), SRGB, outputMode="RGB")
    return im.convert("RGB")

def crop_box(w, h, aspect, focus):
    fx0, fy0, fx1, fy1 = focus[0]*w, focus[1]*h, focus[2]*w, focus[3]*h
    cx, cy = (fx0+fx1)/2, (fy0+fy1)/2
    fw, fh = fx1-fx0, fy1-fy0
    # smallest box of the aspect that holds the focus
    cw = max(fw, fh*aspect); ch = cw/aspect
    # clip to the image, keeping the aspect
    if cw > w: cw = w; ch = cw/aspect
    if ch > h: ch = h; cw = ch*aspect
    x0 = min(max(cx-cw/2, 0), w-cw); y0 = min(max(cy-ch/2, 0), h-ch)
    return (int(x0), int(y0), int(x0+cw), int(y0+ch))

def white_balance(im, strength):
    if strength <= 0: return im
    small = im.resize((300, int(300*im.height/im.width)))
    px = list(small.get_flattened_data()) if hasattr(small, 'get_flattened_data') else list(small.getdata())
    bright = sorted(px, key=lambda p: sum(p), reverse=True)[: max(30, len(px)//100)]
    r = sum(p[0] for p in bright)/len(bright); g = sum(p[1] for p in bright)/len(bright); b = sum(p[2] for p in bright)/len(bright)
    m = (r+g+b)/3
    gains = [1 + strength*((m/c) - 1) for c in (r, g, b)]
    bands = [ch.point(lambda v, k=k: min(255, int(v*k+0.5))) for ch, k in zip(im.split(), gains)]
    return Image.merge("RGB", bands)

def patch(im, rects):
    for (x0, y0, x1, y1), (dx, dy) in rects:
        w, h = im.size
        box = (int(x0*w), int(y0*h), int(x1*w), int(y1*h))
        ox, oy = int(dx*w), int(dy*h)
        src = (box[0]+ox, box[1]+oy, box[2]+ox, box[3]+oy)
        tile = im.crop(src).filter(ImageFilter.GaussianBlur(1.5))
        bw, bh = tile.size
        mask = Image.new("L", (bw, bh), 0)
        inset = max(4, int(min(bw, bh)*0.12))
        ImageDraw.Draw(mask).rectangle([inset, inset, bw-inset, bh-inset], fill=255)
        mask = mask.filter(ImageFilter.GaussianBlur(inset*0.6))
        im.paste(tile, box, mask)
    return im

os.makedirs(OUT, exist_ok=True)
for num, name, aspect, focus, long_edge, wb, patches in PHOTOS:
    im = Image.open(f"{SRC}/{num}.png")
    im = ImageOps.exif_transpose(im)
    im = to_srgb(im)
    im = patch(im, patches)
    im = im.crop(crop_box(im.width, im.height, aspect, focus))
    im = white_balance(im, wb)
    im = ImageOps.autocontrast(im, cutoff=(0.2, 0.2), preserve_tone=True)
    if aspect >= 1: size = (long_edge, int(long_edge/aspect))
    else: size = (int(long_edge*aspect), long_edge)
    im = im.resize(size, Image.LANCZOS)
    im = im.filter(ImageFilter.UnsharpMask(radius=1.0, percent=45, threshold=2))
    path = f"{OUT}/{name}.jpg"
    im.save(path, "JPEG", quality=82, optimize=True, progressive=True, subsampling=1)
    chk = Image.open(path)
    assert not chk.getexif() and "icc_profile" not in chk.info, name
    print(f"{name:28s} {num:>3} {im.width}x{im.height} {os.path.getsize(path)//1024} KB")
