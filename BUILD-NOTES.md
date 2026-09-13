# AZ Printing & Signs — LANDING SITE: build notes (evidence)

The RULES are in `CLAUDE.md`. This file holds the evidence: what was measured,
tried and rejected, read only when touching that thing (context discipline,
2026-09-04).

## 2026-09-13 — client feedback round: the neutral redesign

### What the client said (relayed by Fahad)

- Incorrect terms used, products categorized under incorrect groups
- Create one landing page that demonstrates our services and provides information
- No need for an e-commerce aspect just yet, simply a digital presence
- Sub-categories need to be explained, for example business cards have multiple
  types: glossy, matte, etc.
- The design needs to be more sophisticated and neutral, similar to Staples

### What was wrong with the 09-09 page, concretely

The eight tiles named ONE product each while their lines described a whole
group, so the grouping was wrong in both directions:

| Tile (09-09) | Its line | What it actually is |
|---|---|---|
| Storefront signs | Lawn signs, storefront signs and vinyl banners | three families: Signs, Storefront Signs, Banners & Displays |
| Business cards | Business cards, letterheads, envelopes and forms | Business Cards + Stationery & Forms |
| Flyers | Handouts, folded brochures and larger posters | Marketing Materials; posters belong with banners |
| T-shirts | Single shirts, team orders and printed uniforms | Apparel (uniforms are EMBROIDERED per R2) |
| Printed mugs | Gifts and promotional items | Promotional Products |
| Canvas prints | Photos from your phone | Canvas & Photo Prints |
| Wedding cards | Invitations, signs and banners for the occasion | Invitations & Cards (event signs live in Signs) |

Missing entirely: storefront signage (channel letters, light boxes, pylons,
neon), vinyl graphics and wraps, NCR forms, stamps, and every counter service.
Two production claims were also false for outsourced apparel: "printed at our
Brampton shop" (hero) and "made or finished at the counter" (lede).

### Sources the new taxonomy was built from

1. **Staples Print Canada, read live 2026-09-13** (shop.staplescopyandprint.ca,
   whose header is an iframe at staplescopyandprint.ca/pages/iframe/header).
   Products menu, verbatim: Document Printing · Signs, Posters and Banners
   (Signs, Posters, Banners) · Business Cards · Marketing Materials (Brochures,
   Flyers, Postcards, Mailing and Organization Labels, Menus, Newsletters, Die
   Cut Stickers, Roll Labels, Promotional Products) · Photo Printing and
   Gifting · Cards and Invitations (Folded Cards, Flat Cards and Invitations,
   RSVP Cards, Enclosure Card, Postcards) · Labels · School Solutions · Decals ·
   Engineering Prints · Office and Stationery (Cheques and Forms, Envelopes,
   Letterhead, Name Plates and Badges, Notebooks, Notepads, Presentation
   Folders) · Stamps, Seals and Embossers. Services is a SEPARATE menu:
   In-Store (Passport and Visa Photos, Document Scanning, Photo Scanning, Fax,
   Shredding, Computer Rental, Shipping). Its signs page splits Banners
   (outdoor, hanging, L-stand, retractable) from Signs (A-frame, coroplast
   yard, flexible plastic, thick plastic, metal, acrylic, magnetic). Its
   business cards page has a "Special textures and finishes" block naming each
   finish with a one-line explanation, which is the shape the client asked for.
2. **Urgent Print (urgentprint.ca, GTA independent)** menu, for the local trade's
   words: Coroplast Signs, Foamboard, A Frames, Sandwich Boards, Channel Letters
   (front-lit, halo-lit), Light Box, Cloud Box, Neon, Cerlox and Spiral Binding.
3. **The owner's own window vinyls** (storefront photo 2026-08-27, zoomed and
   transcribed 2026-09-13): CHANNEL LETTERS · FLYERS · BANNERS · POSTCARDS ·
   BUSINESS CARDS · BOOKLETS · SIGN BOARDS · PYLON SIGNS · UV · SOFT TOUCH ·
   FOIL · INVOICES · LETTERHEADS · MENUS · VINYLS · STAMPS · LIGHT BOX ·
   REALTOR SIGNS · DOOR HANGERS · BROCHURES · MUGS · WALLPAPERS · FEATHER FLAGS
   · LAWN SIGNS · GREETING CARDS · STANDEES · PENS · STICKERS · WELCOME SIGNS ·
   HOODIES · DTF PRINT · CAPS · T-SHIRTS · EMBROIDERY · FOR SALE SIGNS · OPEN
   HOUSE SIGNS; left panels PHOTOSTAT · DESIGNING · SIGN BOARDS · BUSINESS
   BOARDS · PERFUMES · NEON SIGNS · BINDING · COURIER · MAILBOX · RESUME ·
   FLYERS · COURIER SERVICE · MAILBOX SERVICE; door SCAN · PRINT · COPY ·
   BINDING. UV, FOIL and SOFT TOUCH together are the business-card finish trio,
   which lines up with the client's "glossy, matte, etc."
4. **The owner's R2 services answers** (2026-08-23) and the R2 form's signs grid,
   which Fahad ruled all-in 2026-08-27 after the owner skipped it.

### Design register, measured on Staples' live CSS

TT Norms (TypeType, commercial) at MEDIUM weight: h1 40px/400-500, h2 32px/500,
body 16px/22.4px; heading ink rgb(16,24,32) = #101820 (Pantone Black 6 C); body
#444; card border 1px #D9D9D6 (Pantone Cool Gray 1 C), radius 8px; white
ground; red on the logo only. TT Norms cannot ship, and type was already ruled
(Libre Franklin, 2026-09-08), so the face stayed and the WEIGHT moved: the old
contract's 900 headings were poster register.

### Measurements

- Desktop 1440: 7,698px, no overflow, no broken images, no console output.
- Phone 375 (CDP gate): first build 11,162px = 13.7 screenfuls with 20 small
  targets. After tightening (services photo hidden on phone, icon-beside-text
  reasons, 2:1 door photos, two-column footer, 44px links): 10,405px, 3 small
  targets. After the top info bar went onto phones: 10,450px = 12.9. For
  comparison the 09-09 page measured 9,793px on the L1 board, so the page grew
  ~7% while going from 8 one-line tiles to 62 explained products + 8 services.
- Width sweep 390 / 768 / 1024 / 1180 / 1280 / 1366 / 1600 / 1920: scrollWidth
  equals innerWidth at every width.
- Page weight if every image loads: 3.18MB of image files referenced, ~2.5MB on
  a full scroll (hidden panels never load theirs). The heavy files were the
  09-09 carry-overs: storefront 452KB, five industry tiles ~930KB, two doors
  ~450KB, all served 2.5-4x their display size. With srcset variants: industry
  tiles 406KB for all five at 560w, doors 218KB at 900w, storefront 123KB at
  900w, product renders 15-46KB at 800w. No image is served above 2.2x its
  display size at 2x DPR (phone gate).

### Things that broke first

- **Five explorer checks failed on the first run, and the page was fine.** The
  click helper measured the target in the same tick as scrollIntoView, and the
  page sets scroll-behavior:smooth, so it clicked where the element USED to be.
  Fixed by scrolling instantly, waiting, then measuring. The footer check then
  failed for a second reason: a 6,000px smooth scroll outlasts a fixed 0.5s
  sample. It now polls for the end state.
- **A red ring round the panel on a deep link.** Panels carried tabindex=0, so
  /#stationery-forms focused the panel on arrival and :focus-visible drew the
  ring. Every panel already contains buttons, so the tabindex was removed.
- **An f-string ate the failsafe script's braces** (NameError on `document`).
- **ffmpeg's crop=1:1 fails on 4:2:0 JPEGs** (chroma subsampling); sample with
  format=rgb24,crop=2:2.
- **The proofs**: with js/landing.js removed the explorer gate fails 8 checks
  (and all 12 panels still showed); verify() refused an injected "printed at our
  shop", a panel shipped with `hidden`, and the retired word "Handouts".

### web-critic, 2026-09-13: REWORK, then SHIP

Blocking, all fixed: unconfirmed details inside confirmed lines (Spot UV
"raised", canvas "stretched over a wooden frame", "wall and desk" calendars,
mailbox "and parcels"); "Coroplast Signs" leading with the material where the
owner's window says LAWN SIGNS; "Sign Installation" filed as a product. Worth
fixing, all fixed: the pre-script panel flash and the missing failsafe; address
and hours 8,400px down on a phone; three bordered-card sections running;
oversized images; a ~170-character meta description; a tenth WhatsApp mention
(rule 48); page-level provisional facts missing from the owner list. Put to
Fahad instead of fixed: rule 26 page length, and rule 82 ("He") in the approved
About copy.

---

## The CLAUDE.md as it stood before the redesign (2026-09-10), verbatim

Superseded by the 2026-09-13 round. Kept whole so nothing is lost; the rules
that still hold were carried into the new CLAUDE.md.

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

**`azprintingandsigns.ca` is BOUGHT (2026-09-10)** in the client's Cloudflare
account: expires 2027-09-11, auto-renew on, Cloudflare nameservers. It was free at
CIRA that day; the short `azprinting.ca` was rejected because the domain must
match the store name, the cards and the Google listing). Plan, in order:
Cloudflare account on the CLIENT'S email (rule 120) -> register the domain
there in the business's name (CIRA legal type = the corporation if
incorporated, else the owner; auto-renew on) -> add Vela's email as a member
-> Workers & Pages serving an **ALLOWLIST of built files only** (see the
warning below; NOT this repo root) -> custom domains apex + www (Cloudflare writes the DNS itself
because the zone is in the same account) -> Claude adds the www-to-root
redirect, verifies from outside (DoH, every asset, certificate) and makes the
old `github.io` link 301 to the domain. Why Cloudflare and not Squarespace:
no nameserver move, so no Squarespace-default DNSSEC/DS trap (ZEF lost a day
to it). A later move to Shopify is DNS only: A @ 23.227.38.65, CNAME www
shops.myshopify.com, both DNS-only (grey cloud) because Shopify issues its
own certificate. Fahad buys it himself; Claude never creates the account or
enters payment.

**THIS REPO IS PUBLIC AND GITHUB PAGES SERVES EVERY FILE IN IT.** Checked
2026-09-10: `/CLAUDE.md` and `/build.py` both return 200 on the live github.io
site, so these internal notes are world-readable. Pointing Cloudflare Pages at
the repo root with output `/` would publish them on the client's own domain.
**Before hosting is connected**, split it the way ZEF does: this folder's repo
goes private, and a deploy script copies an ALLOWLIST (index.html, css/, js/,
images/, favicons, robots.txt) into a separate public repo or output folder that
Pages serves. Keep it an allowlist; "everything except X" is how the next new
script ends up public.

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
