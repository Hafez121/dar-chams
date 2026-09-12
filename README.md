# Dar Chams — concept demo site

A four-page static site for a fictional eight-room guesthouse in Douma, North
Lebanon. Plain HTML, hand-written CSS, vanilla JavaScript. No framework, no
build step, no npm, no external runtime dependency of any kind. Drop the folder
on GitHub Pages at any depth and it serves correctly; every path in the markup
is relative.

Designed and built by [Hafez Fandy](https://hafez121.github.io).

Published from the root of this repository to GitHub Pages at
**<https://hafez121.github.io/dar-chams/>**. Every path in the markup, the CSS
and the JavaScript is relative, so the same files serve correctly from the
domain root, from a one-level subpath, from a three-level one, or from `file://`
with no server at all. The only absolute URLs in the project are the canonical,
Open Graph, JSON-LD and sitemap tags, which have to be absolute — they are
listed under “Moving the site” below.

---

## File tree

```
dar-chams/
├── index.html          home
├── rooms.html          the eight rooms, grouped into three types
├── village.html        Douma: what to do, how to get here, the seasons
├── contact.html        enquiry form, contact details, map
├── css/
│   ├── style.css       the whole design system, mobile-first
│   └── print.css       print rules, linked from contact.html only
├── js/
│   ├── i18n.js         every Arabic string, plus the strings JS builds
│   └── site.js         language, navigation, scroll reveals, the form
├── img/                photographs, .webp with a .jpg fallback for each
│   └── incoming/       drop originals here; rejected/ holds what was not used
├── fonts/              self-hosted woff2 subsets (no Google Fonts request)
├── tools/
│   ├── fetch-photos.sh  resizes originals into the image slots
│   ├── _process_photo.py  one slot: fit, strip EXIF, WebP + JPEG to budget
│   ├── screenshots.cjs  captures the review screenshots
│   └── verify-live.sh   checks the deployed site, not the local copy
├── screenshots/        390 px and 1440 px full-page captures, EN and AR
├── favicon.svg · favicon-32.png · apple-touch-icon.png
├── robots.txt · sitemap.xml
├── CREDITS.md          image sources
└── HANDOFF.md          what is unfinished and what a human must decide
```

## How the language switch works

The chosen language lives in **one JavaScript variable** and in the **URL**
(`?lang=ar`). There is no `localStorage` anywhere in this project.

1. A four-line inline script in each `<head>` reads `?lang=ar` before first
   paint and sets `lang`, `dir` and `data-lang` on `<html>`, so Arabic never
   flashes left-to-right.
2. `js/site.js` re-renders in place: it walks `[data-i18n]` (text) and
   `[data-i18n-attr]` (attributes such as `alt` and `placeholder`), swaps
   `<title>` and the meta description, and rewrites every internal link so the
   choice survives a click through to the next page.
3. The English text lives in the HTML itself, not in a dictionary. Any key
   missing from `js/i18n.js` falls back to what is already in the markup, so a
   half-finished translation degrades to English rather than to a blank page.

Arabic is not a coat of paint on the English layout:

- the whole stylesheet uses logical properties (`padding-inline`,
  `inset-inline-end`, `border-block-start`, `text-align: start`), so the
  mirror is free and there is not one `margin-left` to override;
- arrows flip with `scaleX(-1)`;
- Arabic gets its own type: **Noto Naskh Arabic** for headings, **IBM Plex Sans
  Arabic** for text, with its own line-height (1.9 against 1.62) and no
  letter-spacing or uppercasing, both of which are meaningless in Arabic;
- the Arabic font faces carry a `unicode-range`, so an English visitor never
  downloads them.

## How the booking flow works

The site is static and cannot take a booking, so it does what Lebanese hotels
actually do: it hands the guest to WhatsApp.

`contact.html` validates in JavaScript, shows inline errors, moves focus to the
first bad field, then composes a message and opens `https://wa.me/<number>?text=…`
in a new tab. Nothing is ever POSTed. The composed message reads:

> Hello Dar Chams — I'd like to enquire about a booking. Name: Layla Haddad.
> Check-in: 14 March 2027. Check-out: 16 March 2027. Guests: 2. Room: Garden
> Room. Note: We will arrive late, around 21:00.

and in Arabic:

> مرحباً دار شمس — أودّ الاستفسار عن حجز. الاسم: ليلى حدّاد. تاريخ الوصول: 14 آذار 2027. تاريخ المغادرة: 16 آذار 2027. عدد الضيوف: 2. الغرفة: غرفة قناطر.

If the pop-up is blocked, a fallback link appears carrying the same URL.

**The number `+961 81 520 553` is the real one** and is the single contact
route on the site. It appears in `js/site.js` (`WA_NUMBER`), in every `tel:`
link, in the floating button's static `href`, in the contact page's `noscript`
fallback, and in the `Hotel` JSON-LD. To change it, grep for `520553` and
`520 553` — that catches all of them.

There is deliberately **no email address and no social link** on the site. An
earlier draft carried invented ones; the handles resolved to unrelated
third-party accounts and the mail domain belongs to somebody else, so they were
removed rather than guessed at again. `TODO` comments mark the exact places to
put the real ones — in the footer of all four pages, in the contact page's
social row and contact list, and in the `sameAs` and `email` fields of the
JSON-LD. Do not invent a replacement: confirm the account exists first.

## The photographs, and the image slots

Nine photographs were delivered; eight are in use and one was rejected (see
`CREDITS.md`). Every image on the site is a photograph — there are no generated
illustrations left anywhere.

```
img/hero-valley     940×588    home hero — terraced hillsides in late light
img/roof-tiles      800×1200   home, "The house" — clay tiles and arched openings
img/terrace         740×987    home, "A day here" — the terrace through a doorway
img/room-linen     1100×917    rooms page head — white linen in morning sun
img/shutters       1160×652    rooms — louvred shutters, a light study
img/olive-branch    660×990    village — olives on the branch
img/stone-steps     440×660    village — a village staircase
img/valley-road    1020×573    village, "Getting here" — the valley on the way up
img/og-cover       1200×630    social card, cropped from the hero
```

Three sections carry no photograph, because no photograph of their subject
exists: the three room types on both the home and rooms pages, the old souk on
the village page, and the village page head. They run on typography instead.
Putting one room's picture above another room's description, or a generic
street above a paragraph about Douma's souk, would be a small lie told nine
times over.

To replace or add a photograph: drop the file in `img/incoming/` named after
the slot, then

```sh
tools/fetch-photos.sh
```

It fits each file to the slot's exact dimensions, strips EXIF, and writes a
WebP and a JPEG under the byte budget, choosing the highest quality that fits
and refusing to drop below quality 46. Files matching no slot are listed rather
than silently ignored. The dimensions above live in one place — the `SLOTS`
table at the top of that script — and must match the `width`/`height` in the
markup.

**Why the images are the size they are.** The binding constraint is the 500 KB
per-page budget, not a per-file number. A page carries up to three photographs
plus ~115 KB of fonts and ~70 KB of markup, CSS and JS, so each photograph gets
about 95 KB. Dense subjects cost more per pixel than smooth ones: the aerial
hero and the stone staircase are mostly high-frequency texture, which is why
they are the smallest images on the site. Raising a slot's dimensions without
re-checking page weight will break the budget.

## Verifying the deployed site

Local checks prove the files are right; they say nothing about what GitHub
Pages actually serves. `tools/verify-live.sh` checks the deployment itself:

```sh
tools/verify-live.sh                       # defaults to the published URL
tools/verify-live.sh https://example.test/  # or anywhere else
```

It waits up to five minutes for a first deploy, then confirms the base URL
answers 200 and is really `index.html` (a Pages 404 is also HTML), that all
four pages answer 200, that images return image **bytes** — content-type *and*
magic number, so an error page saved under a `.webp` name cannot pass — that
the five self-hosted fonts return `wOF2` over https, and that the CSS, the
scripts, `robots.txt` and `sitemap.xml` all resolve. It exits with the number
of failures.

`.github/workflows/verify-live.yml` runs the same script on every Pages build,
so a broken deploy shows up in the Actions tab without anyone remembering to
look.

## Moving the site

Nothing needs touching to change how deep the site is served — the relative
paths handle it. What does need touching if the **domain** changes is the small
set of absolute URLs, all of which currently read
`https://hafez121.github.io/dar-chams/…`:

- `<link rel="canonical">`, `og:url`, `og:image`, `twitter:image` — four per page
- the `url` and `image` fields of the `Hotel` JSON-LD in `index.html`
- every `<loc>` and `xhtml:link href` in `sitemap.xml`
- the `Sitemap:` line in `robots.txt`

```sh
grep -rl 'hafez121.github.io/dar-chams' . --include='*.html' --include='*.xml' --include='*.txt' \
  | xargs sed -i 's|https://hafez121.github.io/dar-chams|https://your-domain.example|g'
```

`robots.txt` is a special case: a crawler only reads it from the **domain root**
(`https://hafez121.github.io/robots.txt`), which belongs to the
`Hafez121.github.io` repository, not this one. The file here is therefore inert
where the site currently lives — it is kept correct so that it works the day the
site moves to its own domain, and its rules are written against the
`/dar-chams/` prefix in the meantime.
