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
import os, re, sys
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


def storefront():
    """The shop's own front (04 - Brand, 2026-08-27 photo, 1600x1200): the
    fascia sign, the phone plate and the window listings. Cropped to the shop
    itself (cars and sidewalk off), 4:3. Fahad 2026-10-05: the Welcome section
    carries this, not the designer's stock window poster."""
    src = os.path.join(os.path.dirname(SITE), "04 - Brand", "WhatsApp Image 2026-08-27 at 5.19.00 PM.jpeg")
    im = Image.open(src).convert("RGB")
    W, H = im.size  # 1600x1200
    # crop measured on the 1000x750 preview (x 160-985, y 180-730) and
    # scaled by 1.6: the fascia sign, the phone plate, the three windows and
    # the door, 3:2.
    im = im.crop((256, 290, 1576, 1170))
    save(im, "storefront", [1200, 800], quality=84)


if __name__ == "__main__":
    tiles()
    welcome()
    mark()
    hero_layers()   # hero() still exists for the flat composite; the page uses the layers
    hero_ground_layers()
    storefront()


def hero_layers():
    """Each product in the hero collage as its own transparent cut-out, plus
    the gradient ground, so the page can animate them in one by one. Writes
    images/client/hero/*.webp and layers.json (name, bbox in banner pixels,
    bottom-to-top order), which build.py turns into positioned markup."""
    import json
    try:
        from psd_tools import PSDImage
    except ImportError:
        print("psd-tools not installed; hero layers skipped")
        return
    out = os.path.join(OUT, "hero")
    os.makedirs(out, exist_ok=True)
    psd = PSDImage.open(os.path.join(DROP, "TOP BANNER.psd"))
    group = next(l for l in psd if l.name == "Group 4")
    TEXT = {"Layer 11", "Layer 12", "Layer 13"}
    bx = group.bbox
    top = 178  # banner's first row on the page

    def band(img):
        return img.crop((0 - bx[0], top - bx[1], 1920 - bx[0], 1261 - bx[1]))

    # Ground: everything in the group that is not a product and not text.
    products = []
    for child in group:
        if child.name in TEXT:
            continue
        if child.name == "Group 2":
            products.extend(list(child))
        elif child.name in ("menu", "Business Cards"):
            products.append(child)
    product_names = {id(p) for p in products}

    def is_ground(l):
        # a layer is ground if no ancestor is one of the product layers
        a = l
        while a is not None and a is not psd:
            if id(a) in product_names or a.name in TEXT:
                return False
            a = a.parent
        return True

    ground = group.composite(layer_filter=lambda l: l.is_visible() and is_ground(l))
    ground = flat(band(ground))
    save(ground, "hero-ground", [1920, 1280], quality=84)

    manifest = []
    for i, p in enumerate(products):
        name = re.sub(r"[^a-z0-9]+", "-", p.name.lower()).strip("-") or f"layer-{i}"
        img = p.composite()
        l, t, r, b = p.bbox
        # clip to the banner
        cl, ct, cr, cb = max(l, 0), max(t, top), min(r, 1920), min(b, 1261)
        img = img.crop((cl - l, ct - t, cr - l, cb - t))
        path = os.path.join(out, f"{name}.webp")
        img.save(path, "WEBP", quality=86, method=6)
        manifest.append({"name": name, "x": cl, "y": ct - top, "w": cr - cl, "h": cb - ct})
        print(f"{path[len(SITE)+1:]:48s} {img.width}x{img.height} {os.path.getsize(path)//1024} KB")
    with open(os.path.join(out, "layers.json"), "w") as f:
        json.dump({"stage": [1920, 1083], "layers": manifest}, f, indent=1)


def hero_ground_layers():
    """The ground split in two (Fahad 2026-10-05: products still, background
    moving): hero-base = the flat gradient (the 'Vector Smart Object'),
    hero/swirl.webp = 'Layer 10', the looping ribbon at its 71% opacity, with
    alpha, so the page can drift it over the gradient."""
    from psd_tools import PSDImage
    psd = PSDImage.open(os.path.join(DROP, "TOP BANNER.psd"))
    group = next(l for l in psd if l.name == "Group 4")
    bx = group.bbox
    top = 178

    def band(img):
        return img.crop((0 - bx[0], top - bx[1], 1920 - bx[0], 1261 - bx[1]))

    base = group.composite(layer_filter=lambda l: l.is_visible() and (l.name == "Vector Smart Object" or l is group))
    save(flat(band(base)), "hero-base", [1920, 1280], quality=84)
    swirl = group.composite(layer_filter=lambda l: l.is_visible() and (l.name == "Layer 10" or l is group))
    swirl = band(swirl)
    p = os.path.join(OUT, "hero", "swirl.webp")
    swirl.save(p, "WEBP", quality=84, method=6)
    print(f"{p[len(SITE)+1:]:48s} {swirl.width}x{swirl.height} {os.path.getsize(p)//1024} KB")
