#!/usr/bin/env python3
"""AZ Printing & Signs — LANDING SITE (presence build, 2026-09-09).

A SEPARATE deliverable from the shop build in `05 - Site/`. Fahad, 2026-09-09:
the client wants an online presence now, "not an ecommerce site yet", and the
shop launches later. This is one long page whose only job is to make someone
pick up the phone.

WHY IT IS ITS OWN BUILD, not a mode of the shop generator: the shop generator
emits 25 catalogue pages around a product configurator, and stripping that back
produced a 24-page catalogue with the cart missing, which is not what a landing
page is. Different shape, different build. The two share the DESIGN (css/, js/)
and the approved COPY, which is copied here deliberately rather than imported,
because the two are expected to diverge.

ONE RULE THIS BUILD ENFORCES THAT THE SHOP BUILD DOES NOT: no bracketed
unknowns. `[$X]`, `[owner to confirm]` and friends are the shop build's honest
way of marking a fact nobody has confirmed, and they are fine on a site that is
noindexed and unlaunched. This page is meant to go public, so verify() refuses
to build if one survives. Where a fact is unknown, the sentence is left out.

    python3 build.py            build + verify
    python3 build.py --check    verify only
"""
import html
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

SITE = {
    "name": "AZ Printing & Signs",
    "phone_display": "905-796-1515",
    "phone_tel": "9057961515",
    "whatsapp": "https://wa.me/19057961515",
    "address": "499 Ray Lawson Blvd, Unit 24, Brampton, ON L6Y 4E6",
    "maps": "https://maps.google.com/?q=499+Ray+Lawson+Blvd+Unit+24+Brampton+ON+L6Y+4E6",
    "hours": "Mon to Fri 10:30 to 7 · Sat 12 to 4 · Sun closed",
    "area_line": "A family-run print and sign shop serving Brampton, Mississauga and the GTA.",
}

# Copied from the approved shop build, not rewritten. The tiles do NOT link:
# on a one-page site there is nowhere for them to go, and eight tiles all
# pointing at the same anchor is noise pretending to be navigation.
CATEGORIES = [
    ("Storefront signs", "Lawn signs, storefront signs and vinyl banners.", "tile-signs-banners.jpg"),
    ("Business cards", "Business cards, letterheads, envelopes and forms.", "tile-business-cards.jpg"),
    ("Flyers", "Handouts, folded brochures and larger posters.", "tile-flyers-posters.jpg"),
    ("Stickers", "Labels and stickers cut to the shape you need.", "tile-stickers-labels.jpg"),
    ("T-shirts", "Single shirts, team orders and printed uniforms.", "tile-apparel.jpg"),
    ("Canvas prints", "Photos from your phone, printed for a frame or wall.", "tile-photo-canvas.jpg"),
    ("Printed mugs", "Gifts and promotional items printed with your name or logo.", "tile-promo-gifts.jpg"),
    ("Wedding cards", "Invitations, signs and banners for the occasion.", "tile-wedding-cards.jpg"),
]

# The shop build's four reasons, with ITS icons (Fahad 2026-09-09: "the same
# symbols used on the other website"). The SVGs are copied verbatim so the two
# sites cannot end up with subtly different drawings of the same idea.
#
# ONE LINE IS REWRITTEN, and the reason matters. The shop's delivery reason
# reads "free delivery ... on orders over [$250]". That bracket is in its
# KNOWN_BRACKETS register alongside "[$X]", so from here a real confirmed
# threshold and an unfilled placeholder look identical. This page GOES PUBLIC,
# and publishing a delivery threshold that turns out to be wrong costs the shop
# money on every order under it. So the fact stays and the number goes. If Fahad
# confirms $250 is the owner's own figure, it is one edit to put back.
REASONS = [
    ("Order again without starting over",
     "Your approved artwork stays on file, so repeat orders can begin with a phone call, even years later.",
     """<svg viewBox="0 0 56 56" aria-hidden="true"><rect x="16" y="6" width="24" height="18" fill="#FFFFFF" stroke="#1A1A1A" stroke-width="2.5"/><line x1="21" y1="12" x2="35" y2="12" stroke="#1A1A1A" stroke-width="2.5"/><line x1="21" y1="17" x2="31" y2="17" stroke="#1A1A1A" stroke-width="2.5"/><path d="M5 16h14l4 5h28v27H5z" fill="#FFA347" stroke="#1A1A1A" stroke-width="2.5" stroke-linejoin="round"/></svg>"""),
    ("Order the quantity you need",
     "One shirt or a thousand flyers, both are welcome at the counter.",
     """<svg viewBox="0 0 56 56" aria-hidden="true"><rect x="8" y="8" width="26" height="34" fill="#FFFFFF" stroke="#1A1A1A" stroke-width="2.5"/><rect x="13" y="13" width="26" height="34" fill="#FFFFFF" stroke="#1A1A1A" stroke-width="2.5"/><rect x="34" y="32" width="15" height="18" fill="#A01D20" stroke="#1A1A1A" stroke-width="2.5"/></svg>"""),
    ("Choose pickup or delivery",
     "Pick up on Ray Lawson Blvd, or ask about delivery across Brampton and Mississauga.",
     """<svg viewBox="0 0 56 56" aria-hidden="true"><rect x="4" y="16" width="30" height="22" fill="#8C161A" stroke="#1A1A1A" stroke-width="2.5"/><path d="M34 22h10l8 8v8H34z" fill="#8C161A" stroke="#1A1A1A" stroke-width="2.5" stroke-linejoin="round"/><rect x="37" y="25" width="7" height="6" fill="#FFFFFF" stroke="#1A1A1A" stroke-width="2"/><circle cx="14" cy="41" r="5" fill="#FFFFFF" stroke="#1A1A1A" stroke-width="2.5"/><circle cx="42" cy="41" r="5" fill="#FFFFFF" stroke="#1A1A1A" stroke-width="2.5"/></svg>"""),
    ("Approve the proof first",
     "We send a proof for your approval before printing begins.",
     """<svg viewBox="0 0 56 56" aria-hidden="true"><rect x="10" y="6" width="28" height="38" fill="#FFFFFF" stroke="#1A1A1A" stroke-width="2.5"/><line x1="16" y1="14" x2="32" y2="14" stroke="#1A1A1A" stroke-width="2.5"/><line x1="16" y1="21" x2="32" y2="21" stroke="#1A1A1A" stroke-width="2.5"/><line x1="16" y1="28" x2="26" y2="28" stroke="#1A1A1A" stroke-width="2.5"/><circle cx="40" cy="40" r="11" fill="#FFA347" stroke="#1A1A1A" stroke-width="2.5"/><path d="M35 40l4 4 7-8" fill="none" stroke="#1A1A1A" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg>"""),
]

INDUSTRY_TILES = [
    ("Real estate", "The listing goes live Thursday and the sign has to be on the lawn first.", "ind-real-estate.jpg"),
    ("Restaurants", "A menu gets handled more than anything else we print.", "ind-restaurants.jpg"),
    ("Professional services", "The folder that leaves the meeting, the letterhead under the agreement.", "ind-offices.jpg"),
    ("Construction & trades", "The site sign, the truck door, the invoice book.", "ind-construction.jpg"),
    ("Community & religious organizations", "Banner up Friday, programs ready Sunday.", "ind-community.jpg"),
]

# The two doors, photographs and all. Their CTAs change: on the shop site they
# open /occasions/ and /industries/, and here there is only one page, so each
# points at the contact block with a label that says what it will do.
DOORS = [
    ("d-event", "door-event.jpg", "The day you're planning", "For your event",
     "Choose invitations, welcome signs and banners for weddings, birthdays and community events. Visit the shop to compare materials and samples in person.",
     "Ask about event printing"),
    ("d-biz", "door-business.jpg", "The name you're building", "For your business",
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
          "hi-vis", "workwear", "notary", "Learn More", "Submit"]


def page():
    cats = "".join(
        f'<div class="cat-card"><span class="cat-face">'
        f'<img src="/images/tiles/{img}" alt="{html.escape(name)}, sample image" loading="lazy"></span>'
        f'<span class="cat-name">{name}</span><span class="cat-blurb">{blurb}</span></div>'
        for name, blurb, img in CATEGORIES)
    reasons = "".join(
        f'<div class="why-col">{svg}<h3>{h}</h3><p>{p}</p></div>' for h, p, svg in REASONS)
    inds = "".join(
        f'<div class="ind-tile">'
        f'<img src="/images/tiles/{img}" alt="{html.escape(name)}, sample image" loading="lazy" width="900" height="1200">'
        f'<span class="ind-cap"><span class="ind-name">{name}</span>'
        f'<span class="ind-more"><span class="ind-line">{line}</span></span></span></div>'
        for name, line, img in INDUSTRY_TILES)
    doors = "".join(
        f'<a class="door {cls}" href="#contact">'
        f'<img class="door-bg" src="/images/tiles/{img}" alt="" aria-hidden="true" loading="lazy" width="1600" height="1000">'
        f'<small>{eyebrow}</small><h3>{head}</h3><p>{body}</p>'
        f'<span class="door-go">{cta}</span></a>'
        for cls, img, eyebrow, head, body, cta in DOORS)
    faq = "".join(
        f'<details class="qa-item"><summary>{q}</summary><div class="qa-a"><p>{a}</p></div></details>'
        for q, a in FAQ)
    tel, wa = SITE["phone_tel"], SITE["whatsapp"]
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AZ Printing &amp; Signs | Printing and signs in Brampton</title>
<meta name="description" content="Business cards, signs, flyers, apparel and invitations printed at a family-run shop on Ray Lawson Blvd in Brampton. Call {SITE['phone_display']}.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Libre+Franklin:ital,wght@0,400;0,700;0,800;0,900;1,400&display=swap">
<link rel="stylesheet" href="/css/site.css">
<link rel="stylesheet" href="/css/landing.css">
<link rel="icon" href="/images/favicon-32.png" sizes="32x32">
<link rel="apple-touch-icon" href="/images/apple-touch-icon.png">
</head>
<body data-page="/">
<a class="skip" href="#print">Skip to what we print</a>

<header class="lp-head">
  <div class="lp-head-in">
    <a class="brand" href="#top"><img src="/images/az-logo.png" alt="AZ" width="152" height="144"><span class="brand-word">Printing &amp; Signs</span></a>
    <nav class="lp-nav" aria-label="Sections of this page">
      <a href="#print">What we print</a>
      <a href="#story">The shop</a>
      <a href="#faq">Questions</a>
      <a href="#contact">Find us</a>
    </nav>
    <a class="btn btn-primary lp-call" href="tel:{tel}">Call {SITE['phone_display']}</a>
  </div>
</header>

<main id="top">

<section class="hero">
  <img class="hero-bg" src="/images/hero-press-1920.jpg" alt="" aria-hidden="true" width="1920" height="1080">
  <div class="hero-in">
    <h1>Put it in print.</h1>
    <p class="hero-sub">Business cards, signs, apparel and invitations, printed at our Brampton shop. Explain your order in English, Punjabi, Urdu or Hindi.</p>
    <p class="hero-ctas"><a class="btn btn-primary" href="tel:{tel}">Call {SITE['phone_display']}</a> <a class="btn btn-line" href="{wa}">WhatsApp us</a></p>
  </div>
</section>

<section class="cat-ads" id="print" aria-labelledby="h-print">
  <h2 id="h-print">Products we offer</h2>
  <p class="lp-lede">Printing and signs for Brampton, made or finished at the counter on Ray Lawson Blvd.</p>
  <div class="cat-grid">{cats}</div>
</section>

<section class="lp-rush" aria-labelledby="h-rush">
  <div class="lp-rush-in">
    <h2 id="h-rush">Need it today?</h2>
    <p>Some jobs may be ready the same day. Share your file, quantity and deadline before ordering so the shop can confirm what is possible.</p>
    <p class="cta-row"><a class="btn btn-primary" href="tel:{tel}">Call the shop</a> <a class="btn btn-line" href="{wa}">Ask on WhatsApp</a></p>
  </div>
</section>

<section class="welcome" id="story" aria-labelledby="h-story">
  <div class="welcome-grid">
    <div class="welcome-txt">
      <h2 id="h-story">The experience behind the counter</h2>
      <p>The owner of {SITE['name']} brings more than twenty years of printing experience to every order. He previously ran his own print and shipping store and printed for an agency.</p>
      <p>He took over the shop on Ray Lawson Blvd and put that experience behind his own counter. {SITE['area_line']}</p>
      <p class="cta-row"><a class="btn btn-line" href="#contact">Come and see the shop</a></p>
    </div>
    <figure class="welcome-photo">
      <img src="/images/shop-storefront.jpg" alt="The {SITE['name']} storefront on Ray Lawson Blvd in Brampton" loading="lazy">
    </figure>
  </div>
</section>

<section class="why-cols" aria-labelledby="h-why">
  <h2 id="h-why">What to expect</h2>
  <div class="why-grid">{reasons}</div>
</section>

<section class="doors" aria-labelledby="h-doors">
  <h2 id="h-doors" class="sr-only">Business or personal</h2>
  <div class="doors-in">{doors}</div>
</section>

<section class="ind-home" aria-labelledby="h-inds">
  <h2 id="h-inds">Who we print for</h2>
  <div class="ind-row">{inds}</div>
  <p class="lp-ind-note">These are the trades that come through the door most often, not the only ones we print for. Tell us what you need and we will tell you how we would make it.</p>
</section>

<section class="mini-faq" id="faq" aria-labelledby="h-faq">
  <h2 id="h-faq">Common questions</h2>
  <div class="qa-acc">{faq}</div>
</section>

<section class="closing" id="contact" aria-labelledby="h-close">
  <h2 id="h-close" class="sr-only">Find us and get in touch</h2>
  <div class="closing-in">
    <div class="close-visit">
      <h3>Visit the shop in Brampton</h3>
      <p>Come in to compare materials and samples at the counter, or send your artwork ahead on WhatsApp.</p>
      <p class="visit-nap">{SITE['address']}<br>{SITE['hours']}</p>
      <p class="cta-row"><a class="btn btn-line" href="{SITE['maps']}">Get directions</a><a class="btn btn-line" href="{wa}">Message us on WhatsApp</a><a class="btn btn-line" href="tel:{tel}">Call {SITE['phone_display']}</a></p>
    </div>
    <div class="close-quote">
      <h3>Tell us what you need</h3>
      <p>The fastest way to a price is a phone call, but if it is easier, leave your details and we will come back to you.</p>
      {form()}
    </div>
  </div>
</section>

</main>

<footer class="site-foot">
  <div class="foot-in">
    <div>
      <p class="foot-name">{SITE['name']}</p>
      <p>{SITE['area_line']}</p>
      <p>{SITE['address']}</p>
      <p>{SITE['hours']}</p>
      <p><a href="tel:{tel}">{SITE['phone_display']}</a> · <a href="{wa}">WhatsApp</a></p>
    </div>
  </div>
</footer>

<div class="phone-bar" aria-label="Contact options">
  <a href="tel:{tel}">Call</a>
  <a href="{wa}">WhatsApp</a>
  <a class="pb-quote" href="#contact">Get a quote</a>
</div>
<script src="/js/landing.js" defer></script>
</body>
</html>
"""


def form():
    """No backend is wired yet, and the form says so rather than pretending.

    The shop build posts to FormSubmit, which needs per-domain activation; this
    site has no domain yet. A form that silently swallows a customer's details
    is worse than no form, so the action is left unset and the JS turns it into
    a WhatsApp message instead. When a domain exists, wire the endpoint and drop
    the fallback.
    """
    tel = SITE["phone_tel"]
    return f"""<form class="quote-form" id="lp-form" data-fallback="{SITE['whatsapp']}">
  <div class="field-pair">
    <div class="field"><label for="lp-name">Your name <span class="req" aria-hidden="true">*</span></label>
      <input id="lp-name" name="name" type="text" required autocomplete="name"></div>
    <div class="field"><label for="lp-phone">Phone or WhatsApp <span class="req" aria-hidden="true">*</span></label>
      <input id="lp-phone" name="phone" type="tel" required autocomplete="tel"></div>
  </div>
  <div class="field"><label for="lp-job">What do you need printed?</label>
    <textarea id="lp-job" name="job" rows="3" placeholder="What it is, how many, and when you need it"></textarea></div>
  <button class="btn btn-primary send" type="submit">Send on WhatsApp</button>
  <p class="form-privacy">This opens WhatsApp with your message ready to send. Prefer to talk? Call <a href="tel:{tel}">{SITE['phone_display']}</a>.</p>
</form>"""


def fail(msg):
    print("BUILD FAILED: " + msg)
    sys.exit(1)


def verify(h):
    text = re.sub(r"<[^>]+>", " ", h)

    # THE RULE THIS BUILD ADDS. The shop build marks an unconfirmed fact with a
    # bracket and stays noindexed; this page is meant to go public, so a bracket
    # surviving to launch would put "[owner to confirm]" in front of a customer.
    # Where a fact is unknown here, the sentence is left out instead.
    for br in set(re.findall(r"\[[^\]\[]{2,90}\]", text)):
        fail(f"bracketed unknown reached the landing page: {br!r} — this build ships")

    for bad in BANNED:
        if bad in text:
            fail(f"banned string present: {bad!r}")

    if len(re.findall(r"<h1[ >]", h)) != 1:
        fail("must have exactly one h1")

    for img in re.findall(r"<img[^>]*>", h):
        m = re.search(r'alt="([^"]*)"', img)
        if m and m.group(1) == "" and 'aria-hidden="true"' in img:
            continue
        if not m or not m.group(1).strip():
            fail(f"img without alt: {img[:70]}")

    # every local asset must exist, or the page ships with holes
    for src in re.findall(r'(?:src|href)="(/[^"]+)"', h):
        if not os.path.exists(os.path.join(HERE, src.lstrip("/"))):
            fail(f"asset missing on disk: {src}")

    # every in-page anchor must land somewhere
    for a in re.findall(r'href="#([a-z-]+)"', h):
        if f'id="{a}"' not in h:
            fail(f"anchor #{a} points at nothing")

    for num in set(re.findall(r"\b\d{3}-\d{3}-\d{4}\b", text)):
        if num != SITE["phone_display"]:
            fail(f"unexpected phone number {num}")

    if "prod-modal" in h or "add-quote" in h or "q-badge" in h:
        fail("ordering surface on the presence site")

    n_faq = h.count("<details")
    if n_faq != len(FAQ) or h.count('class="qa-a"') != n_faq:
        fail("FAQ rows and answers disagree")

    print(f"verify OK: 1 page, {len(CATEGORIES)} categories, {len(INDUSTRY_TILES)} industry tiles, "
          f"{len(FAQ)} questions, {len(DOORS)} doors, no bracketed unknowns")


if __name__ == "__main__":
    h = page()
    verify(h)
    if "--check" not in sys.argv:
        with open(os.path.join(HERE, "index.html"), "w") as f:
            f.write(h)
        print("wrote index.html")
