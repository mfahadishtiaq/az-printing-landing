#!/usr/bin/env python3
"""Build the web images for the client-design page from `../Client drop/`.

The drop is Awais Muhammad's 2026-10-04 "WEBSITE IMAGES" set (see
`../Client drop/00-EMAIL.md`). Originals stay untouched there; this script
writes sized, compressed copies into `images/client/`.

Needs Pillow, and psd-tools for the hero step:
    python3 -m venv /tmp/psdenv && /tmp/psdenv/bin/pip install psd-tools
    /tmp/psdenv/bin/python tools/prepare-client-images.py

Why the hero comes from the PSD and not from TOP BANNER.png: the PNG has the
headline baked into the pixels. The PSD keeps the headline ("Layer 11"), the
"we print / we design" list ("Layer 12") and "PREMIUM QUALITY" ("Layer 13") as
separate layers, so the collage can be rendered without them and the words set
as real HTML text that wraps on a phone and that search engines can read.
"""
import os, sys
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
DROP = os.path.join(os.path.dirname(SITE), "Client drop")
OUT = os.path.join(SITE, "images", "client")
os.makedirs(OUT, exist_ok=True)

# Product tiles: the drop's titled 1060x1308 tiles, keyed by the slug the page
# uses. The title band at the top of each is cropped off (the page sets the
# title as text); the picture below it is centre-cropped to a square.
TILES = {
    "business-cards": "business cards.png",
    "flyers": "flyers.png",
    "brochures": "brochures 1.png",
    "greeting-cards": "greeting cards 1.png",
    "posters": "posters1.png",
    "door-hangers": "door hangers 1.png",
    "rollup-banner": "rollup banner1.png",
    "round-stickers": "round stickers 1.png",
    "lawn-signs": "lawn signs 1.png",
    "letterhead": "letter head 1.png",
    "store-branding": "store branding 1.png",
    "spiral-binding": "spiral binding.png",
    "photocopy": "photocopy.png",
    "document-scan": "document scan.png",
}


def flat(im, bg=(255, 255, 255)):
    """Drop transparency onto a solid colour; JPEG has no alpha."""
    if im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info):
        im = im.convert("RGBA")
        base = Image.new("RGBA", im.size, bg + (255,))
        base.alpha_composite(im)
        return base.convert("RGB")
    return im.convert("RGB")


def save(im, name, widths, quality=82):
    for w in widths:
        c = im.copy()
        if c.width > w:
            c = c.resize((w, round(c.height * w / c.width)), Image.LANCZOS)
        p = os.path.join(OUT, f"{name}-{w}.jpg")
        c.save(p, "JPEG", quality=quality, optimize=True, progressive=True)
        print(f"{p[len(SITE)+1:]:48s} {c.width}x{c.height} {os.path.getsize(p)//1024} KB")


def content_top(im, start=130):
    """First row below the title band with real picture in it.

    Measured 2026-10-05: title text sits in rows ~48-128, the picture starts
    at 180-200. Scanning from 130 finds the picture's first row on every tile.
    """
    g = im.convert("L")
    w, h = g.size
    px = g.load()
    for y in range(start, h):
        dark = sum(1 for x in range(0, w, 4) if px[x, y] < 235)
        if dark > (w // 4) * 0.02:
            return y
    return start


def tiles():
    for slug, src in TILES.items():
        im = flat(Image.open(os.path.join(DROP, src)))
        top = content_top(im)
        w, h = im.size
        body = im.crop((0, top, w, h))
        side = min(body.width, body.height)
        x0 = (body.width - side) // 2
        y0 = (body.height - side) // 2
        sq = body.crop((x0, y0, x0 + side, y0 + side))
        save(sq, f"tile-{slug}", [800, 480])


def welcome():
    im = flat(Image.open(os.path.join(DROP, "delicious grill chicken.png")))
    save(im, "welcome", [900, 600])


def hero():
    try:
        from psd_tools import PSDImage
    except ImportError:
        print("psd-tools not installed; hero skipped (see docstring)")
        return
    psd = PSDImage.open(os.path.join(DROP, "TOP BANNER.psd"))
    group = next(l for l in psd if l.name == "Group 4")
    skip = {"Layer 11", "Layer 12", "Layer 13"}  # headline, list, PREMIUM QUALITY
    img = group.composite(layer_filter=lambda l: l.is_visible() and l.name not in skip)
    bx = group.bbox
    # The banner occupies page rows 178-1261; the group bleeds past the page edge.
    band = img.crop((0 - bx[0], 178 - bx[1], 1920 - bx[0], 1261 - bx[1]))
    band = flat(band)
    save(band, "hero-collage", [1920, 1280], quality=84)
    # Phone crop: the products only, the headline column (x < 330) left out.
    save(band.crop((330, 0, 1920, band.height)), "hero-collage-mobile", [900], quality=84)


def mark():
    """The site mark (04 - Brand/AI Logo.png, the owner's A/Z monogram) at
    header size. The mockup's header lockup uses the older circular badge,
    which the brand README retired on 2026-08-28; the current mark takes its
    place with the canonical wordmark set as text beside it."""
    im = Image.open(os.path.join(SITE, "images", "az-logo-master.png")).convert("RGBA")
    h = 240
    im = im.resize((round(im.width * h / im.height), h), Image.LANCZOS)
    p = os.path.join(OUT, "mark-240.png")
    im.save(p, "PNG", optimize=True)
    print(f"{p[len(SITE)+1:]:48s} {im.width}x{im.height} {os.path.getsize(p)//1024} KB")


if __name__ == "__main__":
    tiles()
    welcome()
    hero()
    mark()
