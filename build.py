#!/usr/bin/env python3
"""AZ Printing & Signs — LANDING SITE (presence build).

A SEPARATE deliverable from the shop build in `05 - Site/`. The client wants an
online presence now, "not an ecommerce site yet", and the shop launches later.

2026-09-13 — CLIENT FEEDBACK ROUND (relayed by Fahad), which reshaped this page:
  * incorrect terms were used, and products sat under the wrong groups
  * one landing page that demonstrates the services and gives information
  * no e-commerce, just a digital presence
  * sub-categories must be explained ("business cards have multiple types,
    glossy, matte, etc.")
  * the design should be more sophisticated and neutral, similar to Staples

So the eight loose tiles became a CATEGORY EXPLORER: twelve groups laid out the
way the trade (and Staples Print Canada, read live 2026-09-13) groups them, with
every product and option explained in one plain line. Its vocabulary is the
owner's own, taken from two sources he wrote himself: his services answers
(R2 form, 2026-08-23) and the product list on his shop window.

EVERY LINE CARRIES A SOURCE TAG (see SOURCES). That is the fact register for a
page that cannot show brackets: nothing is on it that cannot say where it came
from, and `python3 build.py --confirm` prints the lines the owner has not yet
said yes to, as one list for one conversation.

ONE RULE THIS BUILD ENFORCES THAT THE SHOP BUILD DOES NOT: no bracketed
unknowns. This page is meant to go public, so verify() refuses to build if one
survives. Where a fact is unknown, the sentence is left out.

    python3 build.py            build + verify
    python3 build.py --check    verify only
    python3 build.py --confirm  print the owner confirm list (markdown)
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
    "phone_display": "905-796-1515",
    "phone_tel": "9057961515",
    "whatsapp": "https://wa.me/19057961515",
    "address": "499 Ray Lawson Blvd, Unit 24, Brampton, ON L6Y 4E6",
    # Google's documented Maps URL API, carrying the BUSINESS NAME as well as the
    # address. An address-only query can land on the plaza rather than the unit.
    "maps": "https://www.google.com/maps/search/?api=1&query=AZ+Printing+and+Signs%2C+499+Ray+Lawson+Blvd+%2324%2C+Brampton%2C+ON+L6Y+4E6",
    "hours": "Mon to Fri 10:30 to 7 · Sat 12 to 4 · Sun closed",
    "area_line": "A family-run print and sign shop serving Brampton, Mississauga and the GTA.",
}

# Where each line on the page comes from. `owner` and `client` are the owner's
# own word; the other three are what the owner is asked to confirm (--confirm).
SOURCES = {
    "owner": "owner's services answers, R2 form 2026-08-23",
    "client": "client feedback relayed by Fahad 2026-09-13",
    "window": "the shop's own window vinyls (storefront photo 2026-08-27)",
    "signs": "Fahad's all-signs ruling 2026-08-27, provisional",
    "std": "industry-standard option, not yet confirmed by the owner",
}
CONFIRMED = {"owner", "client"}

# ---------------------------------------------------------------------------
# THE CATALOGUE. Order follows demand and the Staples reference: cards and
# marketing first, the sign families together, personal products last.
# A group is: id, name, intro, media, sets. A set is (title or None, items).
# An item is (name, explanation, "src+src").
# media is ("img", file, alt) or ("svg", key, label).
# ---------------------------------------------------------------------------
GROUPS = [
    {"id": "business-cards", "name": "Business Cards",
     "intro": "Printed on one or both sides at the standard 3.5 x 2 inch size. The finish decides how the card looks and feels in the hand.",
     "media": ("img", "business-cards.jpg", "Two business cards, one light and one dark, sample designs"),
     "sets": [("Finishes", [
         ("Matte", "A smooth card with no shine. Text stays easy to read under any light, and you can write on it.", "client"),
         ("Glossy", "A shiny coating that makes colours and photos look brighter and richer.", "client"),
         ("Soft Touch", "A velvety coating with a smooth, suede-like feel in the hand.", "window"),
         ("Spot UV", "A clear, glossy coating on selected areas, such as your logo, so they shine against a matte card.", "window"),
         ("Foil", "Metallic gold or silver foil pressed onto your logo or name so it catches the light.", "window"),
     ])]},

    {"id": "marketing-materials", "name": "Marketing Materials",
     "intro": "Printed pieces that promote a business, an event or an opening, handed out or sent by mail.",
     "media": ("img", "flyer.jpg", "A printed restaurant flyer, sample design"),
     "sets": [(None, [
         ("Flyers", "Single sheets printed on one or both sides, for handing out, posting or mailing.", "owner+window"),
         ("Brochures", "Folded into panels, as a bi-fold or tri-fold, with room to explain your services in detail.", "owner+window"),
         ("Postcards", "Sturdy cards for mail campaigns, promotions and appointment reminders.", "owner+window"),
         ("Door Hangers", "Cut to hang on a door handle, for reaching every home on a street.", "owner+window"),
         ("Booklets & Catalogues", "Multi-page printed books, stapled or bound, for product ranges, programs and guides.", "owner+window"),
         ("Menus", "Takeout, dine-in and laminated menus for restaurants and cafés.", "owner+window"),
     ])]},

    {"id": "stationery-forms", "name": "Stationery & Forms",
     "intro": "Everyday business paperwork, printed with your logo and contact details.",
     "media": ("svg", "stationery", "A letterhead, an envelope and a carbonless invoice book"),
     "sets": [(None, [
         ("Letterheads", "Your logo and details on paper for letters, quotes, invoices and agreements.", "owner+window"),
         ("Envelopes", "Business envelopes printed with your logo and return address.", "owner"),
         ("NCR Forms & Invoice Books", "NCR (no carbon required) forms make a copy as you write, bound into books for invoices, receipts and work orders.", "owner+window"),
         ("Notepads", "Branded writing pads, glued along the top edge, for the office or for clients.", "owner"),
         ("Presentation Folders", "Printed folders with inside pockets that hold proposals, price lists and brochures.", "owner"),
         ("Custom Stamps", "Stamps carrying your company name, address, logo or signature.", "window"),
     ])]},

    {"id": "signs", "name": "Signs",
     "intro": "Printed signs for properties, sidewalks, offices and events.",
     "media": ("img", "lawn-sign.jpg", "A printed lawn sign on metal stakes, sample design"),
     "sets": [(None, [
         # The owner's window says LAWN SIGNS, and so do customers searching for
         # one. The material leads nothing; it is explained inside the line.
         ("Lawn Signs", "Printed on coroplast, a lightweight corrugated plastic that holds up to rain and sun, for lawns and yards.", "signs+window"),
         ("Real Estate Signs", "Realtor, for sale and open house signs that mark a listing and point buyers to the door.", "signs+window"),
         ("A-Frame Signs", "Two-sided sidewalk signs, also called sandwich boards, that fold flat at closing time.", "signs+window"),
         ("Welcome Signs", "Signs that greet guests at weddings, parties and community events.", "window"),
         ("Acrylic & Metal Signs", "Rigid signs in clear acrylic or metal for reception walls, office doors and entrances.", "signs"),
         ("Office & Wayfinding Signs", "Door, room and directional signs that help visitors find their way around a building.", "signs"),
         ("Safety Signs", "Safety and regulatory signs for workplaces, warehouses and job sites.", "signs"),
         ("Menu Boards", "Printed menu boards for behind the counter or outside the door.", "signs"),
     ])]},

    {"id": "banners-displays", "name": "Banners & Displays",
     "intro": "Large prints for storefronts, events and trade shows, indoors or outside.",
     "media": ("img", "banner.jpg", "A printed vinyl banner with metal grommets, sample design"),
     "sets": [(None, [
         ("Vinyl Banners", "Durable printed vinyl with grommets, the metal rings along the edge, for hanging indoors or outside.", "signs+window"),
         ("Pull-Up Banners", "A banner that rolls out of its own base and stands upright. Also called a standee or retractable banner.", "signs+window"),
         ("Feather Flags", "Tall, curved flags on a pole that stay visible from the road and the parking lot.", "window"),
         ("Step-and-Repeat Backdrops", "Large backdrops with your logo repeated across them, for event photos and media walls.", "signs"),
         ("Posters", "Prints for windows, walls, events and displays, from small sizes up to large format.", "owner"),
     ])]},

    {"id": "storefront-signs", "name": "Storefront Signs",
     "intro": "Permanent signs for the front of a business, made to be read from the street.",
     "media": ("img", "storefront-sign.jpg", "A lit storefront sign reading AZ Printing and Signs"),
     "sets": [(None, [
         ("Channel Letters", "Individual 3D letters mounted on the building, often lit from inside or behind so the name shows at night.", "signs+window"),
         ("Light Box Signs", "A sign cabinet with a printed face, lit from inside.", "signs+window"),
         ("Pylon Signs", "Tall freestanding signs at a plaza entrance or roadside that list the businesses on site.", "window"),
         ("Neon Signs", "Glowing signs shaped into words or a logo, for windows, walls and interiors.", "window"),
         ("Fascia Signs", "Sign panels for the fascia, the band above a shop's windows, and other parts of the building.", "signs"),
     ])]},

    {"id": "vinyl-graphics", "name": "Vinyl Graphics & Wraps",
     "intro": "Printed and cut vinyl applied to windows, walls and vehicles.",
     "media": ("img", "window-graphics.jpg", "Printed vinyl graphics covering the windows of the AZ Printing and Signs shop"),
     "sets": [(None, [
         ("Window Graphics", "Printed or cut vinyl for shop windows, showing your name, hours, services or promotions.", "signs+window"),
         ("Frosted Vinyl", "A frosted glass effect for office windows and doors that adds privacy and still lets light through.", "signs"),
         ("Vehicle Decals & Magnets", "Your logo and phone number on a work vehicle, as applied decals or removable magnets.", "signs"),
         ("Vehicle Wraps", "Printed vinyl that covers part or all of a vehicle in your design.", "signs"),
         ("Wallpapers", "Custom printed wallpaper for feature walls in offices, shops, restaurants and homes.", "window"),
     ])]},

    {"id": "stickers-labels", "name": "Stickers & Labels",
     "intro": "Printed stickers and labels for packaging, products, giveaways and events.",
     "media": ("img", "sticker.jpg", "A die-cut sticker of a bear holding a coffee, sample design"),
     "sets": [(None, [
         ("Die-Cut Stickers", "Stickers cut around the outline of your design, in the shape you need.", "owner+window"),
         ("Sticker Sheets", "Several stickers printed on one sheet, easy to peel and hand out.", "std"),
         ("Product Labels", "Labels for jars, bottles, bags and boxes, printed with your logo and product details.", "owner"),
     ])]},

    {"id": "apparel", "name": "Apparel",
     "intro": "Custom clothing for teams, staff, events and gifts, from a single piece to a full order. The decoration method depends on the design and the quantity.",
     "media": ("img", "tshirt.jpg", "A black t-shirt printed with a colourful mountain design, sample design"),
     "sets": [
         ("What we customize", [
             ("T-Shirts & Hoodies", "Printed tees and hoodies for teams, staff, events and fundraisers.", "owner+window"),
             ("Polos & Uniforms", "Embroidered polos and staff uniforms for offices, shops and restaurants.", "owner"),
             ("Caps & Hats", "Caps and hats embroidered with your logo.", "owner+window"),
             ("Tote Bags", "Printed tote bags for shops, events and giveaways.", "owner"),
         ]),
         ("Decoration methods", [
             ("Screen Printing", "Ink pressed through a fine mesh screen, one colour at a time. Bold and long-lasting, and best suited to larger orders.", "owner"),
             ("DTF Printing", "Direct to film: the design is printed onto a film, then heat-pressed onto the garment. Full colour and fine detail, even for one piece.", "window"),
             ("Embroidery", "Your logo stitched in thread, a durable finish for polos, caps and uniforms.", "owner+window"),
         ]),
     ]},

    {"id": "promotional-products", "name": "Promotional Products",
     "intro": "Branded items to give away at events, reward a team or thank customers.",
     "media": ("img", "mugs.jpg", "Three white mugs printed with names and initials, sample designs"),
     "sets": [(None, [
         ("Mugs & Drinkware", "Mugs and drinkware printed with a logo, a name or a photo.", "owner+window"),
         ("Pens", "Branded pens for the front desk, trade shows and client gifts.", "owner+window"),
         ("Keychains & Giveaways", "Small branded items to hand out at events and grand openings.", "owner"),
         ("Lanyards & Name Badges", "Printed lanyards and name badges for staff, conferences and events.", "owner"),
         ("Awards, Plaques & Trophies", "Awards personalized with names and titles, for staff recognition, teams and tournaments.", "owner"),
         ("Fridge Magnets", "Printed magnets that keep your phone number on a customer's fridge.", "owner"),
     ])]},

    {"id": "invitations-cards", "name": "Invitations & Cards",
     "intro": "Cards for weddings and celebrations, and for the thank-yous that follow.",
     "media": ("img", "wedding-invitation.jpg", "A wedding invitation with a green botanical border, sample design"),
     "sets": [(None, [
         ("Wedding Invitations", "Invitations for the wedding and each event around it, including shaadi, nikkah, mehndi and walima cards.", "owner"),
         ("Event Invitations", "Invitations for birthdays, engagements, anniversaries, religious events and community gatherings.", "owner"),
         ("Greeting & Thank You Cards", "Folded or flat cards for holidays, thank-yous and business greetings.", "owner+window"),
     ])]},

    {"id": "canvas-photo-prints", "name": "Canvas & Photo Prints",
     "intro": "Photos and artwork printed for the wall, the desk or a gift.",
     "media": ("img", "canvas.jpg", "A canvas print of a guitar illustration, sample design"),
     "sets": [(None, [
         ("Canvas Prints", "Your photo or artwork printed on canvas for the wall.", "owner"),
         ("Photo Prints", "Prints from your phone or camera, from small sizes up to poster size.", "owner"),
         ("Calendars", "Calendars printed with your photos or your business branding.", "owner"),
     ])]},
]

SERVICES = [
    ("Graphic Design", "Flyers, cards, menus and signs designed for you, including logo and branding design.", "owner+window"),
    ("Printing & Copying", "Black and white or colour copies, and documents printed from your file.", "owner+window"),
    ("Scanning & Faxing", "Paper documents scanned to a file, and faxes sent from the counter.", "owner+window"),
    ("Laminating & Binding", "A clear protective layer for menus, signs and certificates, and reports or manuals bound into a finished document.", "owner+window"),
    ("Passport & ID Photos", "Photos for passports and ID, taken at the shop.", "owner"),
    ("Courier & Shipping", "Send parcels with UPS or DHL from our counter.", "owner+window"),
    ("Mailbox Rental", "Rent a personal mailbox at the shop to receive your mail.", "owner+window"),
    # A SERVICE, NOT A PRODUCT: it sat under Storefront Signs for one round,
    # which is the very "wrong group" complaint this round answers.
    ("Sign Installation", "We install signs, wraps and window graphics.", "owner"),
]

# Facts on the page OUTSIDE the catalogue that are still provisional or are
# the studio's reading of a source. They go on the owner list with the products,
# so one conversation covers everything before the page goes public.
PAGE_FACTS = [
    ("About", "More than twenty years of printing experience", "Fahad's account 2026-07-31 (owner in printing since 2002), provisional"),
    ("About", "Previously ran his own print and shipping store, and printed for an agency", "Fahad's account 2026-07-31, provisional"),
    ("FAQ", "Standard jobs are ready in 2 to 4 business days from proof approval", "Fahad's account 2026-07-31, provisional"),
    ("What to expect, FAQ", "A proof is sent for approval before printing begins, on every job", "brief follow-up item 3, never answered"),
    ("Doors, Contact", "Customers can compare materials and samples at the counter", "approved copy 2026-09-09, no owner source"),
    ("Business Cards", "The window says UV: the page reads that as Spot UV. Or is it a full UV gloss coating?", "studio reading of the window vinyl"),
    ("Not on the page", "The window also lists Resume, Business Boards and Perfumes. What are these services?", "window vinyl, left out until explained"),
]

# Kept from the approved page. The icons are redrawn in the neutral inks
# (2026-09-13): the shop build's amber and red fills belonged to the "pop"
# direction the client has now asked to move away from.
REASONS = [
    ("Order again without starting over",
     "Your approved artwork stays on file, so repeat orders can begin with a phone call, even years later.",
     '<svg viewBox="0 0 48 48" aria-hidden="true"><path d="M5 13h13l4 5h21v23H5z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><path d="M14 9h20v9" fill="none" stroke="currentColor" stroke-width="2"/><path d="M5 25h38" stroke="var(--red)" stroke-width="2"/></svg>'),
    ("Order the quantity you need",
     "One shirt or a thousand flyers, both are welcome at the counter.",
     '<svg viewBox="0 0 48 48" aria-hidden="true"><rect x="7" y="7" width="22" height="30" fill="none" stroke="currentColor" stroke-width="2"/><rect x="13" y="12" width="22" height="30" fill="#fff" stroke="currentColor" stroke-width="2"/><rect x="30" y="30" width="12" height="13" fill="var(--red)"/></svg>'),
    ("Choose pickup or delivery",
     "Pick up on Ray Lawson Blvd, or ask about delivery across Brampton and Mississauga.",
     '<svg viewBox="0 0 48 48" aria-hidden="true"><path d="M4 13h26v21H4zM30 19h8l6 7v8H30" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><circle cx="13" cy="36" r="4" fill="#fff" stroke="currentColor" stroke-width="2"/><circle cx="36" cy="36" r="4" fill="#fff" stroke="currentColor" stroke-width="2"/><path d="M9 20h14" stroke="var(--red)" stroke-width="2"/></svg>'),
    ("Approve the proof first",
     "We send a proof for your approval before printing begins.",
     '<svg viewBox="0 0 48 48" aria-hidden="true"><path d="M9 5h24v34H9z" fill="none" stroke="currentColor" stroke-width="2"/><path d="M14 13h14M14 19h14M14 25h8" stroke="currentColor" stroke-width="2"/><circle cx="35" cy="35" r="9" fill="#fff" stroke="var(--red)" stroke-width="2"/><path d="M31 35l3 3 6-6" fill="none" stroke="var(--red)" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>'),
]

INDUSTRY_TILES = [
    ("Real estate", "The listing goes live Thursday and the sign has to be on the lawn first.", "ind-real-estate.jpg"),
    ("Restaurants", "A menu gets handled more than anything else we print.", "ind-restaurants.jpg"),
    ("Professional services", "The folder that leaves the meeting, the letterhead under the agreement.", "ind-offices.jpg"),
    ("Construction & trades", "The site sign, the truck door, the invoice book.", "ind-construction.jpg"),
    ("Community & religious organizations", "Banner up Friday, programs ready Sunday.", "ind-community.jpg"),
]

DOORS = [
    ("door-event.jpg", "The day you're planning", "For your event",
     "Choose invitations, welcome signs and banners for weddings, birthdays and community events. Visit the shop to compare materials and samples in person.",
     "Ask about event printing"),
    ("door-business.jpg", "The name you're building", "For your business",
     "Order business cards, flyers, apparel and signs from the same counter as your business grows.",
     "Ask about business printing"),
]

FAQ = [
    ("How long does it take?",
     "Standard jobs are ready in 2 to 4 business days from proof approval. Some jobs can be done the same day; ask when you order."),
    ("Do I see a proof before it prints?",
     "Yes. Printing starts once you approve it."),
    ("What do I need to bring?",
     "Whatever you have. If it can be made printable, we will make it printable."),
    ("What if my file is not print-ready?",
     "Fixing a file you already have, so it prints properly, is part of every job and costs nothing."),
    ("Do you print small orders?",
     "Yes. One shirt or one canvas is a normal order here."),
]

BANNED = ["—", "AZ Printing and Signs", "416-731-9229", "(416)", "PrimePress",
          "hi-vis", "workwear", "notary", "Learn More", "Submit",
          # PRODUCTION CLAIMS. Apparel is sent out (brief v2), so the page may
          # say a job is ordered, handled or delivered here, never that
          # everything is printed here. Two of these shipped on the 09-09 page
          # ("printed at our Brampton shop", "made or finished at the counter").
          "printed at our", "printed in our", "printed here", "made or finished",
          "in-house", "in house",
          # The old tile names this round exists to retire.
          "Handouts", "Printed mugs"]

NUM_WORDS = {10: "Ten", 11: "Eleven", 12: "Twelve", 13: "Thirteen", 14: "Fourteen"}


def esc(s):
    return html.escape(s, quote=True)


def items_of(group):
    for _title, items in group["sets"]:
        for it in items:
            yield it


def wa_link(text):
    return SITE["whatsapp"] + "?text=" + urllib.parse.quote(text)


def stationery_svg(label):
    """The one group with no product render. Drawn as a flat paper mock-up in
    the page's own inks, so it sits beside the photographed renders without
    pretending to be one. NCR sets are white, yellow and pink: that colour
    stack is how the trade recognises a carbonless book at a glance."""
    return f"""<svg class="ex-svg" viewBox="0 0 1200 750" role="img" aria-label="{esc(label)}">
<defs><filter id="paper-sh" x="-15%" y="-15%" width="130%" height="140%"><feDropShadow dx="0" dy="12" stdDeviation="16" flood-color="#101820" flood-opacity=".13"/></filter></defs>
<rect width="1200" height="750" fill="#fff"/>
<g transform="rotate(-6 400 330)" filter="url(#paper-sh)">
<rect x="235" y="80" width="330" height="430" fill="#fff" stroke="#E6E6E3" stroke-width="2"/>
<rect x="270" y="118" width="44" height="44" fill="#A01D20"/>
<rect x="328" y="124" width="118" height="12" fill="#101820"/><rect x="328" y="146" width="80" height="8" fill="#9A9C9E"/>
<g fill="#D9D9D6"><rect x="270" y="210" width="258" height="8"/><rect x="270" y="232" width="240" height="8"/><rect x="270" y="254" width="252" height="8"/><rect x="270" y="276" width="170" height="8"/>
<rect x="270" y="318" width="258" height="8"/><rect x="270" y="340" width="232" height="8"/><rect x="270" y="362" width="248" height="8"/><rect x="270" y="384" width="120" height="8"/></g>
<rect x="270" y="446" width="96" height="10" fill="#53565A"/>
</g>
<g transform="rotate(5 860 320)" filter="url(#paper-sh)">
<rect x="722" y="116" width="300" height="392" fill="#F4C7CD"/>
<rect x="711" y="105" width="300" height="392" fill="#F8E9A8"/>
<rect x="700" y="94" width="300" height="392" fill="#fff" stroke="#E6E6E3" stroke-width="2"/>
<rect x="700" y="94" width="300" height="34" fill="#101820"/>
<rect x="728" y="152" width="34" height="34" fill="#A01D20"/><rect x="774" y="158" width="92" height="10" fill="#101820"/><rect x="774" y="176" width="60" height="7" fill="#9A9C9E"/>
<g fill="none" stroke="#D9D9D6" stroke-width="2"><rect x="728" y="214" width="244" height="190"/><path d="M728 252h244M728 290h244M728 328h244M728 366h244M890 214v190"/></g>
<rect x="890" y="424" width="82" height="12" fill="#53565A"/>
</g>
<g filter="url(#paper-sh)">
<rect x="400" y="470" width="430" height="226" fill="#fff" stroke="#E6E6E3" stroke-width="2"/>
<rect x="428" y="496" width="30" height="30" fill="#A01D20"/><rect x="470" y="500" width="96" height="9" fill="#101820"/><rect x="470" y="516" width="64" height="7" fill="#9A9C9E"/>
<g fill="#D9D9D6"><rect x="590" y="592" width="170" height="9"/><rect x="590" y="612" width="140" height="9"/><rect x="590" y="632" width="156" height="9"/></g>
</g>
</svg>"""


# RIGHT-SIZED IMAGES (QA checklist: nothing served above 2.2x its display size,
# page under 1.5MB). Each entry: the full file, its smaller variant and their
# widths. Variants are made once with ffmpeg (lanczos, -q:v 4, industry tiles
# -q:v 6) and verify() refuses a srcset pointing at a file that is not on disk.
# window-graphics.jpg has NO variant: its source is a 730px crop of a phone photo,
# and scaling it up to make a "large" version would only add bytes.
VARIANTS = {
    "products": ("-800", 800, 1200),
    "ind": ("-560", 560, 900),
    "door": ("-900", 900, 1600),
    "store": ("-900", 900, 1400),
}


def srcset(path, kind):
    suffix, small, full = VARIANTS[kind]
    base, ext = os.path.splitext(path)
    return f'src="{path}" srcset="{base}{suffix}{ext} {small}w, {path} {full}w"'


def media_html(group):
    kind, ref, label = group["media"]
    if kind == "svg":
        return f'<figure class="ex-media">{stationery_svg(label)}</figure>'
    path = f"images/products/{ref}"
    src = srcset(path, "products") if os.path.exists(os.path.join(HERE, path.replace(".jpg", "-800.jpg"))) else f'src="{path}"'
    return (f'<figure class="ex-media"><img {src} sizes="(min-width: 1024px) 460px, (min-width: 768px) 48vw, 92vw" '
            f'alt="{esc(label)}" loading="lazy" width="1200" height="750"></figure>')


def explorer_html():
    tabs = "".join(
        f'<a class="ex-tab" href="#{g["id"]}"><span>{esc(g["name"])}</span></a>' for g in GROUPS)
    panels = []
    for g in GROUPS:
        sets = []
        for title, items in g["sets"]:
            rows = "".join(
                f'<div class="ty"><dt>{esc(n)}</dt><dd>{esc(e)}</dd></div>' for n, e, _s in items)
            head = f'<h4 class="ex-set-h">{esc(title)}</h4>' if title else ""
            sets.append(f'<div class="ex-set">{head}<dl class="ex-types">{rows}</dl></div>')
        ask = wa_link(f"Hello, I would like a price for {g['name'].lower()}.")
        panels.append(
            f'<section class="ex-panel" id="{g["id"]}" aria-labelledby="t-{g["id"]}">'
            f'<div class="ex-head"><div class="ex-head-txt">'
            f'<h3 id="t-{g["id"]}">{esc(g["name"])}</h3><p>{esc(g["intro"])}</p>'
            f'<p class="ex-ask"><a class="btn btn-primary" href="{esc(ask)}">Get a price on WhatsApp</a>'
            f'<a class="text-link" href="tel:{SITE["phone_tel"]}">Or call {SITE["phone_display"]}</a></p>'
            f'</div>{media_html(g)}</div>{"".join(sets)}</section>')
    return f'<div class="explorer" data-explorer><div class="ex-index">{tabs}</div><div class="ex-panels">{"".join(panels)}</div></div>'


def schema_json():
    """LocalBusiness with confirmed NAP and hours only. No url or image until the
    domain serves, and never a self-collected rating (rule 112)."""
    data = {
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        "name": SITE["name"],
        "telephone": "+1-" + SITE["phone_display"],
        "address": {"@type": "PostalAddress", "streetAddress": "499 Ray Lawson Blvd, Unit 24",
                    "addressLocality": "Brampton", "addressRegion": "ON",
                    "postalCode": "L6Y 4E6", "addressCountry": "CA"},
        "openingHoursSpecification": [
            {"@type": "OpeningHoursSpecification",
             "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
             "opens": "10:30", "closes": "19:00"},
            {"@type": "OpeningHoursSpecification", "dayOfWeek": "Saturday",
             "opens": "12:00", "closes": "16:00"},
        ],
        "areaServed": ["Brampton", "Mississauga"],
        "knowsLanguage": ["en", "pa", "ur", "hi"],
        "hasOfferCatalog": {
            "@type": "OfferCatalog", "name": "Printing, signs and counter services",
            "itemListElement": [
                {"@type": "OfferCatalog", "name": g["name"],
                 "itemListElement": [{"@type": "Offer", "itemOffered": {"@type": "Service", "name": n}}
                                     for n, _e, _s in items_of(g)]}
                for g in GROUPS]},
    }
    return json.dumps(data, ensure_ascii=False, separators=(",", ":"))


def page():
    tel, wa = SITE["phone_tel"], SITE["whatsapp"]
    services = "".join(f'<div class="svc"><dt>{esc(n)}</dt><dd>{esc(e)}</dd></div>' for n, e, _s in SERVICES)
    reasons = "".join(f'<div class="why"><span class="why-ic">{svg}</span><h3>{esc(h)}</h3><p>{esc(p)}</p></div>'
                      for h, p, svg in REASONS)
    doors = "".join(
        f'<a class="door" href="#contact"><span class="door-img"><img {srcset("images/tiles/" + img, "door")} sizes="(min-width: 900px) 590px, 92vw" alt="" aria-hidden="true" loading="lazy" width="1600" height="1000"></span>'
        f'<span class="door-body"><small>{esc(kicker)}</small><h3>{esc(head)}</h3><span class="door-p">{esc(body)}</span>'
        f'<span class="door-go">{esc(cta)}</span></span></a>'
        for img, kicker, head, body, cta in DOORS)
    inds = "".join(
        f'<figure class="ind"><img {srcset("images/tiles/" + img, "ind")} sizes="(min-width: 1024px) 230px, (min-width: 640px) 42vw, 72vw" alt="{esc(name)}, sample image" loading="lazy" width="900" height="1200">'
        f'<figcaption><strong>{esc(name)}</strong><span>{esc(line)}</span></figcaption></figure>'
        for name, line, img in INDUSTRY_TILES)
    faq = "".join(f'<details class="qa"><summary>{esc(q)}</summary><div class="qa-a"><p>{esc(a)}</p></div></details>'
                  for q, a in FAQ)
    foot_products = "".join(f'<li><a href="#{g["id"]}">{esc(g["name"])}</a></li>' for g in GROUPS)
    foot_services = "".join(f'<li>{esc(n)}</li>' for n, _e, _s in SERVICES)
    n_groups = NUM_WORDS.get(len(GROUPS), str(len(GROUPS)))
    title = "AZ Printing &amp; Signs | Printing, signs and design in Brampton"
    # Kept under ~155 characters, where Google truncates a description.
    desc = ("Business cards, flyers, signs, banners, apparel and invitations from a family-run "
            f"print and sign shop in Brampton. Call {SITE['phone_display']}.")
    return f"""<!doctype html>
<html lang="en-CA">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{esc(desc)}">
<meta property="og:type" content="website">
<meta property="og:locale" content="en_CA">
<meta property="og:title" content="AZ Printing &amp; Signs, Brampton">
<meta property="og:description" content="{esc(desc)}">
<meta name="theme-color" content="#101820">
<script>document.documentElement.classList.add('js');setTimeout(function(){{document.documentElement.classList.add('js-failsafe')}},4000)</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Libre+Franklin:wght@400;500;600&display=swap">
<link rel="stylesheet" href="css/landing.css">
<link rel="icon" href="images/favicon-32.png" sizes="32x32">
<link rel="apple-touch-icon" href="images/apple-touch-icon.png">
<script type="application/ld+json">{schema_json()}</script>
</head>
<body>
<a class="skip" href="#products">Skip to products</a>

<div class="topbar">
  <div class="wrap topbar-in">
    <a href="{SITE['maps']}">{SITE['address']}</a>
    <span>{SITE['hours']}</span>
  </div>
</div>

<header class="head">
  <div class="wrap head-in">
    <a class="brand" href="#top"><img src="images/az-logo.png" alt="AZ" width="152" height="144"><span>Printing &amp; Signs</span></a>
    <nav class="nav" aria-label="Sections of this page">
      <a href="#products">Products</a>
      <a href="#services">Services</a>
      <a href="#about">About us</a>
      <a href="#faq">FAQ</a>
      <a href="#contact">Contact</a>
    </nav>
    <a class="btn btn-primary head-call" href="tel:{tel}"><span class="head-call-long">Call {SITE['phone_display']}</span><span class="head-call-short">Call</span></a>
  </div>
</header>

<main id="top">

<section class="hero" aria-labelledby="h-hero">
  <div class="wrap hero-in">
    <div class="hero-txt">
      <h1 id="h-hero">Put it in print.</h1>
      <p class="hero-sub">Business cards, signs, apparel and invitations from our shop in Brampton. Explain your order in English, Punjabi, Urdu or Hindi.</p>
      <p class="hero-ctas"><a class="btn btn-primary" href="tel:{tel}">Call {SITE['phone_display']}</a><a class="btn btn-line" href="{wa}">WhatsApp us</a></p>
    </div>
    <div class="hero-art">
      <span class="card-img ha-1"><img {srcset("images/products/banner.jpg", "products")} sizes="(min-width: 1024px) 600px, 92vw" alt="" aria-hidden="true" width="1200" height="750" fetchpriority="high"></span>
      <span class="card-img ha-2"><img {srcset("images/products/business-cards.jpg", "products")} sizes="(min-width: 1024px) 295px, 46vw" alt="" aria-hidden="true" width="1200" height="750"></span>
      <span class="card-img ha-3"><img {srcset("images/products/tshirt.jpg", "products")} sizes="(min-width: 1024px) 295px, 46vw" alt="" aria-hidden="true" width="1200" height="750"></span>
    </div>
  </div>
</section>

<section class="sec products" id="products" aria-labelledby="h-products">
  <div class="wrap">
    <div class="sec-head">
      <h2 id="h-products">Products we offer</h2>
      <p>{n_groups} categories of printing and signs from our shop in Brampton. Select a category to see its products, with a short explanation of each.</p>
    </div>
    {explorer_html()}
  </div>
</section>

<section class="sec band services" id="services" aria-labelledby="h-services">
  <div class="wrap services-in">
    <div class="services-intro">
      <h2 id="h-services">Services we offer</h2>
      <p>Design help, document services and shipping, at the same counter as your printing.</p>
      <figure class="card-img"><img {srcset("images/products/copier.jpg", "products")} sizes="(min-width: 1024px) 380px, 520px" alt="A document being placed on a copier and scanner" loading="lazy" width="1200" height="750"></figure>
    </div>
    <dl class="svc-list">{services}</dl>
  </div>
</section>

<section class="rush" aria-labelledby="h-rush">
  <div class="wrap rush-in">
    <div>
      <h2 id="h-rush">Need it today?</h2>
      <p>Some jobs may be ready the same day. Share your file, quantity and deadline before ordering so the shop can confirm what is possible.</p>
    </div>
    <p class="rush-ctas"><a class="btn btn-primary" href="tel:{tel}">Call the shop</a><a class="btn btn-ghost" href="{wa}">Ask on WhatsApp</a></p>
  </div>
</section>

<section class="sec about" id="about" aria-labelledby="h-about">
  <div class="wrap about-in">
    <div class="about-txt">
      <h2 id="h-about">The experience behind the counter</h2>
      <p>The owner of {SITE['name']} brings more than twenty years of printing experience to every order. He previously ran his own print and shipping store and printed for an agency.</p>
      <p>He took over the shop on Ray Lawson Blvd and put that experience behind his own counter. {SITE['area_line']}</p>
      <p><a class="btn btn-line" href="#contact">Come and see the shop</a></p>
    </div>
    <figure class="about-photo">
      <img {srcset("images/shop-storefront.jpg", "store")} sizes="(min-width: 1024px) 650px, 92vw" alt="The {SITE['name']} storefront on Ray Lawson Blvd in Brampton" loading="lazy" width="1400" height="1050">
    </figure>
  </div>
</section>

<section class="sec band expect" aria-labelledby="h-expect">
  <div class="wrap">
    <div class="sec-head"><h2 id="h-expect">What to expect</h2></div>
    <div class="why-grid">{reasons}</div>
  </div>
</section>

<section class="sec doors" aria-labelledby="h-doors">
  <div class="wrap">
    <h2 id="h-doors" class="sr-only">Business or personal</h2>
    <div class="doors-in">{doors}</div>
  </div>
</section>

<section class="sec band inds" aria-labelledby="h-inds">
  <div class="wrap">
    <div class="sec-head">
      <h2 id="h-inds">Who we print for</h2>
      <p>These are the trades that come through the door most often, not the only ones we print for. Tell us what you need and we will tell you how we would make it.</p>
    </div>
    <div class="ind-row">{inds}</div>
  </div>
</section>

<section class="sec faq" id="faq" aria-labelledby="h-faq">
  <div class="wrap faq-in">
    <div class="faq-intro">
      <h2 id="h-faq">Common questions</h2>
      <p>Another question? Call <a class="text-link" href="tel:{tel}">{SITE['phone_display']}</a>.</p>
    </div>
    <div class="qa-list">{faq}</div>
  </div>
</section>

<section class="sec band contact" id="contact" aria-labelledby="h-contact">
  <div class="wrap">
    <div class="sec-head"><h2 id="h-contact">Find us and get in touch</h2></div>
    <div class="contact-in">
      <div class="panel visit">
        <h3>Visit the shop in Brampton</h3>
        <p>Come in to compare materials and samples at the counter, or send your artwork ahead on WhatsApp.</p>
        <dl class="nap">
          <div><dt>Address</dt><dd><a class="text-link" href="{SITE['maps']}">{SITE['address']}</a></dd></div>
          <div><dt>Hours</dt><dd>Mon to Fri 10:30 to 7<br>Sat 12 to 4<br>Sun closed</dd></div>
          <div><dt>Phone and WhatsApp</dt><dd><a class="text-link" href="tel:{tel}">{SITE['phone_display']}</a></dd></div>
        </dl>
        <p class="visit-ctas"><a class="btn btn-line" href="{SITE['maps']}">Get directions</a><a class="btn btn-line" href="{wa}">Message us on WhatsApp</a><a class="btn btn-line" href="tel:{tel}">Call {SITE['phone_display']}</a></p>
      </div>
      <div class="panel quote">
        <h3>Tell us what you need</h3>
        <p>The fastest way to a price is a phone call, but if it is easier, leave your details and we will come back to you.</p>
        {form()}
      </div>
    </div>
  </div>
</section>

</main>

<footer class="foot">
  <div class="wrap foot-in">
    <div class="foot-brand">
      <p class="foot-name">{SITE['name']}</p>
      <p>{SITE['area_line']}</p>
      <p><a href="{SITE['maps']}">{SITE['address']}</a></p>
      <p>{SITE['hours']}</p>
      <p><a href="tel:{tel}">{SITE['phone_display']}</a> · <a href="{wa}">WhatsApp</a></p>
    </div>
    <div class="foot-col">
      <h2 class="foot-h">Products</h2>
      <ul>{foot_products}</ul>
    </div>
    <div class="foot-col">
      <h2 class="foot-h">Services</h2>
      <ul>{foot_services}</ul>
    </div>
  </div>
  <div class="wrap foot-base"><p>© 2026 {SITE['name']} · Brampton, Ontario</p></div>
</footer>

<div class="phone-bar" aria-label="Contact options">
  <a href="tel:{tel}">Call</a>
  <a href="{wa}">WhatsApp</a>
  <a class="pb-quote" href="#contact">Get a quote</a>
</div>
<script src="js/landing.js" defer></script>
</body>
</html>
"""


def form():
    """No backend is wired yet, and the form says so rather than pretending: the
    submit composes a WhatsApp message and hands it over. When the domain serves,
    wire a real endpoint and drop the fallback in js/landing.js."""
    tel = SITE["phone_tel"]
    return f"""<form class="quote-form" id="lp-form" data-fallback="{SITE['whatsapp']}">
          <div class="field-pair">
            <div class="field"><label for="lp-name">Your name <span class="req" aria-hidden="true">*</span></label>
              <input id="lp-name" name="name" type="text" required autocomplete="name"></div>
            <div class="field"><label for="lp-phone">Phone or WhatsApp <span class="req" aria-hidden="true">*</span></label>
              <input id="lp-phone" name="phone" type="tel" required autocomplete="tel"></div>
          </div>
          <div class="field"><label for="lp-job">What do you need printed?</label>
            <textarea id="lp-job" name="job" rows="4" placeholder="What it is, how many, and when you need it"></textarea></div>
          <button class="btn btn-primary" type="submit">Send on WhatsApp</button>
          <p class="form-note">This opens WhatsApp with your message ready to send. Prefer to talk? Call <a class="text-link" href="tel:{tel}">{SITE['phone_display']}</a>.</p>
        </form>"""


def fail(msg):
    print("BUILD FAILED: " + msg)
    sys.exit(1)


def verify(h):
    # Visible text only: <script> and <style> bodies are stripped first, because
    # the JSON-LD block is full of [arrays] that the bracket guard would
    # otherwise read as unconfirmed facts.
    body = re.sub(r"<(script|style)\b[^>]*>.*?</\1>", " ", h, flags=re.S)
    text = html.unescape(re.sub(r"<[^>]+>", " ", body))

    # THE RULE THIS BUILD ADDS: no bracketed unknowns on a page that goes public.
    for br in set(re.findall(r"\[[^\]\[]{2,90}\]", text)):
        fail(f"bracketed unknown reached the landing page: {br!r}")

    for bad in BANNED:
        if bad.lower() in text.lower():
            fail(f"banned string present: {bad!r}")

    if len(re.findall(r"<h1[ >]", h)) != 1:
        fail("must have exactly one h1")

    for img in re.findall(r"<img[^>]*>", h):
        m = re.search(r'alt="([^"]*)"', img)
        if m and m.group(1) == "" and 'aria-hidden="true"' in img:
            continue
        if not m or not m.group(1).strip():
            fail(f"img without alt: {img[:70]}")

    # EVERY LOCAL ASSET PATH MUST BE RELATIVE. GitHub Pages serves a project site
    # under a SUBPATH, so "/css/x.css" resolves to the domain root and 404s; the
    # first push went live with no stylesheet for exactly that reason.
    refs = re.findall(r'(?:src|href)="([^"#]+)"', h)
    for ss in re.findall(r'srcset="([^"]+)"', h):
        refs += [part.strip().split(" ")[0] for part in ss.split(",")]
    for src in refs:
        if src.startswith(("http://", "https://", "tel:", "mailto:", "#")):
            continue
        if src.startswith("/"):
            fail(f"absolute asset path {src!r}: a project site serves under a subpath")
        if not os.path.exists(os.path.join(HERE, src)):
            fail(f"asset missing on disk: {src}")

    ids = set(re.findall(r'\bid="([^"]+)"', h))
    for a in re.findall(r'href="#([^"]+)"', h):
        if a not in ids:
            fail(f"anchor #{a} points at nothing")
    dup = [i for i in ids if len(re.findall(rf'\bid="{re.escape(i)}"', h)) > 1]
    if dup:
        fail(f"duplicate ids: {dup}")

    for num in set(re.findall(r"\b\d{3}-\d{3}-\d{4}\b", text)):
        if num != SITE["phone_display"]:
            fail(f"unexpected phone number {num}")

    if "AZ+Printing" not in h:
        fail("the maps link lost the business name")
    if "prod-modal" in h or "add-quote" in h or "q-badge" in h or "cart" in text.lower():
        fail("ordering surface on the presence site")

    # CONTENT DOES NOT DEPEND ON JAVASCRIPT (rule 31). Panels ship visible and
    # the script hides the inactive ones, so a failed script shows everything.
    if re.search(r'class="ex-panel"[^>]*\shidden', h):
        fail("an explorer panel ships hidden; the script hides panels, the markup never does")
    if "classList.add('js')" not in h:
        fail("the js class hook is missing; the explorer CSS is gated on it")
    # The .js class hides panels 2-12 BEFORE the script has run, so a first paint
    # never flashes twelve stacked panels and then collapses them. If the script
    # then fails to load, the timed failsafe class shows everything (rule 31).
    if "js-failsafe" not in h:
        fail("the timed failsafe that reveals every panel if the explorer script never runs is missing")

    # THE CATALOGUE
    seen_ids, seen_names = set(), {}
    for g in GROUPS:
        if not re.fullmatch(r"[a-z0-9-]+", g["id"]) or g["id"] in seen_ids:
            fail(f"bad or duplicate group id {g['id']!r}")
        seen_ids.add(g["id"])
        if h.count(f'href="#{g["id"]}"') < 2:
            fail(f"group {g['id']} needs its explorer tab and its footer link")
        kind, ref, _label = g["media"]
        if kind == "img" and not os.path.exists(os.path.join(HERE, "images/products", ref)):
            fail(f"group {g['id']} image missing: {ref}")
        n_items = 0
        for title, items in g["sets"]:
            if len(g["sets"]) > 1 and not title:
                fail(f"group {g['id']} has several sets, so every set needs a title")
            for name, expl, src in items:
                n_items += 1
                if not name.strip() or not expl.strip():
                    fail(f"empty line in {g['id']}")
                if not expl.endswith("."):
                    fail(f"explanation must be a full sentence: {name}")
                if len(expl) > 150:
                    fail(f"explanation over 150 characters, which is a paragraph, not a line: {name}")
                tags = src.split("+")
                if not tags or any(t not in SOURCES for t in tags):
                    fail(f"unknown source tag {src!r} on {name}")
                key = name.lower()
                if key in seen_names:
                    fail(f"{name!r} is listed under both {seen_names[key]} and {g['id']}")
                seen_names[key] = g["id"]
        if n_items < 3:
            fail(f"group {g['id']} explains fewer than three products")
    for name, _e, src in SERVICES:
        if any(t not in SOURCES for t in src.split("+")):
            fail(f"unknown source tag on service {name}")
        if name.lower() in seen_names:
            fail(f"{name!r} is both a product and a service")

    n_faq = h.count("<details")
    if n_faq != len(FAQ) or h.count('class="qa-a"') != n_faq:
        fail("FAQ rows and answers disagree")

    total = sum(1 for g in GROUPS for _ in items_of(g))
    pending = sum(1 for g in GROUPS for _n, _e, s in items_of(g) if not set(s.split("+")) & CONFIRMED)
    print(f"verify OK: 1 page, {len(GROUPS)} product groups, {total} products explained "
          f"({pending} awaiting the owner's yes), {len(SERVICES)} services, "
          f"{len(FAQ)} questions, no bracketed unknowns")


def confirm_list():
    out = ["# AZ Printing & Signs: lines on the landing page awaiting the owner's yes",
           "",
           "Generated by `python3 build.py --confirm`. Everything else on the page is",
           "the owner's own word (his services answers, or his feedback of 2026-09-13).",
           ""]
    for g in GROUPS:
        rows = [(n, s) for n, _e, s in items_of(g) if not set(s.split("+")) & CONFIRMED]
        if not rows:
            continue
        out.append(f"## {g['name']}")
        for n, s in rows:
            why = "; ".join(SOURCES[t] for t in s.split("+"))
            out.append(f"- [ ] {n}  ({why})")
        out.append("")
    out.append("## Other facts on the page")
    for where, fact, why in PAGE_FACTS:
        out.append(f"- [ ] {fact}  ({where}; {why})")
    out.append("")
    return "\n".join(out)


if __name__ == "__main__":
    if "--confirm" in sys.argv:
        print(confirm_list())
        sys.exit(0)
    h = page()
    verify(h)
    if "--check" not in sys.argv:
        with open(os.path.join(HERE, "index.html"), "w") as f:
            f.write(h)
        print("wrote index.html")
