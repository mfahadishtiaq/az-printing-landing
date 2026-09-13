# AZ Printing & Signs — LANDING SITE (presence build)

A **separate deliverable** from the shop build in `../05 - Site/`. The client wants
an online presence now, **not an e-commerce site**; the shop launches later.
**One page that shows everything the shop does and tells a visitor how to reach it.**

```
python3 build.py             # build + verify
python3 build.py --check     # verify only
python3 build.py --confirm   # the owner confirm list (markdown)
node test/explorer.js        # explorer gate, 20 checks (needs the dev server)
```
Preview: dev config **"az-landing"** (port 8804), serving this folder as root.
Phone gate: `node ../05\ -\ Site/test/qa-mobile.js http://localhost:8804/ <outDir> index.html`.

Evidence for everything below (research, measurements, what broke):
**`BUILD-NOTES.md`**. Read the heading you need, not the whole file.

## THE 2026-09-13 CLIENT RULINGS — the page was rebuilt on these

The client (relayed by Fahad): incorrect terms, products under the wrong groups;
one landing page that demonstrates the services and gives information; no
e-commerce; **sub-categories explained** ("business cards have multiple types,
glossy, matte, etc."); **design more sophisticated and neutral, similar to
Staples**. These are the client's own choices (rule 66). They supersede, FOR
THIS SITE, the "pop" direction and the "show the range in many colours" note.

Restore point for the page before this round: git tag
**`pre-neutral-redesign-2026-09-13`**.

## THE CATALOGUE — rules that keep the terms right

- **Twelve product groups, trade-standard, in the order of `GROUPS`.** Grouping
  follows Staples Print Canada's live menu (read 2026-09-13) and the GTA trade.
  **Products and services are separate lists**: a service filed inside a product
  group ("Sign Installation" under Storefront Signs) was exactly the complaint.
- **A product NAME is the trade's word, and the owner's where he has one.** His
  window says LAWN SIGNS, so the product is Lawn Signs and "coroplast" is
  explained inside the line, never the other way round. Friendly paraphrases
  ("Handouts", "printed mugs" for all promo products) are what the client called
  incorrect terms. Rule 20 governs the explanation, not the name.
- **Every item carries a source tag** (`owner` · `client` · `window` · `signs` ·
  `std`). `owner`/`client` are the owner's own word; the rest print on
  `--confirm`. verify() refuses an unknown tag.
- **No production detail the owner has not given** inside a line: no "raised"
  Spot UV, no "stretched over a wooden frame", no "wall and desk" calendars. The
  owner confirmed the PRODUCT; the specifics are his to add.
- verify() also refuses: a name listed in two groups or as both product and
  service; an explanation that is not a full sentence or runs past 150
  characters; a group with fewer than three products; a set without a title in
  a multi-set group; a group with no footer link.
- **Production claims are banned words** (`printed at our`, `printed here`,
  `made or finished`, `in-house`…). Apparel is sent out (brief v2); say a job is
  ordered, handled or delivered here, never that everything is printed here.
- **No bracketed unknowns** on a page that goes public. Where a fact is unknown,
  the sentence is left out.
- **Window items deliberately NOT on the page:** Resume, Business Boards,
  Perfumes (unclear or not print). They are questions on the confirm list.

## DESIGN — the Staples register, sourced

- **Standalone `css/landing.css`.** `css/site.css` and `js/site.js` are the shop
  build's copies from 09-09 and are NOT loaded; they sit on disk as the record.
- **Inks, each with its source (rule 56):** ink #101820 Pantone Black 6 C and
  rule #D9D9D6 Pantone Cool Gray 1 C (both Staples' live CSS); body #343B41;
  muted #53565A Cool Gray 11 C; band #F6F6F5; field #888B8D Cool Gray 8 C; red
  #A01D20 / #8C161A from the AZ brand PDF. **Red is the only colour doing work**
  (buttons, active tab, focus). Amber is in the logo and nowhere else.
- **Type stays Libre Franklin (ruled 09-08); the weights moved**: headings 600,
  labels 500, body 400. Do not restore the 900 poster weights here.
- **Hero art is general**: no cultural-occasion card in the hero (rule 54). The
  nikkah invitation is used nowhere on the page today.
- **Industry photos have no card frame**, on purpose: What to expect and the
  doors are bordered boxes, and a third in a row read as one repeated skeleton.

## THE EXPLORER — mechanics and traps

- **Markup ships every panel visible; the index is jump links.** With scripting
  off the whole catalogue reads top to bottom (tested).
- **`.js` (set in the head) hides panels 2-12 BEFORE the script runs**, so a slow
  first paint never flashes twelve panels and collapses them. **The head's 4s
  timer adds `.js-failsafe`**, which shows them all again if `js/landing.js`
  never runs. The script adds `.ex-ready` and from then the `hidden` attribute
  owns visibility. Remove the failsafe and a blocked script hides eleven groups
  forever; verify() refuses a build without it.
- **No `tabindex` on panels.** With it, a link such as `/#signs` focused the
  panel on arrival and drew a red focus ring round it. Panels already hold
  buttons, so the ARIA pattern does not need it.
- Deep links and footer links work through the hash: `#business-cards` opens
  that group on load, and `hashchange` handles same-page links.
- **The phone chip row is sticky under the header.** Its ancestors must not
  clip; `overflow:hidden` anywhere above it silently kills sticky.
- **Test trap:** the page sets `scroll-behavior:smooth`, so a test that measures
  an element in the same tick as `scrollIntoView` clicks where it USED to be.
  Scroll instantly, wait, then measure; poll for end states after long scrolls.

## IMAGES

- **Every photo has a right-sized variant and a `srcset`** (`VARIANTS` in
  build.py): products `-800`, industry tiles `-560` (q 6), doors and storefront
  `-900`. **Replacing a photo means regenerating its variant** (ffmpeg lanczos,
  `-q:v 4`), or the browser keeps serving the old picture at small sizes. verify()
  fails a srcset naming a missing file. `window-graphics.jpg` has no variant: it
  is a 730px crop of the storefront photo, and upscaling would only add bytes.
- **Stationery & Forms has no render**; its panel draws a flat SVG mock-up
  (letterhead, envelope, white/yellow/pink NCR book) in `stationery_svg()`. A
  photo slot at 1200x750 on white would replace it.
- Every product render is a SAMPLE design (alt text says so); none is presented
  as a client's job (rule 30).

## Still true from the 09-09 build

- **The maps link carries the BUSINESS NAME**; an address-only query can land on
  the plaza. verify() refuses a build without it.
- **EVERY LOCAL ASSET PATH IS RELATIVE**, srcset included. GitHub serves a project
  site under a subpath, so `/css/x.css` 404s; the first push shipped with no CSS.
  Check the URL the browser will request, not a path you typed.
- **THE FORM HAS NO BACKEND AND DOES NOT PRETEND TO.** Submit composes a WhatsApp
  message. When the domain serves, wire a real endpoint and delete the fallback.
- **Ampersand, never "and", in the name.** BANNED refuses the drift spelling.

## Deployment

**Live preview (still the 09-10 page until pushed):**
https://mfahadishtiaq.github.io/az-printing-landing/ — repo
`mfahadishtiaq/az-printing-landing`, Pages from `main` at root.

**`azprintingandsigns.ca` is BOUGHT (2026-09-10)** in the client's Cloudflare
account: expires 2027-09-11, auto-renew on, Cloudflare nameservers. Plan, in
order: add Vela's email as an account member (rule 120) -> Workers & Pages
serving an **ALLOWLIST of built files only** -> custom domains apex + www -> Claude
adds the www-to-root redirect, verifies from outside (DoH, every asset,
certificate) and makes the old github.io link 301 to the domain. A later move to
Shopify is DNS only: A @ 23.227.38.65, CNAME www shops.myshopify.com, both
DNS-only. Fahad does anything needing his login or payment; Claude never
creates accounts or enters payment.

**THIS REPO IS PUBLIC AND GITHUB PAGES SERVES EVERY FILE IN IT** (`/CLAUDE.md`,
`/build.py`, `/BUILD-NOTES.md`, `/test/`). Before hosting is connected, split it
the way ZEF does: this repo private, a deploy script copying an ALLOWLIST
(index.html, css/landing.css, js/landing.js, the referenced images, favicons,
robots.txt) into what Pages serves. An allowlist, never "everything except X".

**At deploy time, add what needs the real domain:** `<link rel="canonical">`,
`og:image` and `og:url` (absolute URLs), and `url` in the LocalBusiness JSON-LD.

## Open

- **The owner confirm list** (`../00 - Source of Truth/00-Owner-Confirm-List-2026-09-13.md`):
  28 product lines (mostly signs, because he skipped that questionnaire grid)
  plus 7 page facts (20+ years, 2-4 days, proof on every job, samples at the
  counter, the UV reading, three unexplained window items). The page should not
  go public on the domain until he has been through it.
- **Page length: 12.9 phone screens against rule 26's 7-9.** The doors and the
  industries are two cuts of "who we print for"; cutting the doors saves ~1,020px
  on a phone. A deletion is Fahad's ruling (rule 106).
- **About copy says "He"** (rule 82 wants we/us). Approved copy; Fahad's call.
- The door photo showing the fictional "BRIOVA" brand was flagged 09-09; his call.
- `mfahadishtiaq.github.io/az-printing/` still serves the scrapped Direction F
  site printing the retired 416 number. Switch it off whatever else happens.
