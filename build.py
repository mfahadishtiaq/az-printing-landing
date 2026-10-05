#!/usr/bin/env python3
"""AZ Printing & Signs site generator (client design, 2026-10-05).

    python3 build.py             # build every page + verify
    python3 build.py --check     # verify the files on disk only
    python3 build.py --confirm   # the owner confirm list (markdown)

Home is the client's mockup (Awais Muhammad, 2026-10-04), approved by Fahad
2026-10-05. Each product tile links to its own page, which lists the TYPES of
that product with a one-line explanation each; the client asked for this in
September ("business cards have multiple types, glossy, matte, etc.").

Every type line carries a source tag. `owner`/`client` are the owner's own
word; everything else prints on --confirm so one conversation with him
settles the lot before the site goes public.
"""
import html
import json
import os
import re
import sys
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))

SITE = {
    "name": "AZ Printing & Signs",
    "domain": "https://azprintingandsigns.ca/",
    "email": "azprint499@gmail.com",
    "phone_display": "905-796-1515",
    "phone_tel": "9057961515",
    "whatsapp": "https://wa.me/19057961515",
    "address": "499 Ray Lawson Blvd. Unit 24, Brampton, ON, L6Y 4E6",
    # Google's Maps URL API carrying the BUSINESS NAME: an address-only query
    # can land on the plaza rather than the unit.
    "maps": "https://www.google.com/maps/search/?api=1&query=AZ+Printing+and+Signs%2C+499+Ray+Lawson+Blvd+%2324%2C+Brampton%2C+ON+L6Y+4E6",
    "map_embed": "https://www.google.com/maps?q=AZ+Printing+and+Signs,+499+Ray+Lawson+Blvd+Unit+24,+Brampton,+ON+L6Y+4E6&output=embed",
    "hours": "Mon to Fri 10:30 to 7 · Sat 12 to 4 · Sun closed",
}

SOURCES = {
    "owner": "owner's services answers, R2 form 2026-08-23",
    "client": "client feedback relayed by Fahad 2026-09-13",
    "window": "the shop's own window vinyls (storefront photo 2026-08-27)",
    "signs": "Fahad's all-signs ruling 2026-08-27, provisional",
    "drop": "pictured in the designer's image set, 2026-10-04",
    "std": "industry-standard option, not yet confirmed by the owner",
}
CONFIRMED = {"owner", "client"}

# ---------------------------------------------------------------------------
# THE PRODUCTS, in the mockup's tile order. A product is: slug, name, intro,
# alt (for its picture), sets. A set is (title or None, items); an item is
# (name, explanation, "src+src"). Explanations are full sentences in plain
# English (rule 20): the trade word is kept, and explained inside the line.
# ---------------------------------------------------------------------------
PRODUCTS = [
    {"slug": "business-cards", "name": "Business Cards",
     "intro": "Printed on one or both sides at the standard 3.5 x 2 inch size. The finish decides how the card looks and feels in the hand.",
     "alt": "A black embossed business card held in a hand",
     "sets": [
         ("Finishes", [
             ("Matte", "A smooth card with no shine. Text stays easy to read under any light, and you can write on it.", "client"),
             ("Glossy", "A shiny coating that makes colours and photos look brighter and richer.", "client"),
             ("Soft Touch", "A velvety coating with a smooth, suede-like feel in the hand.", "window"),
             ("Spot UV", "A clear, glossy coating on selected areas, such as your logo, so they shine against a matte card.", "window"),
             ("Foil", "Metallic gold or silver foil pressed onto your logo or name so it catches the light.", "window"),
             ("Embossed", "Your logo or name raised out of the card so you can feel it under your thumb.", "drop"),
         ]),
         ("Options", [
             ("Single or Double Sided", "Print on the front only, or use the back for a map, a tagline or a second language.", "std"),
             ("Rounded Corners", "Corners trimmed to a soft curve instead of a sharp point.", "std"),
             ("Thick Stock", "A heavier card that feels more substantial in the hand.", "std"),
         ]),
     ]},

    {"slug": "flyers", "name": "Flyers",
     "intro": "Single sheets printed on one or both sides, for handing out, posting or mailing.",
     "alt": "A hand holding a printed spring sale flyer",
     "sets": [
         ("Sizes", [
             ("Letter, 8.5 x 11", "The standard page size, for menus, price lists and event flyers.", "std"),
             ("Half Letter, 5.5 x 8.5", "Half a page, easy to hand out and cheaper to print in quantity.", "std"),
             ("Postcard, 4 x 6", "A small flyer that fits a pocket or a mailbox.", "std"),
             ("Tabloid, 11 x 17", "A double-size sheet for posters, menus and notices.", "std"),
         ]),
         ("Paper and Printing", [
             ("Glossy", "A shiny finish that makes photos and colours stand out.", "std"),
             ("Matte", "A smooth, non-reflective finish that is easy to read.", "std"),
             ("Card Stock", "Thicker paper that holds up to handling and feels more substantial.", "std"),
             ("Single or Double Sided", "One side printed, or both, for example a menu on the front and an offer on the back.", "std"),
         ]),
     ]},

    {"slug": "brochures", "name": "Brochures",
     "intro": "Folded into panels, with room to explain your services in detail.",
     "alt": "A yellow folded brochure for a restaurant opening",
     "sets": [
         ("Folds", [
             ("Bi-Fold", "One fold down the middle, giving four panels, like a small booklet.", "owner+window"),
             ("Tri-Fold", "Two folds giving six panels, the familiar brochure that fits a rack or an envelope.", "owner+window"),
             ("Z-Fold", "Folded in a zigzag so the panels open out like an accordion.", "std"),
             ("Gate Fold", "The two outer panels fold in to meet in the middle and open like gates.", "std"),
         ]),
         ("Related", [
             ("Booklets & Catalogues", "Multi-page printed books, stapled or bound, for product ranges, programs and guides.", "owner+window"),
             ("Menus", "Takeout, dine-in and laminated menus for restaurants and cafés.", "owner+window"),
             ("Postcards", "Sturdy cards for mail campaigns, promotions and appointment reminders.", "owner+window"),
         ]),
     ]},

    {"slug": "greeting-cards", "name": "Greeting Cards",
     "intro": "Cards for holidays, celebrations and the thank-yous that follow.",
     "alt": "Vintage style Christmas greeting cards laid out together",
     "sets": [
         (None, [
             ("Folded Cards", "A card that opens, with your message printed inside.", "owner+window"),
             ("Flat Cards", "A single printed card, like a postcard, for short messages and announcements.", "owner+window"),
             ("Holiday Cards", "Cards for Christmas, Eid, Diwali, the New Year and other occasions, for family or for clients.", "std"),
             ("Thank You Cards", "Folded or flat cards for thank-yous and business greetings.", "owner+window"),
             ("Wedding Invitations", "Invitations for the wedding and each event around it, including shaadi, nikkah, mehndi and walima cards.", "owner"),
             ("Event Invitations", "Invitations for birthdays, engagements, anniversaries, religious events and community gatherings.", "owner"),
         ]),
     ]},

    {"slug": "posters", "name": "Posters",
     "intro": "Prints for windows, walls, events and displays, from small sizes up to large format.",
     "alt": "A summer event poster displayed in a shop window",
     "sets": [
         ("Sizes", [
             ("11 x 17", "A small poster for notice boards, counters and windows.", "std"),
             ("18 x 24", "A mid-size poster for shop windows and event displays.", "std"),
             ("24 x 36", "A full-size poster that reads from across a room.", "std"),
             ("Large Format", "Bigger than a standard poster, for walls, storefronts and events.", "owner"),
         ]),
         ("Finishes", [
             ("Glossy or Matte", "Shiny for photos and colour, or non-reflective for text under bright lights.", "std"),
             ("Laminated", "A clear protective layer so the poster holds up to handling and weather.", "owner+window"),
             ("Mounted on Foam Board", "The poster fixed to a light, rigid board so it stands or hangs flat.", "std"),
         ]),
     ]},

    {"slug": "door-hangers", "name": "Door Hangers",
     "intro": "Cut to hang on a door handle, for reaching every home on a street.",
     "alt": "A man placing a printed door hanger on a front door handle",
     "sets": [
         (None, [
             ("Standard, 4.25 x 11", "The usual door hanger size, with the hole cut to fit a door handle.", "std"),
             ("Single or Double Sided", "Your message on the front, or both sides, for example an offer and a menu.", "std"),
             ("Tear-Off Coupon", "A perforated strip at the bottom that the customer can tear off and keep.", "std"),
             ("Custom Shapes", "Cut to a shape of your own, such as a house, a leaf or a rounded tab.", "std"),
         ]),
     ]},

    {"slug": "rollup-banner", "name": "Rollup Banner",
     "intro": "A banner that rolls out of its own base and stands upright. Also called a pull-up, standee or retractable banner.",
     "alt": "A roll-up banner stand printed with a social media design",
     "sets": [
         ("Rollup Banners", [
             ("Standard, 33 x 80 inches", "The usual size for a trade show, a lobby or a shop entrance.", "std"),
             ("Double Sided", "Printed on both sides so it reads from either direction.", "std"),
             ("Replacement Graphic", "A new print for a stand you already own.", "std"),
         ]),
         ("Other Banners and Displays", [
             ("Vinyl Banners", "Durable printed vinyl with grommets, the metal rings along the edge, for hanging indoors or outside.", "signs+window"),
             ("Feather Flags", "Tall, curved flags on a pole that stay visible from the road and the parking lot.", "window"),
             ("Step-and-Repeat Backdrops", "Large backdrops with your logo repeated across them, for event photos and media walls.", "signs"),
         ]),
     ]},

    {"slug": "round-stickers", "name": "Round Stickers",
     "intro": "Printed stickers and labels for packaging, products, giveaways and events.",
     "alt": "A roll of round printed product stickers",
     "sets": [
         ("Types", [
             ("Round Stickers", "Circles in sizes from one inch up, for jars, bags, envelopes and giveaways.", "drop"),
             ("Roll Labels", "Stickers supplied on a roll, quick to peel and apply in quantity.", "drop"),
             ("Die-Cut Stickers", "Stickers cut around the outline of your design, in the shape you need.", "owner+window"),
             ("Sticker Sheets", "Several stickers printed on one sheet, easy to peel and hand out.", "std"),
             ("Product Labels", "Labels for jars, bottles, bags and boxes, printed with your logo and product details.", "owner"),
         ]),
         ("Materials", [
             ("Paper", "An everyday sticker for indoor use and short-term labelling.", "std"),
             ("Vinyl", "A waterproof sticker that holds up outdoors and on products that get wet.", "std"),
         ]),
     ]},

    {"slug": "lawn-signs", "name": "Lawn Signs",
     "intro": "Printed on coroplast, a lightweight corrugated plastic that holds up to rain and sun, for lawns and yards.",
     "alt": "Three printed lawn signs standing on a front lawn",
     "sets": [
         ("Types", [
             ("Lawn Signs", "A printed coroplast sign on a metal H-stake pushed into the ground.", "signs+window"),
             ("Real Estate Signs", "Realtor, for sale and open house signs that mark a listing and point buyers to the door.", "signs+window"),
             ("A-Frame Signs", "Two-sided sidewalk signs, also called sandwich boards, that fold flat at closing time.", "signs+window"),
             ("Welcome Signs", "Signs that greet guests at weddings, parties and community events.", "window"),
         ]),
         ("Options", [
             ("18 x 24 or 24 x 36", "The two common sizes: one reads from the sidewalk, the other from the road.", "std"),
             ("Single or Double Sided", "Printed on one face, or both so it reads from either direction.", "std"),
             ("H-Stakes", "The wire stakes that hold the sign in the ground, supplied with it.", "std"),
         ]),
     ]},

    {"slug": "letterhead", "name": "Letterhead",
     "intro": "Everyday business paperwork, printed with your logo and contact details.",
     "alt": "A printed company letterhead",
     "sets": [
         (None, [
             ("Letterheads", "Your logo and details on paper for letters, quotes, invoices and agreements.", "owner+window"),
             ("Envelopes", "Business envelopes printed with your logo and return address.", "owner"),
             ("NCR Forms & Invoice Books", "NCR (no carbon required) forms make a copy as you write, bound into books for invoices, receipts and work orders.", "owner+window"),
             ("Notepads", "Branded writing pads, glued along the top edge, for the office or for clients.", "owner"),
             ("Presentation Folders", "Printed folders with inside pockets that hold proposals, price lists and brochures.", "owner"),
             ("Custom Stamps", "Stamps carrying your company name, address, logo or signature.", "window"),
         ]),
     ]},

    {"slug": "store-branding", "name": "Store Branding",
     "intro": "Signs and graphics for the front of a business, made to be read from the street.",
     "alt": "A restaurant storefront with a fascia sign and window posters",
     "sets": [
         ("Storefront Signs", [
             ("Channel Letters", "Individual 3D letters mounted on the building, often lit from inside or behind so the name shows at night.", "signs+window"),
             ("Light Box Signs", "A sign cabinet with a printed face, lit from inside.", "signs+window"),
             ("Fascia Signs", "Sign panels for the fascia, the band above a shop's windows, and other parts of the building.", "signs"),
             ("Menu Boards", "Printed menu boards for behind the counter or outside the door.", "signs"),
         ]),
         ("Vinyl Graphics", [
             ("Window Graphics", "Printed or cut vinyl for shop windows, showing your name, hours, services or promotions.", "signs+window"),
             ("Frosted Vinyl", "A frosted glass effect for office windows and doors that adds privacy and still lets light through.", "signs"),
             ("Vehicle Decals & Wraps", "Your logo and phone number on a work vehicle, as decals, magnets or a full wrap.", "signs"),
             ("Sign Installation", "We install signs, wraps and window graphics.", "owner"),
         ]),
     ]},

    {"slug": "spiral-binding", "name": "Spiral Binding",
     "intro": "Reports, manuals and menus bound into a finished document, with a cover that protects it.",
     "alt": "A stack of spiral-bound documents",
     "sets": [
         ("Binding", [
             ("Spiral (Coil) Binding", "A plastic coil threaded through holes along the edge. The pages turn fully and lie flat.", "owner+window"),
             ("Cerlox (Comb) Binding", "A plastic comb with teeth that clip through the pages. Pages can be added or removed later.", "std"),
             ("Wire-O Binding", "A metal double-wire binding with a neat, professional look.", "std"),
             ("Stapled Booklets", "Pages folded and stapled along the spine, for programs, catalogues and short guides.", "std"),
         ]),
         ("Covers and Finishing", [
             ("Clear Front Cover", "A clear plastic sheet on the front so the title page shows through.", "std"),
             ("Card Back Cover", "A stiff card on the back so the document holds its shape.", "std"),
             ("Laminating", "A clear protective layer for menus, signs and certificates.", "owner+window"),
         ]),
     ]},

    {"slug": "photocopy", "name": "Photocopy",
     "intro": "Black and white or colour copies, and documents printed from your file.",
     "alt": "A hand lifting the lid of a photocopier",
     "sets": [
         (None, [
             ("Black and White Copies", "Everyday copies of documents, forms and handouts.", "owner+window"),
             ("Colour Copies", "Full-colour copies for flyers, photos and presentations.", "owner+window"),
             ("Double Sided", "Both sides of the page, to halve the paper.", "std"),
             ("Letter, Legal and Tabloid", "The three standard page sizes: 8.5 x 11, 8.5 x 14 and 11 x 17.", "std"),
             ("Print from Email or USB", "Send your file to us or bring it on a USB stick and we print it at the counter.", "std"),
         ]),
     ]},

    {"slug": "document-scan", "name": "Document Scan",
     "intro": "Paper documents scanned to a file, and faxes sent from the counter.",
     "alt": "A woman holding printed pages beside a scanner",
     "sets": [
         (None, [
             ("Scan to PDF", "Your pages scanned into one PDF file, ready to email or keep.", "owner+window"),
             ("Scan to Email or USB", "The scanned file sent to your email or saved to your USB stick.", "std"),
             ("Multi-Page Documents", "Contracts, applications and records scanned in order as one document.", "std"),
             ("Photo Scanning", "Prints scanned at high resolution so they can be reprinted or shared.", "std"),
             ("Fax", "Faxes sent from the counter.", "owner+window"),
         ]),
     ]},
]

# The home page shows the catalogue in three groups (Fahad 2026-10-05: the
# flat grid of fourteen "looks far too cluttered"). Names are the trade's.
GROUPS = [
    ("Print", "Cards, flyers, brochures and stationery, printed to order.",
     ["business-cards", "flyers", "brochures", "greeting-cards", "posters", "door-hangers", "letterhead"]),
    ("Signs, Displays & Stickers", "For the lawn, the window, the storefront and the event.",
     ["lawn-signs", "rollup-banner", "store-branding", "round-stickers"]),
    ("Counter Services", "Walk in with a file or a stack of paper; walk out with it done.",
     ["photocopy", "document-scan", "spiral-binding"]),
]

BANNED = ["—", "AZ Printing and Signs", "416-731-9229", "(416)", "AZ PRINT &", "Eamil",
          "printed at our", "printed here", "made or finished", "in-house"]

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def esc(s):
    return html.escape(s, quote=True)


def wa_link(text):
    return SITE["whatsapp"] + "?text=" + urllib.parse.quote(text)


def by_slug(slug):
    return next(p for p in PRODUCTS if p["slug"] == slug)


def tile_img(p, root, sizes, lazy=True):
    s = p["slug"]
    return (f'<img src="{root}images/client/tile-{s}-800.jpg" '
            f'srcset="{root}images/client/tile-{s}-480.jpg 480w, {root}images/client/tile-{s}-800.jpg 800w" '
            f'sizes="{sizes}" alt="{esc(p["alt"])}" width="800" height="800"'
            + (' loading="lazy"' if lazy else "") + '>')


# ---------------------------------------------------------------------------
# shared chrome
# ---------------------------------------------------------------------------

def head(root, title, description, extra="", schema=""):
    return f'''<!doctype html>
<html lang="en-CA">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<meta property="og:type" content="website">
<meta property="og:locale" content="en_CA">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta name="theme-color" content="#9f257d">
<script>if(!matchMedia('(prefers-reduced-motion: reduce)').matches&&!/[?&]motion=off\\b/.test(location.search)){{document.documentElement.classList.add('pre');setTimeout(function(){{document.documentElement.classList.remove('pre')}},3000)}}</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Merriweather:wght@900&family=Montserrat:wght@400;500;700;900&display=swap">
{extra}<link rel="stylesheet" href="{root}css/client.css">
<link rel="icon" href="{root}images/favicon-32.png" sizes="32x32">
<link rel="apple-touch-icon" href="{root}images/apple-touch-icon.png">
{schema}</head>
<body>
'''


def brand(root):
    home = root or "./"
    return (f'<a class="brand" href="{home}" aria-label="AZ Printing &amp; Signs, home">'
            f'<img src="{root}images/client/mark-240.png" alt="" width="253" height="240">'
            f'<span class="brand-word">AZ Printing<br>&amp; Signs</span></a>')


def header(root, current=""):
    def nav(href, label, key):
        cur = ' aria-current="page"' if key == current else ""
        return f'<a href="{href}"{cur}>{label}</a>'
    return f'''<a class="skip" href="#main">Skip to content</a>

<header class="head">
  <div class="wrap head-in">
    {brand(root)}
    <nav class="nav" aria-label="Site">
      {nav(root + "products/", "Products", "products")}
      {nav(root + "#about", "About", "about")}
      {nav(root + "#contact", "Contact", "contact")}
    </nav>
    <div class="head-contact">
      <a class="wa" href="{SITE["whatsapp"]}">WhatsApp {SITE["phone_display"]}</a>
      <a class="btn" href="tel:{SITE["phone_tel"]}"><span class="call-long">Call {SITE["phone_display"]}</span><span class="call-short">Call us</span></a>
    </div>
  </div>
</header>

<main id="main">
'''


def footer(root):
    links = "".join(f'<li><a href="{root}products/{p["slug"]}/">{esc(p["name"])}</a></li>' for p in PRODUCTS)
    return f'''
</main>

<footer class="foot">
  <div class="wrap foot-in">
    <div>
      {brand(root)}
      <div class="foot-text">
        <p>AZ Printing &amp; Signs is Canada’s choice for high-quality digital printing and commercial printing services, delivering superior print pieces to clients nationwide.</p>
        <p><a href="{SITE["maps"]}">{esc(SITE["address"])}</a></p>
        <p><a href="tel:{SITE["phone_tel"]}">{SITE["phone_display"]}</a> · <a href="{SITE["whatsapp"]}">WhatsApp</a></p>
        <p>{esc(SITE["hours"])}</p>
      </div>
    </div>
    <nav class="foot-nav" aria-label="Products">
      <h2 class="foot-h">Products</h2>
      <ul>{links}</ul>
    </nav>
    <!-- Facebook and Instagram icons sit top right here in the mockup. They go in once the owner's pages exist (brief: "owner WILL create"); a dead social link is worse than none. -->
  </div>
  <div class="wrap foot-base"><p>© 2026 AZ Printing &amp; Signs · Brampton, Ontario</p></div>
</footer>

<div class="phone-bar" aria-label="Contact options">
  <a href="tel:{SITE["phone_tel"]}">Call</a>
  <a href="{SITE["whatsapp"]}">WhatsApp</a>
  <a class="pb-main" href="{root}#contact">Message</a>
</div>
<script src="{root}js/vendor/gsap.min.js" defer></script>
<script src="{root}js/vendor/ScrollTrigger.min.js" defer></script>
<script src="{root}js/vendor/lenis.min.js" defer></script>
<script src="{root}js/motion.js" defer></script>
</body>
</html>
'''


def business_schema():
    return ('<script type="application/ld+json">{"@context":"https://schema.org","@type":"LocalBusiness",'
            '"name":"AZ Printing & Signs","url":"https://azprintingandsigns.ca/","telephone":"+1-905-796-1515",'
            '"email":"azprint499@gmail.com","address":{"@type":"PostalAddress","streetAddress":"499 Ray Lawson Blvd, Unit 24",'
            '"addressLocality":"Brampton","addressRegion":"ON","postalCode":"L6Y 4E6","addressCountry":"CA"},'
            '"openingHoursSpecification":[{"@type":"OpeningHoursSpecification","dayOfWeek":["Monday","Tuesday","Wednesday","Thursday","Friday"],"opens":"10:30","closes":"19:00"},'
            '{"@type":"OpeningHoursSpecification","dayOfWeek":"Saturday","opens":"12:00","closes":"16:00"}],'
            '"areaServed":["Brampton","Mississauga"],"knowsLanguage":["en","pa","ur","hi"]}</script>\n')


# ---------------------------------------------------------------------------
# home: the client's mockup, tiles now links
# ---------------------------------------------------------------------------

# What each hero cut-out IS and where it goes: the collage is a navigable
# showcase (Fahad 2026-10-05 night: "make the hero more interactive").
HERO_LINKS = {
    "menu": ("brochures", "Menus"),
    "business-cards": ("business-cards", "Business Cards"),
    "poster": ("posters", "Posters"),
    "rollup-banner": ("rollup-banner", "Rollup Banners"),
    "lawn-sign": ("lawn-signs", "A-Frame Signs"),
    "flyer": ("flyers", "Flyers & Brochures"),
    "group-1": ("round-stickers", "Stickers"),
    "h-stand": ("lawn-signs", "Lawn Signs"),
    "object": ("letterhead", "Notepads"),
}


def hero_stage(root):
    """The collage as positioned cut-outs (images/client/hero/layers.json,
    written by tools/prepare-client-images.py from the PSD). Bottom-to-top
    order; depth grows toward the front so the front moves most. Each is a
    link to its product page with a label that shows on hover or focus.
    Nesting, each layer owned by one thing: .hero-item (entrance + scroll,
    GSAP) > .hero-float (pointer parallax, GSAP) > .hero-lift (hover lift and
    tilt, CSS) > img (idle drift, GSAP)."""
    with open(os.path.join(HERE, "images", "client", "hero", "layers.json")) as f:
        m = json.load(f)
    W, H = m["stage"]
    n = len(m["layers"])
    out = []
    for i, L in enumerate(m["layers"]):
        depth = round(0.35 + 0.65 * i / max(n - 1, 1), 2)
        slug, label = HERO_LINKS[L["name"]]
        # a label hangs below its item unless the item sits at the stage's
        # bottom edge, where it would be clipped; then it goes above
        above = " above" if (L["y"] + L["h"]) / H > 0.9 else ""
        out.append(f'<a class="hero-item" href="{root}products/{slug}/" data-name="{L["name"]}" data-depth="{depth}" '
                   f'aria-label="{esc(label)}: see the types" '
                   f'style="--x:{L["x"]/W*100:.3f}%;--y:{L["y"]/H*100:.3f}%;--w:{L["w"]/W*100:.3f}%">'
                   f'<span class="hero-float"><span class="hero-lift">'
                   f'<img src="{root}images/client/hero/{L["name"]}.webp" alt="" width="{L["w"]}" height="{L["h"]}">'
                   f'</span></span><span class="hero-tag{above}" aria-hidden="true">{esc(label)}</span></a>')
    return "\n    ".join(out)


def words(text):
    return " ".join(f'<span class="w">{esc(w)}</span>' for w in text.split())


def first_sentence(text):
    return text.split(". ")[0].rstrip(".") + "."


def catalog_html(root):
    """Home: three titled groups of cards, each card a picture, the name, one
    plain sentence and the link to its types."""
    out = []
    for title, lede, slugs in GROUPS:
        cards = []
        for slug in slugs:
            p = by_slug(slug)
            cards.append(f'<li class="card" data-reveal><a href="{root}products/{slug}/">'
                         f'<span class="card-img">{tile_img(p, root, "(min-width: 1000px) 22vw, (min-width: 600px) 46vw, 92vw")}</span>'
                         f'<span class="card-body"><strong>{esc(p["name"])}</strong><span>{esc(first_sentence(p["intro"]))}</span>'
                         f'<em>See the types</em></span></a></li>')
        out.append(f'<div class="group"><div class="group-head"><h3>{esc(title)}</h3><p>{esc(lede)}</p></div>'
                   f'<ul class="cards">{"".join(cards)}</ul></div>')
    return "\n    ".join(out)


def tiles_html(root):
    out = []
    for p in PRODUCTS:
        out.append(f'<li class="tile" data-reveal><a href="{root}products/{p["slug"]}/"><h3>{esc(p["name"])}</h3>'
                   f'{tile_img(p, root, "(min-width: 760px) 30vw, 46vw")}'
                   f'<span class="tile-more">See the types</span></a></li>')
    return "\n      ".join(out)


def home():
    root = ""
    title = "AZ Printing & Signs | Printing, signs and design in Brampton"
    desc = ("Printing, signs, graphic design and branding in Brampton: business cards, flyers, lawn signs, "
            "banners, stickers, copying, scanning and binding. Call 905-796-1515.")
    extra = '<link rel="preload" as="image" href="images/client/hero-ground-1920.jpg" media="(min-width: 900px)">\n'
    h = head(root, title, desc, extra, business_schema()) + header(root, "home")
    h += f'''
<section class="hero" aria-labelledby="hero-h">
  <div class="hero-text">
    <h1 id="hero-h">{words("Your business deserves to be seen")}</h1>
    <ul class="hero-list">
      <li>We<br>print</li>
      <li>We<br>design</li>
      <li>We build<br>brands</li>
    </ul>
  </div>
  <div class="hero-view"><img class="hero-ground" src="images/client/hero-ground-1920.jpg" srcset="images/client/hero-ground-1280.jpg 1280w, images/client/hero-ground-1920.jpg 1920w" sizes="100vw" alt="" width="1920" height="1083" fetchpriority="high"><div class="hero-stage" aria-label="Printed pieces side by side, each a link to its product: a menu, business cards, flyers, a roll-up banner, a poster, a lawn sign, an A-frame sign, stickers and a notepad">
    {hero_stage(root)}
  </div></div>
  <p class="hero-quality">Premium quality</p>
</section>

<section class="slogan" aria-labelledby="slogan-h">
  <div class="wrap slogan-in">
    <h2 id="slogan-h"><span class="line" data-reveal>we commit</span><span class="line" data-reveal>we deliver</span></h2>
    <div class="slogan-side" data-reveal>
      <p>Walk in, call or WhatsApp. English, Urdu, Hindi and Punjabi spoken at the counter.</p>
      <p class="slogan-ctas"><a class="btn btn-white" href="#contact">Get a quote</a><a class="slogan-call" href="tel:{SITE["phone_tel"]}">Call {SITE["phone_display"]}</a></p>
    </div>
  </div>
</section>

<section class="welcome" id="about" aria-labelledby="welcome-h">
  <div class="wrap welcome-in">
    <div class="welcome-text">
      <h2 id="welcome-h" data-reveal>Welcome to Brampton<br>AZ Printing &amp; Signs</h2>
      <p data-reveal>AZ PRINTING &amp; SIGNS is your one-stop destination for professional printing, signage, graphic design, and branding services in Brampton.</p>
      <p data-reveal>Conveniently located at 499 Ray Lawson Blvd, we offer digital printing, Xerox promotional printing, photocopying (Photo Stat), scanning, spiral binding, and custom signage, including window graphics.</p>
      <p data-reveal>Our qualified designer also provides logo design, brand identity, complete rebranding, and marketing design services to help businesses build a professional and consistent image.</p>
      <p data-reveal>From everyday printing to complete branding solutions, AZ PRINTING &amp; SIGNS is here to bring your ideas to life with quality, creativity, and reliable service.<br><a class="contact-link" href="#contact">Contact us</a> today to learn more about how we can help you.</p>
    </div>
    <figure class="welcome-photo" data-reveal><img src="images/client/storefront-1200.jpg" srcset="images/client/storefront-800.jpg 800w, images/client/storefront-1200.jpg 1200w" sizes="(min-width: 760px) 44vw, 92vw" alt="The AZ Printing &amp; Signs storefront at 499 Ray Lawson Blvd, Brampton: the sign, the phone number and the window listings" width="1200" height="800" loading="lazy"></figure>
  </div>
</section>

<section class="catalog" id="products" aria-labelledby="products-h">
  <div class="wrap">
    <div class="catalog-head" data-reveal>
      <h2 id="products-h">What we do</h2>
      <p>Fourteen products and services. Choose one to see its types, sizes and finishes, each explained in plain words.</p>
    </div>
    {catalog_html(root)}
  </div>
</section>

{contact_html()}
'''
    return h + footer(root)


def contact_html():
    return f'''<section class="contact" id="contact" aria-labelledby="contact-h">
  <div class="wrap">
    <h2 id="contact-h" data-reveal>Send us a message</h2>
    <div class="contact-in">
      <form class="contact-form" data-reveal action="https://formsubmit.co/{SITE["email"]}" method="POST">
        <input type="hidden" name="_subject" value="Website message from azprintingandsigns.ca">
        <input type="hidden" name="_template" value="table">
        <input type="hidden" name="_captcha" value="true">
        <input type="hidden" name="_next" value="{SITE["domain"]}?sent=1#contact">
        <input class="hp" type="text" name="_honey" tabindex="-1" autocomplete="off" aria-hidden="true">
        <div class="form-row">
          <label class="form-field"><span>Name</span><input type="text" name="name" required autocomplete="name"></label>
          <label class="form-field"><span>Email</span><input type="email" name="email" required autocomplete="email"></label>
        </div>
        <div class="form-row">
          <label class="form-field"><span>Phone Number</span><input type="tel" name="phone" autocomplete="tel"></label>
          <label class="form-field"><span>Company</span><input type="text" name="company" autocomplete="organization"></label>
        </div>
        <label class="form-field"><span>Comment or Message</span><textarea name="message" required></textarea></label>
        <div class="form-actions">
          <button class="btn" type="submit">Send message</button>
          <p class="alt">Or message us on <a href="{SITE["whatsapp"]}">WhatsApp</a>, or call <a href="tel:{SITE["phone_tel"]}">{SITE["phone_display"]}</a>.</p>
        </div>
        <p class="form-sent" id="form-sent" role="status">Thank you. Your message has been sent and we will get back to you soon.</p>
      </form>
      <figure class="map" data-reveal><iframe title="Map showing AZ Printing &amp; Signs at 499 Ray Lawson Blvd, Brampton" src="{esc(SITE["map_embed"])}" loading="lazy" referrerpolicy="no-referrer-when-downgrade" allowfullscreen></iframe></figure>
    </div>
  </div>
</section>'''


# ---------------------------------------------------------------------------
# products index + one page per product
# ---------------------------------------------------------------------------

def products_index():
    root = "../"
    title = "Products | AZ Printing & Signs, Brampton"
    desc = "Every product and service at AZ Printing & Signs in Brampton, each with its types explained. Call 905-796-1515 for a price."
    h = head(root, title, desc) + header(root, "products")
    h += f'''
<section class="page-head">
  <div class="wrap">
    <nav class="crumbs" aria-label="Breadcrumb"><a href="{root}">Home</a> <span>/</span> <span aria-current="page">Products</span></nav>
    <h1>Products and services</h1>
    <p class="lede">Choose a product to see its types, sizes and finishes, each explained in plain words. For a price, call <a href="tel:{SITE["phone_tel"]}">{SITE["phone_display"]}</a> or message us on <a href="{SITE["whatsapp"]}">WhatsApp</a>.</p>
  </div>
</section>
<section class="products" aria-label="All products">
  <div class="wrap">
    <ul class="tiles">
      {tiles_html(root)}
    </ul>
  </div>
</section>
'''
    return h + footer(root)


def product_page(p):
    root = "../../"
    name = p["name"]
    title = f"{name} in Brampton | AZ Printing & Signs"
    first = p["sets"][0][1][0][0]
    desc = f"{name} at AZ Printing & Signs, Brampton: {p['intro']} Types include {first.lower()} and more. Call 905-796-1515."
    ask = wa_link(f"Hello, I would like a price for {name.lower()}.")
    schema = ('<script type="application/ld+json">{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":['
              '{"@type":"ListItem","position":1,"name":"Home","item":"https://azprintingandsigns.ca/"},'
              '{"@type":"ListItem","position":2,"name":"Products","item":"https://azprintingandsigns.ca/products/"},'
              f'{{"@type":"ListItem","position":3,"name":"{esc(name)}","item":"https://azprintingandsigns.ca/products/{p["slug"]}/"}}]}}</script>\n')
    sets = []
    for stitle, items in p["sets"]:
        dl = "".join(f'<div class="ty"><dt>{esc(n)}</dt><dd>{esc(x)}</dd></div>' for n, x, _ in items)
        sets.append((f'<h3 class="set-h">{esc(stitle)}</h3>' if stitle else "") + f'<dl class="types">{dl}</dl>')
    others = "".join(
        f'<li><a href="{root}products/{o["slug"]}/">{tile_img(o, root, "(min-width: 760px) 14vw, 30vw")}<span>{esc(o["name"])}</span></a></li>'
        for o in PRODUCTS if o["slug"] != p["slug"])
    count = sum(len(items) for _, items in p["sets"])
    h = head(root, title, desc, "", schema) + header(root, "products")
    h += f'''
<section class="page-head">
  <div class="wrap">
    <nav class="crumbs" aria-label="Breadcrumb"><a href="{root}">Home</a> <span>/</span> <a href="{root}products/">Products</a> <span>/</span> <span aria-current="page">{esc(name)}</span></nav>
    <div class="product-top">
      <div class="product-text">
        <h1>{esc(name)}</h1>
        <p class="lede">{esc(p["intro"])}</p>
        <p class="product-ctas"><a class="btn" href="{ask}">Get a price on WhatsApp</a><a class="text-link" href="tel:{SITE["phone_tel"]}">Or call {SITE["phone_display"]}</a></p>
      </div>
      <figure class="product-photo">{tile_img(p, root, "(min-width: 900px) 38vw, 92vw", lazy=False)}</figure>
    </div>
  </div>
</section>

<section class="product-types" aria-labelledby="types-h">
  <div class="wrap">
    <h2 id="types-h">Types of {esc(name.lower())}</h2>
    <p class="types-note">{count} options, each explained. Not sure which you need? Tell us what it is for and we will suggest one.</p>
    {"".join(sets)}
  </div>
</section>

<section class="product-ask">
  <div class="wrap product-ask-in">
    <h2>Ready for a price?</h2>
    <p>Send your file, or tell us what you have in mind, and we will come back with a quote.</p>
    <p class="product-ctas"><a class="btn" href="{ask}">WhatsApp us</a><a class="btn btn-line" href="tel:{SITE["phone_tel"]}">Call {SITE["phone_display"]}</a><a class="text-link" href="{root}#contact">Or send a message</a></p>
  </div>
</section>

<section class="others" aria-labelledby="others-h">
  <div class="wrap">
    <h2 id="others-h">Other products</h2>
    <ul class="others-list">{others}</ul>
  </div>
</section>
'''
    return h + footer(root)


# ---------------------------------------------------------------------------
# files, verify, confirm
# ---------------------------------------------------------------------------

def outputs():
    yield "index.html", home()
    yield "products/index.html", products_index()
    for p in PRODUCTS:
        yield f"products/{p['slug']}/index.html", product_page(p)


def sitemap():
    urls = [SITE["domain"], SITE["domain"] + "products/"] + [SITE["domain"] + f"products/{p['slug']}/" for p in PRODUCTS]
    body = "".join(f"  <url><loc>{u}</loc></url>\n" for u in urls)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{body}</urlset>\n'


def fail(msg):
    print("VERIFY FAILED:", msg)
    sys.exit(1)


def verify():
    slugs = [p["slug"] for p in PRODUCTS]
    if len(set(slugs)) != len(slugs):
        fail("duplicate product slug")
    names = []
    for p in PRODUCTS:
        if not os.path.exists(os.path.join(HERE, "images", "client", f"tile-{p['slug']}-800.jpg")):
            fail(f"{p['slug']}: tile image missing")
        for stitle, items in p["sets"]:
            if len(p["sets"]) > 1 and not stitle:
                fail(f"{p['slug']}: a set without a title in a multi-set product")
            for n, x, src in items:
                names.append((p["slug"], n))
                for s in src.split("+"):
                    if s not in SOURCES:
                        fail(f"{p['slug']} / {n}: unknown source tag {src}")
                if not x.endswith(".") or len(x) > 160:
                    fail(f"{p['slug']} / {n}: explanation must be a sentence under 160 chars")
    for path, h in outputs():
        text = re.sub(r"<[^>]+>", " ", h)
        for b in BANNED:
            if b in text:
                fail(f"{path}: banned text {b!r}")
        d = os.path.dirname(os.path.join(HERE, path))
        for m in re.finditer(r'(?:src|href)="([^"#?]+)', h):
            u = m.group(1)
            if u.startswith(("http", "tel:", "mailto:")):
                continue
            target = os.path.normpath(os.path.join(d, u))
            if u.endswith("/"):
                target = os.path.join(target, "index.html")
            if not os.path.exists(target):
                fail(f"{path}: link to missing file {u}")
        for m in re.finditer(r'srcset="([^"]+)"', h):
            for part in m.group(1).split(","):
                f = part.strip().split(" ")[0]
                if not os.path.exists(os.path.normpath(os.path.join(d, f))):
                    fail(f"{path}: srcset names missing file {f}")
    print(f"verify ok: {len(PRODUCTS)} products, {len(names)} type lines, {2 + len(PRODUCTS)} pages")


def confirm_list():
    out = ["# AZ Printing & Signs, owner confirm list (site types)", "",
           "*Generated by `07 - Landing Site/build.py --confirm`. Every type on the site that is not yet the owner's own word, grouped by product. Tick to confirm, strike to remove.*", ""]
    for p in PRODUCTS:
        rows = [(n, src) for _, items in p["sets"] for n, _, src in items
                if not set(src.split("+")) & CONFIRMED]
        if not rows:
            continue
        out.append(f"## {p['name']}")
        for n, src in rows:
            why = "; ".join(SOURCES[s] for s in src.split("+"))
            out.append(f"- [ ] **{n}** ({why})")
        out.append("")
    return "\n".join(out)


def vendor():
    """js/vendor/ is copied from node_modules at build so the site stays
    self-hosted. `npm install` first (gsap, lenis; node_modules is ignored)."""
    import shutil
    src = os.path.join(HERE, "node_modules")
    dst = os.path.join(HERE, "js", "vendor")
    files = [("gsap/dist/gsap.min.js", "gsap.min.js"), ("gsap/dist/ScrollTrigger.min.js", "ScrollTrigger.min.js"),
             ("lenis/dist/lenis.min.js", "lenis.min.js")]
    if not os.path.isdir(src):
        for _, name in files:
            if not os.path.exists(os.path.join(dst, name)):
                fail(f"js/vendor/{name} missing and node_modules absent: run npm install")
        return
    os.makedirs(dst, exist_ok=True)
    for rel, name in files:
        shutil.copyfile(os.path.join(src, rel), os.path.join(dst, name))


def build():
    vendor()
    for path, h in outputs():
        full = os.path.join(HERE, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as f:
            f.write(h)
    with open(os.path.join(HERE, "sitemap.xml"), "w") as f:
        f.write(sitemap())
    with open(os.path.join(HERE, "robots.txt"), "w") as f:
        f.write(f"User-agent: *\nAllow: /\nSitemap: {SITE['domain']}sitemap.xml\n")
    verify()


if __name__ == "__main__":
    if "--confirm" in sys.argv:
        print(confirm_list())
    elif "--check" in sys.argv:
        verify()
    else:
        build()
