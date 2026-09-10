# AZ Printing & Signs — LANDING SITE (presence build)

A **separate deliverable** from the shop build in `../05 - Site/`. Fahad,
2026-09-09: the client wants an online presence now, **"not an ecommerce site
yet"**, and the shop launches later and is transitioned onto afterwards.

**One long page. Its only job is to make someone pick up the phone.**

```
python3 build.py           # build + verify
python3 build.py --check   # verify only
```
Preview: dev config **"az-landing"** (port 8804), serving this folder as root.

## Why it is its own build, not a mode of the shop generator

That was tried first and was the wrong shape. `generate.py --presence` strips
the ordering surface out of the shop build and leaves a 24-page catalogue with
the cart missing, which is not a landing page. The two share the **design**
(`css/site.css`, `js/site.js`, copied here) and the approved **copy**, which is
copied deliberately rather than imported — the two are expected to diverge.

The `--presence` mode still exists in the shop generator. It is **superseded by
this folder**; do not develop it further without Fahad saying so.

## The rule this build adds

**No bracketed unknowns.** `[$X]`, `[owner to confirm]` and friends are the shop
build's honest way of marking a fact nobody has confirmed, and they are fine on
a site that is noindexed and unlaunched. **This page is meant to go public**, so
`verify()` refuses to build if one survives. Where a fact is unknown here, the
sentence is left out instead — which is why the delivery-threshold reason and
the year the owner took over are both absent.

## Decisions that bind it

- **NINE BLOCKS AND A WHITE / GREY PATTERN** (Fahad 2026-09-09, exact order):
  hero (dark) · **Products we offer** (white) · Need it today (red) · the shop's
  story (white) · What to expect (grey) · For your event / business (white) ·
  Who we print for (grey) · Questions (white) · Find us (grey).
  **Two inherited bands are overridden to hold that beat**, both banded grey on
  the shop home earlier the same day: `.welcome` and `.doors`. If either is
  edited on the shop site, this page's pattern is unaffected — the overrides
  live in `landing.css` — but check the beat still alternates.
  **"Products we offer" is Fahad's wording.** It replaced a keyword-led heading;
  the location words moved into the lede beneath it so the page keeps them
  without overriding his choice.
- **What to expect uses the SHOP'S ICONS**, copied verbatim so the two sites
  cannot end up with subtly different drawings of the same idea.
  **Its delivery line drops a number the shop shows.** The shop reads "free
  delivery ... on orders over `[$250]`", and that bracket sits in its
  KNOWN_BRACKETS register next to `[$X]` — so from here a confirmed threshold
  and an unfilled placeholder are indistinguishable. This page goes public, and
  a wrong threshold costs the shop money on every order under it, so the fact
  stays and the number goes. **If Fahad confirms $250 is the owner's own figure,
  it is one edit to put back.**
- **The category tiles DO NOT LINK.** On a one-page site there is nowhere for
  them to go, and eight tiles pointing at the same anchor is noise pretending to
  be navigation. `landing.css` removes the pointer and the hover lift so they
  do not look clickable.
- **The header carries the wordmark** (Fahad 2026-09-09: the top looked empty).
  It is the shop's own `.brand` block, markup and all: monogram plus
  "Printing &amp; Signs". **Ampersand, never "and"** — that is the canonical
  name by Fahad's 2026-08-27 ruling, and this build's BANNED list refuses the
  drift spelling. The monogram's alt is just "AZ" so the name is not read twice.
  `site.css` hides `.brand-word` below 1100px because the SHOP'S tier-1 also
  carries a search field, three links, an account link, a cart and a phone
  number, and the name is the first thing that has to go there. **This bar has
  room**, so `landing.css` puts the word back down to 520px.
- **The header bar spans the FULL WIDTH, brand flush left** (Fahad 2026-09-09:
  "move AZ to the top left"). It used to be constrained to the centred content
  width like the sections below it, which left the logo 220px from the left edge
  at 1600 and 380px at 1920. The sections stay centred; a header bar is
  furniture, not content, and belongs to the window.
- **The maps link carries the BUSINESS NAME, not just the address.** An
  address-only query can land on the plaza rather than the unit. `verify()`
  refuses a build where the name has fallen out of it. Source: the Google
  Business Profile Fahad supplied 2026-09-09.
- **The header is a slim anchor bar**, not the shop's two-tier mega-nav. Four
  anchors do not earn a burger, so below 860px the nav hides entirely and the
  phone bar at the foot carries the actions.
- **Industries are the shop's PHOTO TILES**, imported with their pictures
  (Fahad 2026-09-09). An earlier note here said the photographs did not exist;
  that was wrong — they were wired into the shop build the same day.
  **The tiles are `<div>`s and every line stays permanently open.** On the shop
  site the line is revealed by `:hover` AND `:focus-visible` together, so
  keyboard users get it; a `<div>` cannot take focus, so that pairing would
  leave the copy reachable by mouse and invisible to everyone else. Do not
  restore the collapse without making the tiles focusable again.
  **THE SCRIM HAD TO BE REDRAWN FOR THAT, and it is the reason the collapse
  exists on the shop site.** There the resting caption is just the name, ~68px,
  and the scrim is tuned for it: `.90` opaque for the bottom 82px, gone by 214.
  Opening every line makes the caption reach 61-67% UP the tile, so its top rows
  landed in the faded tail over bright photograph. Measured, not guessed: **all
  five failed, worst 1.47:1**. The landing scrim holds `.90` to 42% and measures
  **7.61 to 10.31:1**. Percentages, not pixels, so it keeps covering the caption
  if the tile height changes. If the line copy grows, measure again.
- **The two doors are imported whole**, photographs and scrim, with only the
  destination changed: on the shop they open `/occasions/` and `/industries/`,
  and here there is one page, so both point at `#contact` with a label that
  says what they will do.
- **THE FORM HAS NO BACKEND AND DOES NOT PRETEND TO.** There is no domain, so
  FormSubmit cannot be activated, and a form that silently swallows a customer's
  details is worse than no form. Submitting builds a WhatsApp message from the
  fields and hands it over. **When a domain exists, wire a real endpoint and
  delete `js/landing.js`'s fallback.**

## Deployment

**Live:** https://mfahadishtiaq.github.io/az-printing-landing/ — repo
`mfahadishtiaq/az-printing-landing`, Pages from `main` at root. A window for
the client only; a real domain comes later.

**The real domain is decided: `azprintingandsigns.ca`** (2026-09-10, free at
CIRA that day; the short `azprinting.ca` was rejected because the domain must
match the store name, the cards and the Google listing). Plan, in order:
Cloudflare account on the CLIENT'S email (rule 120) -> register the domain
there in the business's name (CIRA legal type = the corporation if
incorporated, else the owner; auto-renew on) -> add Vela's email as a member
-> Workers & Pages, connect this repo, branch `main`, **no build command,
output `/`** -> custom domains apex + www (Cloudflare writes the DNS itself
because the zone is in the same account) -> Claude adds the www-to-root
redirect, verifies from outside (DoH, every asset, certificate) and makes the
old `github.io` link 301 to the domain. Why Cloudflare and not Squarespace:
no nameserver move, so no Squarespace-default DNSSEC/DS trap (ZEF lost a day
to it). A later move to Shopify is DNS only: A @ 23.227.38.65, CNAME www
shops.myshopify.com, both DNS-only (grey cloud) because Shopify issues its
own certificate. Fahad buys it himself; Claude never creates the account or
enters payment.

**EVERY LOCAL ASSET PATH IS RELATIVE, and must stay that way.** GitHub serves a
project site under a **subpath**, so `/css/site.css` resolves to the domain
ROOT and 404s — the first push went live with no stylesheet and no images.
`verify()` now refuses any absolute local path. Relative paths work under the
subpath AND at the root of a real domain later, so they are correct either way.

**The check that missed it is the lesson.** The assets were confirmed by asking
whether the FILE EXISTS on the server, with the subpath typed in by hand. The
question that mattered was whether the URL THE BROWSER WILL REQUEST resolves.
Fetch the page's own references, not paths you construct.

## Open

- **Hosting:** GitHub Pages until the owner sends his email address; then the
  Cloudflare plan under Deployment. `azprintingandsigns.com` (not .ca) is
  held by someone since 2023-03-02 with no site; the owner is being asked
  whether it is his (brief follow-up 19).
- **Still noindexed?** No — this build sets no robots tag, because it is meant
  to be found. The shop build's placeholder-image coupling does not apply here.
  Before it goes public, confirm every image on it is one AZ may use.
- The live page at `mfahadishtiaq.github.io/az-printing/` still serves the
  scrapped Direction F site **printing the retired 416 number**. It should be
  switched off whatever happens to this build.
