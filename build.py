#!/usr/bin/env python3
"""AZ Printing & Signs site generator (client design, 2026-10-05).

    python3 build.py             # build the page + verify
    python3 build.py --check     # verify the files on disk only
    python3 build.py --confirm   # the owner confirm list (markdown)

Home is the client's mockup (Awais Muhammad, 2026-10-04), approved by Fahad
2026-10-05. ONE PAGE ONLY (Fahad 2026-10-06: "Remove separate product pages,
this will only be a landing page"): every product card, hero cut-out and
industry card opens the quote form (#contact). The fourteen product pages and
the products index are gone (restore: git tag pre-landing-only-2026-10-06).
PRODUCTS still holds every type: it feeds --confirm, the SHORT lines and the
owner's types questionnaire.

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

# One line per product for the mega menu and the catalogue cards. Each is a
# summary of that product's own type list below, never a new claim.
SHORT = {
    "business-cards": "Matte, glossy, foil and more",
    "flyers": "Every size, one or both sides",
    "brochures": "Bi-fold, tri-fold, booklets, menus",
    "greeting-cards": "Holiday, thank-you, invitations",
    "posters": "Small sizes to large format",
    "door-hangers": "Reach every home on a street",
    "letterhead": "Letterheads, envelopes, NCR forms",
    "lawn-signs": "Lawn, real estate and A-frame signs",
    "rollup-banner": "Roll-up, vinyl banners and flags",
    "store-branding": "Storefront signs and window graphics",
    "round-stickers": "Stickers and product labels",
    "photocopy": "Black and white or colour",
    "document-scan": "Scan to PDF, email or USB",
    "spiral-binding": "Coil, comb and wire binding",
}

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

# Two home sections carried over from the shop build (`05 - Site` home, Fahad
# 2026-10-06: "add two sections from the original site"): "For your event /
# For your business" and "Industries we serve". The words are that build's
# approved copy, unchanged (an industry's line is the first sentence of its
# approved intro). The photos are the same files, stock samples, restored from
# tag pre-client-design-2026-10-05 into images/tiles/. This site has no events,
# industries or business-accounts page, so the doors ask for a quote and each
# industry opens the product it orders most (the last field; a cheap swap).
DOORS = [
    ("door-event", "The day you're planning", "For your event",
     "Choose invitations, welcome signs and banners for weddings, birthdays and community events. "
     "Visit the shop to compare materials and samples in person.",
     "Ask about event printing"),
    ("door-business", "The name you're building", "For your business",
     "Order business cards, flyers, apparel and signs from the same counter as your business grows.",
     "Ask about business printing"),
]
INDUSTRIES = [
    ("ind-real-estate", "Real estate",
     "The listing goes live Thursday and the sign has to be on the lawn first.", "lawn-signs"),
    ("ind-restaurants", "Restaurants",
     "A menu gets handled more than anything else we print.", "brochures"),
    ("ind-offices", "Professional services",
     "The folder that leaves the meeting, the letterhead under the agreement.", "letterhead"),
    ("ind-construction", "Construction & trades",
     "The site sign, the truck door, the invoice book.", "store-branding"),
    ("ind-community", "Community & religious organizations",
     "Banner up Friday, programs ready Sunday.", "rollup-banner"),
]

# The two coloured bands between the white sections (Fahad 2026-10-06: "a gap
# between page headings and the banners ... with a different colour, show
# process in one and a catchphrase in another"). Band 1 = HOW IT WORKS, band 2 =
# the client's catchphrase. Words: owner-confirmed facts only; step 3 is on the
# owner list (PAGE_FACTS). BAND_PRESETS are colour pairings; the FIRST loads,
# and js/site.js offers the rest on a localhost-only switch. Before go-live, cut
# to the one he keeps.
# Made COMPACT 2026-10-06 (Fahad: "make that smaller, just logos with small
# copy"): icon + title + a few words; no cards, numbers, intro or buttons.
STEPS = [
    ("chat", "Tell us what you need", "Walk in, call or WhatsApp."),
    ("pen", "We design it", "Or send us your file."),
    ("check", "You approve it", "Before anything is printed."),
    ("bag", "Pick up or delivery", "Brampton and Mississauga."),
]
STEP_ICON = {
    "chat": '<path d="M8 10h32v22H20l-8 7v-7H8z"/><path d="M15 18h18M15 24h12"/>',
    "pen": '<path d="M30 8l10 10-20 20H10V28z"/><path d="M26 12l10 10"/>',
    "check": '<rect x="9" y="7" width="30" height="34" rx="3"/><path d="M17 25l5 5 10-11"/>',
    "bag": '<path d="M10 16h28l-2 24H12z"/><path d="M18 16v-3a6 6 0 0 1 12 0v3"/>',
}
# 2026-10-06 later: band 2 is now the swatch tiles (Fahad picked concept 6a on
# the Claude Design canvas "We Commit Banner Concepts"), which carry their own
# colours, so the presets now colour band 1 (How it works) only.
BAND_PRESETS = ("white",)  # print2go pass: a plain white feature row under the hero (was cream / black / grey)
# Background of the colour-tile band (Fahad 2026-10-06: stone "needs to pop
# more"). First loads; the rest on a localhost switch until he settles it.
PROMISE_BGS = ("charcoal", "deepred", "stone")
SWATCHES = [  # (verb, label, colour, ink); the client's hero line + slogan,
    # in the BRAND PALETTE since 2026-10-06 (AZ Brand Colours.pdf): the hexes on
    # the tiles are the brand's own. Amber takes dark ink (white fails on it).
    ("print", "PRINT", "#A01D20", "#ffffff"),
    ("design", "DESIGN", "#FFA347", "#1a1a1a"),
    ("commit", "COMMIT", "#B37B33", "#ffffff"),
    ("deliver", "DELIVER", "#000000", "#ffffff"),
]

# Facts on the home page, outside the product types, that are not yet the
# owner's word. They print on --confirm under the types.
PAGE_FACTS = [
    ("How it works", "Customers see and approve the design before anything is printed",
     "brief follow-up item 3, never answered by the owner"),
    ("For your event", "Customers can visit the shop to compare materials and samples in person",
     "shop-build copy approved 2026-09-09, no owner source"),
    ("Doors and industries", "The seven photos are stock samples (one shows a made-up 'Briova' office, "
     "one a made-up wedding sign); swap for the shop's own work when he has it",
     "restored from the shop build 2026-10-06"),
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
<html lang="en-CA" data-bands="{BAND_PRESETS[0]}" data-bands-presets="{" ".join(BAND_PRESETS)}" data-promise="{PROMISE_BGS[0]}" data-promise-presets="{" ".join(PROMISE_BGS)}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<meta property="og:type" content="website">
<meta property="og:locale" content="en_CA">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta name="theme-color" content="#a01d20">
<script>if(!matchMedia('(prefers-reduced-motion: reduce)').matches&&!/[?&]motion=off\\b/.test(location.search)){{document.documentElement.classList.add('pre');setTimeout(function(){{document.documentElement.classList.remove('pre')}},3000)}}</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@1,500&family=Merriweather:wght@900&family=Montserrat:wght@400..900&display=swap">
{extra}<link rel="stylesheet" href="{root}css/client.css">
<link rel="icon" href="{root}images/az-mark.svg" type="image/svg+xml">
<link rel="icon" href="{root}images/favicon-32.png" sizes="32x32">
<link rel="apple-touch-icon" href="{root}images/apple-touch-icon.png">
{schema}</head>
<body>
'''


# THE MARK (Fahad 2026-10-06): images/az-mark.svg, a vector redrawn from the
# shop's own channel-letter sign (photo, perspective-corrected, equal strokes),
# in the lit sign's colours. The earlier AI Logo.png render was WRONG (split Z,
# misplaced A) and is retired. Source + build script: ../04 - Brand/.
def brand(root):
    home = root or "./"
    return (f'<a class="brand" href="{home}" aria-label="AZ Printing &amp; Signs, home">'
            f'<img src="{root}images/az-mark.svg" alt="" width="47" height="48">'
            f'<span class="brand-word">AZ Printing<br>&amp; Signs</span></a>')


def vf(label):
    """Variable-font hover (Fahad 2026-10-06, from a React "VariableFontHover"
    nav he pasted, rebuilt in CSS): each letter runs 'wght' 400 -> 700 with a
    30ms stagger outward from the centre. A hidden bold copy sits in the same
    grid cell so the word never changes width and the nav never shifts."""
    mid = (len(label) - 1) / 2
    letters = "".join(f'<span style="--d:{abs(i - mid):.1f}">{esc(ch)}</span>' for i, ch in enumerate(label))
    return (f'<span class="vf" aria-hidden="true"><span class="vf-ghost">{esc(label)}</span>'
            f'<span class="vf-l">{letters}</span></span>')


def header(root, current=""):
    """Studio nav pattern (ZEF, 2026-09): lockup, Products / About / Contact
    as in-page links (the mega menu went with the product pages, 2026-10-06),
    Call + Get a quote on the right, a burger sheet on phones.
    Above it a utility strip that scrolls away; the main bar is sticky."""
    def cur(key):
        return ' aria-current="page"' if key == current else ""
    return f'''<a class="skip" href="#main">Skip to content</a>

<div class="util" role="complementary" aria-label="Shop details">
  <div class="wrap util-in">
    <p class="util-l"><a href="{SITE["maps"]}">499 Ray Lawson Blvd, Unit 24, Brampton</a><span>{esc(SITE["hours"])}</span></p>
    <p class="util-r"><span>English · Urdu · Hindi · Punjabi</span><a href="{SITE["whatsapp"]}">WhatsApp {SITE["phone_display"]}</a></p>
  </div>
</div>

<header class="head" id="site-nav">
  <div class="wrap head-in">
    {brand(root)}
    <nav class="menu" aria-label="Main">
      <a href="{root}#products" aria-label="Products">{vf("Products")}</a>
      <a href="{root}#about" aria-label="About"{cur("about")}>{vf("About")}</a>
      <a href="{root}#contact" aria-label="Contact"{cur("contact")}>{vf("Contact")}</a>
    </nav>
    <div class="head-cta">
      <a class="btn-ghost" href="tel:{SITE["phone_tel"]}"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2"/></svg><span>{SITE["phone_display"]}</span></a>
      <a class="btn" href="{root}#contact">Get a quote</a>
      <button class="burger" type="button" aria-label="Open menu" aria-expanded="false" aria-controls="sheet"><svg viewBox="0 0 24 24" aria-hidden="true"><path class="l1" d="M4 12H20"/><path class="l2" d="M4 12H20"/><path class="l3" d="M4 12H20"/></svg></button>
    </div>
  </div>
</header>

<div class="sheet" id="sheet" hidden>
  <nav class="sheet-in" aria-label="Menu">
    <a class="sheet-link" href="{root}#products">Products</a>
    <a class="sheet-link" href="{root}#about">About</a>
    <a class="sheet-link" href="{root}#contact">Contact</a>
    <div class="sheet-cta"><a class="btn" href="{root}#contact">Get a quote</a><a class="btn-ghost dark" href="tel:{SITE["phone_tel"]}">Call {SITE["phone_display"]}</a></div>
    <p class="sheet-meta">{esc(SITE["address"])}<br>{esc(SITE["hours"])}</p>
  </nav>
</div>

<main id="main">
'''


def footer(root):
    return f'''
</main>

<footer class="foot">
  <div class="wrap foot-in">
    <div class="foot-brand">
      {brand(root)}
      <p class="foot-line">AZ Printing &amp; Signs is Canada’s choice for high-quality digital printing and commercial printing services, delivering superior print pieces to clients nationwide.</p>
    </div>
    <div class="foot-contact">
      <p><a href="{SITE["maps"]}">{esc(SITE["address"])}</a></p>
      <p><a href="tel:{SITE["phone_tel"]}">{SITE["phone_display"]}</a> · <a href="{SITE["whatsapp"]}">WhatsApp</a></p>
      <p>{esc(SITE["hours"])}</p>
    </div>
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
<script src="{root}js/site.js" defer></script>
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
            '"logo":"https://azprintingandsigns.ca/images/az-logo-512.png","areaServed":["Brampton","Mississauga"],"knowsLanguage":["en","pa","ur","hi"]}</script>\n')


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


def hero_layout():
    """Fahad's own hero layout from ?edit=1, saved as hero-layout.json beside
    this file. Absent: the PSD's boxes. Present: its boxes and order win,
    and the headline / Premium quality blocks get its variables inline."""
    p = os.path.join(HERE, "hero-layout.json")
    if not os.path.exists(p):
        return None
    with open(p) as f:
        return json.load(f)


def style_vars(block):
    custom = hero_layout()
    if not custom or not custom.get(block):
        return ""
    return ' style="' + ";".join(f"--{k}:{v}" for k, v in custom[block].items()) + '"'


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
    layers = m["layers"]
    custom = hero_layout()
    if custom:
        by = {L["name"]: L for L in layers}
        for name in custom["order"]:
            if name not in by:
                fail(f"hero-layout.json names an unknown layer {name}")
        layers = []
        for name in custom["order"]:
            L = dict(by[name])
            c = custom["layers"][name]
            scale = (c["w"] * W / 100) / L["w"]
            L["x"], L["y"], L["w"], L["h"] = c["x"] * W / 100, c["y"] * H / 100, c["w"] * W / 100, L["h"] * scale
            layers.append(L)
    n = len(layers)
    # the ground: the flat gradient, then the ribbon twice (the real one and a
    # mirrored, fainter copy behind it) so the background can move while the
    # products stay still
    out = [f'<img class="hero-ground" src="{root}images/client/hero-base-1920.jpg" '
           f'srcset="{root}images/client/hero-base-1280.jpg 1280w, {root}images/client/hero-base-1920.jpg 1920w" '
           f'sizes="100vw" alt="" width="1920" height="1083" fetchpriority="high">',
           f'<img class="hero-swirl hero-swirl-b" src="{root}images/client/hero/swirl.webp" alt="" width="1920" height="1083" aria-hidden="true">',
           f'<img class="hero-swirl hero-swirl-a" src="{root}images/client/hero/swirl.webp" alt="" width="1920" height="1083" fetchpriority="high" aria-hidden="true">']
    for i, L in enumerate(layers):
        depth = round(0.35 + 0.65 * i / max(n - 1, 1), 2)
        slug, label = HERO_LINKS[L["name"]]
        # a label hangs below its item unless the item sits at the stage's
        # bottom edge, where it would be clipped; then it goes above
        above = " above" if (L["y"] + L["h"]) / H > 0.9 else ""
        out.append(f'<a class="hero-item" href="{root}#contact" data-name="{L["name"]}" data-depth="{depth}" '
                   f'aria-label="{esc(label)}: get a quote" '
                   f'style="--x:{L["x"]/W*100:.3f}%;--y:{L["y"]/H*100:.3f}%;--w:{L["w"]/W*100:.3f}%">'
                   f'<span class="hero-float"><span class="hero-lift">'
                   f'<img src="{root}images/client/hero/{L["name"]}.webp" alt="" width="{L["w"]}" height="{L["h"]}">'
                   f'</span></span><span class="hero-tag{above}" aria-hidden="true">{esc(label)}</span></a>')
    return "\n    ".join(out)


def words(text):
    return " ".join(f'<span class="w">{esc(w)}</span>' for w in text.split())


def first_sentence(text):
    return text.split(". ")[0].rstrip(".") + "."


# "What we do" LAYOUTS (Fahad 2026-10-06: picked C "shelves" and D "bento" off
# the board `2026-10-06-what-we-do-layouts.html`, "keep a switch on the local
# host so that I can change them"). Both are built into the page; the FIRST is
# what loads, and js/site.js shows a switch ONLY on localhost when more than one
# is listed. BEFORE GO-LIVE cut this to the one he keeps, so the live page ships
# one copy of the catalogue, not two.
# PRINT2GO PASS (Fahad 2026-10-06 night: "the page is far too cluttered", reference
# print2go.com): one layout, "tabs" = group tabs over a single row of light
# product cards. shelves / bento / circles stay defined below but are off.
CATALOG_LAYOUTS = ("tabs",)
# Bento placement: big tile, two tall ones, one wide; our pick, a cheap swap.
BENTO_AREAS = {"business-cards": "bc", "flyers": "fl", "brochures": "br", "greeting-cards": "gc",
               "posters": "po", "lawn-signs": "ls", "rollup-banner": "rb", "store-branding": "sb",
               "round-stickers": "st", "door-hangers": "dh", "letterhead": "lh", "photocopy": "pc",
               "document-scan": "ds", "spiral-binding": "sp"}
CHEV = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15 6l-6 6 6 6"/></svg>'


def c3d_card(root, slug, gtitle, cls="", style="", sizes="(min-width: 900px) 24vw, 62vw", w=800):
    """One 3D tilting photo card (js/site.js tilts every .c3d)."""
    p = by_slug(slug)
    return (f'<li class="c3d{(" " + cls) if cls else ""}"{style}><a href="{root}#contact">'
            f'<span class="c3d-in">'
            f'<span class="c3d-img"><img src="{root}images/client/tile-{slug}-800.jpg" srcset="{root}images/client/tile-{slug}-480.jpg 480w, {root}images/client/tile-{slug}-800.jpg 800w" sizes="{sizes}" alt="{esc(p["alt"])}" width="800" height="800" loading="lazy"></span>'
            f'<span class="c3d-chip">{esc(gtitle)}</span>'
            f'<span class="c3d-txt"><strong>{esc(p["name"])}</strong><span>{esc(SHORT[slug])}</span></span>'
            f'<span class="c3d-go" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M5 12h14M13 6l6 6-6 6"/></svg></span>'
            f'<span class="c3d-glare" aria-hidden="true"></span>'
            f'</span></a></li>')


def catalog_html(root):
    """Home "What we do": every layout in CATALOG_LAYOUTS, the first visible."""
    gt = {s: t for t, _, ss in GROUPS for s in ss}
    views = {}
    views["shelves"] = "".join(
        f'<div class="shelf"><div class="shelf-h"><h3>{esc(t)} <span>{len(ss)}</span></h3>'
        f'<span class="shelf-arrows"><button type="button" data-dir="-1" aria-label="Scroll {esc(t)} back">{CHEV}</button>'
        f'<button type="button" data-dir="1" aria-label="Scroll {esc(t)} forward">{CHEV}</button></span></div>'
        f'<ul class="shelf-row">{"".join(c3d_card(root, sl, t, sizes="(min-width: 900px) 280px, 62vw") for sl in ss)}</ul></div>'
        for t, _, ss in GROUPS)
    views["bento"] = '<ul class="bento">' + "".join(
        c3d_card(root, sl, gt[sl], cls=f"a-{a}", style=f' style="grid-area:{a}"',
                 sizes="(min-width: 900px) 46vw, 92vw" if a == "bc" else "(min-width: 900px) 24vw, 46vw")
        for sl, a in BENTO_AREAS.items()) + '</ul>'
    views["circles"] = '<ul class="circles">' + "".join(
        f'<li class="cir"><a href="{root}#contact"><span class="cir-i"><img src="{root}images/client/tile-{sl}-480.jpg" '
        f'srcset="{root}images/client/tile-{sl}-480.jpg 480w, {root}images/client/tile-{sl}-800.jpg 800w" sizes="(min-width: 1000px) 12vw, 30vw" '
        f'alt="" width="480" height="480" loading="lazy"></span><b>{esc(by_slug(sl)["name"])}</b></a></li>'
        for _, _, ss in GROUPS for sl in ss) + '</ul>'
    tabs = "".join(
        f'<button class="ptab" type="button" role="tab" id="ptab-{gi}" aria-controls="ppanel-{gi}" aria-selected="{"true" if gi == 0 else "false"}">{esc(t)}</button>'
        for gi, (t, _, _) in enumerate(GROUPS))
    panels = "".join(
        f'<ul class="pcards" role="tabpanel" id="ppanel-{gi}" aria-labelledby="ptab-{gi}"{"" if gi == 0 else " hidden"}>'
        + "".join(
            f'<li class="pcard"><a href="{root}#contact"><span class="pcard-img"><img src="{root}images/client/tile-{sl}-480.jpg" '
            f'srcset="{root}images/client/tile-{sl}-480.jpg 480w, {root}images/client/tile-{sl}-800.jpg 800w" sizes="(min-width: 1100px) 270px, (min-width: 900px) 24vw, (min-width: 600px) 32vw, 48vw" '
            f'alt="{esc(by_slug(sl)["alt"])}" width="480" height="480" loading="lazy"></span>'
            f'<b>{esc(by_slug(sl)["name"])}</b><span class="pcard-go" aria-hidden="true">{ARROW}</span></a></li>'
            for sl in ss) + '</ul>'
        for gi, (_, _, ss) in enumerate(GROUPS))
    views["tabs"] = f'<div class="ptabs" role="tablist" aria-label="Product groups">{tabs}</div>{panels}'
    return "".join(
        f'<div class="cat-view cat-{v}" data-view="{v}"{"" if i == 0 else " hidden"}>{views[v]}</div>'
        for i, v in enumerate(CATALOG_LAYOUTS))


ARROW = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'


def process_html():
    steps = "".join(
        f'<li class="step"><span class="step-ic"><svg viewBox="0 0 48 48" aria-hidden="true">{STEP_ICON[ic]}</svg></span>'
        f'<h3>{esc(t)}</h3><p>{esc(d)}</p></li>'
        for ic, t, d in STEPS)
    return f'''<section class="band process" aria-labelledby="process-h">
  <div class="wrap">
    <h2 id="process-h">How it works</h2>
    <ol class="steps">{steps}</ol>
  </div>
</section>
'''


def promise_html():
    """Band 2: four printed swatch tiles, we print / we design / we commit /
    we deliver (concept 6a, Fahad 2026-10-06). The buttons and the languages
    line were removed on his ask the same night: the tiles stand alone."""
    # Premium restyle (Fahad 2026-10-06, a paint-palette pin as inspiration):
    # rounded ink blocks, the name in italic serif, the code spaced out below.
    tiles = "".join(
        f'<li class="sw" style="background:{c};color:{ink}"><span class="sw-hex">{c}</span>'
        f'<span class="sw-name">We {v.capitalize()}</span></li>'
        for v, lab, c, ink in SWATCHES)
    return f'''<section class="band promise" aria-labelledby="promise-h">
  <div class="wrap">
    <h2 id="promise-h" class="sr-only">We print, we design, we commit, we deliver</h2>
    <div class="sw-head">
      <p class="sw-eyebrow">Our promise, in our colours</p>
    </div>
    <ul class="swatches">{tiles}</ul>
  </div>
</section>
'''


def doors_html(root):
    """Two light cards: photo on top, words under it (print2go pass, 2026-10-06)."""
    out = []
    for img, kicker, head_, body, cta in DOORS:
        out.append(
            f'<a class="dcard" href="#contact">'
            f'<span class="dcard-img"><img src="{root}images/tiles/{img}-900.jpg" srcset="{root}images/tiles/{img}-900.jpg 900w, {root}images/tiles/{img}.jpg 1600w" '
            f'sizes="(min-width: 900px) 600px, 92vw" alt="" width="1600" height="1000" loading="lazy"></span>'
            f'<span class="dcard-body"><small>{esc(kicker)}</small><h3>{esc(head_)}</h3>'
            f'<span class="dcard-p">{esc(body)}</span>'
            f'<span class="dcard-go">{esc(cta)}{ARROW}</span></span></a>')
    return "".join(out)


def industries_html(root):
    """Five trades as light cards: photo, name, the product it uses; opens the quote form."""
    out = []
    for img, name, line, slug in INDUSTRIES:
        out.append(
            f'<a class="icard" href="{root}#contact">'
            f'<span class="icard-img"><img src="{root}images/tiles/{img}-560.jpg" srcset="{root}images/tiles/{img}-560.jpg 560w, {root}images/tiles/{img}.jpg 900w" '
            f'sizes="(min-width: 1100px) 230px, 46vw" alt="" width="900" height="1200" loading="lazy"></span>'
            f'<b>{esc(name)}</b><span class="icard-go">{esc(by_slug(slug)["name"])}{ARROW}</span></a>')
    return "".join(out)


def home():
    root = ""
    title = "AZ Printing & Signs | Printing, signs and design in Brampton"
    desc = ("Printing, signs, graphic design and branding in Brampton: business cards, flyers, lawn signs, "
            "banners, stickers, copying, scanning and binding. Call 905-796-1515.")
    extra = '<link rel="preload" as="image" href="images/client/hero-base-1920.jpg" media="(min-width: 900px)">\n'
    h = head(root, title, desc, extra, business_schema()) + header(root, "home")
    h += f'''
<section class="hero" aria-labelledby="hero-h">
  <div class="hero-text"{style_vars("text")}>
    <p class="hero-eyebrow">We print · We design · We build brands</p>
    <h1 id="hero-h">{words("Your business deserves to be seen")}</h1>
    <p class="hero-ctas"><a class="btn btn-white" href="#contact">Get a quote</a><a class="hero-call" href="tel:{SITE["phone_tel"]}">Call {SITE["phone_display"]}</a></p>
  </div>
  <div class="hero-view"><div class="hero-stage" aria-label="Printed pieces side by side, each a link to the quote form: a menu, business cards, flyers, a roll-up banner, a poster, a lawn sign, an A-frame sign, stickers and a notepad">
    {hero_stage(root)}
  </div></div>
  <p class="hero-quality"{style_vars("quality")}>Premium quality</p>
</section>

{process_html()}
<section class="catalog" id="products" aria-labelledby="products-h" data-layouts="{" ".join(CATALOG_LAYOUTS)}">
  <div class="wrap">
    <div class="catalog-head">
      <h2 id="products-h">What we do</h2>
      <p>Fourteen products and services. Choose one to ask us for a quote.</p>
    </div>
    {catalog_html(root)}
  </div>
</section>

<section class="welcome" id="about" aria-labelledby="welcome-h">
  <div class="wrap welcome-in">
    <div class="welcome-text">
      <h2 id="welcome-h">Welcome to Brampton<br>AZ Printing &amp; Signs</h2>
      <p>AZ PRINTING &amp; SIGNS is your one-stop destination for professional printing, signage, graphic design, and branding services in Brampton.</p>
      <p>Conveniently located at 499 Ray Lawson Blvd, we offer digital printing, Xerox promotional printing, photocopying (Photo Stat), scanning, spiral binding, and custom signage, including window graphics.</p>
      <p>Our qualified designer also provides logo design, brand identity, complete rebranding, and marketing design services to help businesses build a professional and consistent image.</p>
      <p>From everyday printing to complete branding solutions, AZ PRINTING &amp; SIGNS is here to bring your ideas to life with quality, creativity, and reliable service.<br><a class="contact-link" href="#contact">Contact us</a> today to learn more about how we can help you.</p>
    </div>
    <figure class="welcome-photo"><img src="images/client/storefront-1200.jpg" srcset="images/client/storefront-800.jpg 800w, images/client/storefront-1200.jpg 1200w" sizes="(min-width: 760px) 44vw, 92vw" alt="The AZ Printing &amp; Signs storefront at 499 Ray Lawson Blvd, Brampton: the sign, the phone number and the window listings" width="1200" height="800" loading="lazy"></figure>
  </div>
</section>

<section class="doors" aria-labelledby="doors-h">
  <div class="wrap">
    <div class="catalog-head"><h2 id="doors-h">Printing for events and businesses</h2></div>
    <div class="dcards">{doors_html(root)}</div>
  </div>
</section>

<section class="inds" aria-labelledby="inds-h">
  <div class="wrap">
    <div class="catalog-head"><h2 id="inds-h">Industries we serve</h2></div>
    <div class="icards">{industries_html(root)}</div>
  </div>
</section>

{contact_html()}
'''
    return h + footer(root)


def contact_html():
    return f'''<section class="contact" id="contact" aria-labelledby="contact-h">
  <div class="wrap">
    <h2 id="contact-h">Send us a message</h2>
    <div class="contact-in">
      <form class="contact-form" action="https://formsubmit.co/{SITE["email"]}" method="POST">
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
      <figure class="map"><iframe title="Map showing AZ Printing &amp; Signs at 499 Ray Lawson Blvd, Brampton" src="{esc(SITE["map_embed"])}" loading="lazy" referrerpolicy="no-referrer-when-downgrade" allowfullscreen></iframe></figure>
    </div>
  </div>
</section>'''


# ---------------------------------------------------------------------------
# files, verify, confirm
# ---------------------------------------------------------------------------

def outputs():
    yield "index.html", home()


def sitemap():
    urls = [SITE["domain"]]
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
    if sorted(BENTO_AREAS) != sorted(slugs):
        fail("BENTO_AREAS must place every product exactly once")
    for path, h in outputs():
        if re.search(r'href="[^"]*products/', h):
            fail(f"{path}: links to a product page; this site is one landing page")
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
    print(f"verify ok: {len(PRODUCTS)} products, {len(names)} type lines, {len(list(outputs()))} page")


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
    out.append("## Home page")
    for where, fact, why in PAGE_FACTS:
        out.append(f"- [ ] **{where}:** {fact} ({why})")
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
