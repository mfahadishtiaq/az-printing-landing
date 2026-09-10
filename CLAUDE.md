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

- **Eight blocks, in this order:** hero · what we print · same day · what to
  expect · the shop's story · who we print for · questions · find us and
  contact. Ordered so a visitor can stop anywhere and still know enough to call.
- **The category tiles DO NOT LINK.** On a one-page site there is nowhere for
  them to go, and eight tiles pointing at the same anchor is noise pretending to
  be navigation. `landing.css` removes the pointer and the hover lift so they
  do not look clickable.
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

## Open

- **Hosting:** GitHub Pages, as a window for the client only. A real domain
  comes later. `azprintingandsigns.com` was on clientHold at last check.
- **Still noindexed?** No — this build sets no robots tag, because it is meant
  to be found. The shop build's placeholder-image coupling does not apply here.
  Before it goes public, confirm every image on it is one AZ may use.
- The live page at `mfahadishtiaq.github.io/az-printing/` still serves the
  scrapped Direction F site **printing the retired 416 number**. It should be
  switched off whatever happens to this build.
