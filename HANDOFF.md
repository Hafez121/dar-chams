# Handoff

What is finished, what is not, and what only a human can decide.

## What is still open on the photography

Nine photographs were delivered and eight are in use. Every generated
illustration has been deleted. Three things remain:

1. **Four of the eight are unattributed.** `hero-valley` (the home page hero),
   `terrace`, `stone-steps` and `valley-road` arrived with generic filenames,
   so there is no photographer and no source URL for them. The other four kept
   their download filenames and are credited in `CREDITS.md`. Identify the four
   before this is shown publicly — the hero above all.
2. **The reconstructed URLs are unverified.** This environment cannot reach
   Unsplash or Pexels, so every link in `CREDITS.md` was rebuilt from a
   filename and none has been opened. Check them.
3. **`stone-wall.jpg` was rejected** and sits in `img/incoming/rejected/`. It
   carries a burned-in "Nicole Moore PHOTOGRAPHY" watermark, and it is not
   Lebanese architecture — grey fieldstone, a brick arch, cedar shingles and
   maple leaves. Both reasons are in `CREDITS.md`.

## Where the copy and the photographs disagree

The site makes specific visual claims. Most have no photograph behind them,
which is fine. These are the ones where a photograph is now adjacent to a claim
it does not support. Two of them have since been closed by the owner's decision:
"from Marseille" and "the same limestone" were dropped from the home page
paragraph, in both languages. What is left below are claims with no photograph
behind them, which is not the same thing as a contradiction.

| Claim | Where | What the photograph shows |
|---|---|---|
| "triple-arched windows" | home and rooms, repeatedly | The only arches in the set are the two round-headed openings in `roof-tiles`. Nothing shows a triple arch. |
| "olive-green shutters" | previously in the home alt text, now removed | `shutters` shows natural varnished wood. The alt text was rewritten to match; the claim no longer appears anywhere in the copy. |
| "six hundred houses with red roofs" | home teaser and the village page H1 | `valley-road` shows a village of modern white buildings. This is why it is on *Getting here* and not under either of those lines, and why the village page head now carries no photograph at all. |

The paragraph now reads "the same red tiles", which the photograph does
support. The triple arch remains a claim with no picture behind it: fine as it
stands, and worth a photograph if one ever turns up. Nothing else needs a
decision.

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
