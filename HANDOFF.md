# Handoff

What is finished, what is not, and what only a human can decide.

## Photography

Nine photographs were delivered, eight are in use, and every generated
illustration has been deleted. **Attribution is complete**: all eight are
credited in `CREDITS.md` against profile and photo links that have been opened
and verified. Nothing is outstanding here.

One delivered file is not used. **`stone-wall.jpg`** sits in
`img/incoming/rejected/` and is deliberately absent from `CREDITS.md` — there
is no sense in crediting a photograph nobody can see. It was rejected for two
independent reasons:

1. **A burned-in watermark** — "Nicole Moore PHOTOGRAPHY" across the lower
   third of the frame. The licence permits the use; publishing another
   photographer's branding across a guesthouse's own website is still not
   something to do.
2. **It is not Lebanon.** Grey fieldstone rubble walling, a red brick arch, a
   cedar-shingle roof and North American maple leaves on the ground. Lebanese
   village building is pale limestone with clay tile. It would have read as
   wrong to anyone who knows the country, which is the client.

If it is ever replaced with an unwatermarked Lebanese equivalent, the slot it
would have filled is the village page head, which currently carries no
photograph.

## Claims and photographs

A claim with no photograph behind it is not a contradiction. Only a claim a
photograph disproves is. **Nothing on the site is now in the second category.**

### Closed

- **"from Marseille" and "the same limestone"** — dropped from the home page
  paragraph in both languages. The roof photograph shows curved barrel tiles on
  a rendered wall, so neither claim survived contact with it. The paragraph now
  reads "the same red tiles", which the photograph does support.
- **"olive-green shutters"** — only ever appeared in alt text written for an
  illustration. The shutters photograph shows natural varnished wood; the alt
  text was rewritten to match and the claim appears nowhere in the copy.

### A standing placement constraint

**"Six hundred houses with red roofs"** — home teaser, and the village page H1.
`valley-road` shows a village of modern white buildings. It is the one
photograph in the set that would disprove a claim if it sat next to it, which
is why it is on *Getting here* and why the village page head carries no
photograph at all. Do not move it under either of those lines, and do not put a
village-wide photograph at the head of that page without checking it against
the H1 first.

### Claims wanting a photograph

These stand as written. They are unsupported, not contradicted — and they are
the shot list if anyone commissions more photography:

| Claim | Where | Would need |
|---|---|---|
| the triple-arched window | home and rooms, repeatedly — the most specific architectural claim on the site | a facade or interior showing three round-headed lights, the middle one taller. The only arches in the set are the two openings in `roof-tiles` |
| the vaulted breakfast room | home, *The house* | the vaulted room, ideally laid for breakfast — which would also fill the food gap |
| a Garden Room's own door onto the garden | home and rooms | a ground-floor room with its door open |
| the eighteen-step stone stair | rooms, twice | the house's own staircase, not a village one |
| the old souk | village | the arcaded street, which is the single most-cited reason to visit |

## Sections that now carry no photograph

Deliberate, not missing:

- the three room types, on both the home page and the rooms page — there is no
  wide interior photograph of any of them;
- the old souk on the village page — no photograph of the souk exists, so it
  leads its section as text;
- the village page head — its H1 claims six hundred red roofs and the only
  village-wide photograph contradicts it.

## Decisions a human has to make

1. **The WhatsApp number is now real.** `+961 81 520 553`, supplied by the
   owner, replaced the invented `+961 71 555 019` everywhere: `js/site.js`
   (`WA_NUMBER`), every `tel:` link, the floating button's static `href` on all
   four pages, the contact page's `noscript` fallback, the contact meta
   description, the Arabic strings and the JSON-LD. Grep for `520553` and
   `520 553` to change it again. Treat it as live: it is the only way anyone can
   reach the house from this site.
2. **The real domain.** Canonical URLs, Open Graph URLs, the JSON-LD `url`, the
   sitemap and `robots.txt` all point at
   `https://hafez121.github.io/dar-chams/`, which is where GitHub Pages serves
   this repository. If the site ships anywhere else, those absolute URLs need
   updating — they are the only absolute URLs in the project, there is one
   `sed` line for them in `README.md`, and everything else is a relative path
   that moves freely.
3. **Email and social links have been removed, not replaced.** The invented
   address `stay@darchams.com` sat on a domain registered to a third party, and
   `instagram.com/darchams` / `facebook.com/darchams` resolved to unrelated
   people's accounts. All of them are gone from the markup, the Arabic strings
   and the JSON-LD. `TODO` comments mark every place a real one goes: the footer
   of all four pages, the contact page's social row and contact list, and the
   `email` / `sameAs` fields of the JSON-LD. **Confirm an account exists before
   linking it.** Guessing a handle from the business name is what caused this.
4. **The rates, the policies and the history** are invented but internally
   consistent: $95 / $135 / $175 / $185, breakfast 8:00–10:30, check-in 15:00,
   check-out 11:00, a two-night weekend minimum, free cancellation to seven
   days, built 1874, restored over three winters, reopened 2023. Change one and
   you must change it in `index.html`, `rooms.html`, `contact.html`, the room
   `<select>` and the JSON-LD.
5. **Geo coordinates and the street address have been removed.** The JSON-LD
   no longer carries a `geo` block, a `streetAddress` or a `postalCode`: the
   coordinates were village-level rather than surveyed, `Rue du Vieux Souk` is
   not how a Lebanese address is written, and `1304` was an invented postal
   code. The address is now `Douma, Batroun District, North Lebanon`
   everywhere. The contact page no longer claims that Google Maps and Waze
   return a result for the guesthouse — they do not, because it does not exist.
   Add a `geo` block and a fuller address once there is a real building to
   survey.
6. **Arabic proofreading by a second native speaker.** The Arabic is mine and it
   is idiomatic Lebanese-flavoured MSA, but a hotel's own words deserve a second
   pair of eyes — particularly the room names and the policy wording.

## What was removed, and why

This site was publicly reachable for a while carrying invented identifiers that
turned out to belong to real people. Everything below has been taken out. None
of it should be reintroduced by guesswork.

| Invented | Where it was | Now |
|---|---|---|
| `+961 71 555 019` | every page, JSON-LD, `js/site.js`, Arabic strings | replaced with the owner's real number |
| `stay@darchams.com` | footers, contact list, form note, `noscript`, JSON-LD | removed; `TODO` left in place |
| `instagram.com/darchams` | four footers, contact social row, JSON-LD `sameAs` | removed; `TODO` left in place |
| `facebook.com/darchams` | four footers, contact social row, JSON-LD `sameAs` | removed; `TODO` left in place |
| `Rue du Vieux Souk` | four footers, contact list, JSON-LD `streetAddress` | `Douma, Batroun District, North Lebanon` |
| postal code `1304` | contact list, JSON-LD | removed |
| `34.2172 N, 35.8339 E` | JSON-LD `geo`, contact page, OpenStreetMap deep link | removed |
| "Google Maps and Waze find Dar Chams Douma" | contact page map note | removed — a false claim about real services |
| `Abou Elias` (restaurant) | home page copy, Arabic strings | "the grill house on the square" |

Place names that remain — Douma, Batroun, Bchaaleh, Baatara, Tannourine,
Byblos, Beirut — are real geography, not businesses or people, and the site
makes no claim about any of them beyond distances and directions.

## Known limits, deliberately accepted

- **Arabic lost its second typeface.** Headings used Noto Naskh Arabic, a
  serif, against IBM Plex Sans Arabic for text. That pairing cost 92 KB — more
  than a whole photograph — on every Arabic page. Arabic now uses Plex at two
  weights throughout. If the budget ever loosens, the Naskh pairing is worth
  restoring; it read better.
- **Self-hosted fonts do not load over `file://`.** Every browser blocks font
  fetches from the `null` origin, so opening the HTML straight off disk falls
  back to system type and logs two blocked requests. Everything else — images,
  reveals, the form, the Arabic toggle — works from disk. Over HTTP there is
  nothing in the console.
- **`robots.txt` does nothing where the site currently lives.** A crawler reads
  robots.txt only from the domain root — `https://hafez121.github.io/robots.txt`
  — which is served by the `Hafez121.github.io` repository, not this one. The
  file here is kept correct and written against the `/dar-chams/` prefix so it
  works the day the site gets its own domain, and so its rules can be pasted
  into the user-site robots.txt as they stand. Until then, `screenshots/` and
  `tools/` are publicly reachable and crawlable. If that matters, move them out
  of the published branch rather than relying on this file.

- **No language `<link rel="alternate">` tags in the pages.** The Arabic version
  lives at the same URL with `?lang=ar`, which is declared in `sitemap.xml` via
  `xhtml:link`, but search engines may still index only the English text since
  the Arabic is applied client-side. A server-rendered `/ar/` tree would be the
  correct answer at real scale; it is out of scope for a four-page static demo.
- **With JavaScript disabled the site is English-only.** Everything else works:
  every page is complete in the markup, the navigation is a plain list, the
  floating WhatsApp button is a real link with a prefilled message, and the
  enquiry form shows a `<noscript>` block pointing at WhatsApp, the email
  address and the phone number. The Arabic toggle is the one feature that
  cannot work without JS.
- **The date inputs are `type="date"`,** so their internal format follows the
  device locale rather than the page language. That is the correct trade: it
  gives the native picker and the right mobile keyboard. The composed WhatsApp
  message always spells the month out (`14 March 2027` / `14 آذار 2027`), so
  nothing is ambiguous by the time a human reads it.
- **One inline `style` attribute** remains, on the contact page's `#map`
  heading, to set its top margin. Move it into `css/style.css` if that offends.
- **The one tap target under 44 px** is the "Open in OpenStreetMap" link, which
  sits inline inside a sentence — WCAG 2.5.8 exempts inline text links, and
  padding it out would break the paragraph.

## What was checked, and how

Everything in the "Checks that were run" section of `README.md` was run against
a headless Chromium on every page in both languages, and everything it found
was fixed rather than noted. There are no known failures outstanding.

Screenshots are in `screenshots/`: four pages at 390 px and at 1440 px, the
contact page with the enquiry form filled in at both widths, and the Arabic
build of the home, rooms, village and contact pages.
