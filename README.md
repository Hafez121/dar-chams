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
├── img/                artwork, .webp with a .jpg fallback for each
├── fonts/              self-hosted woff2 subsets (no Google Fonts request)
├── tools/
│   ├── make_images.py  regenerates the placeholder artwork
│   ├── fetch-photos.sh downloads and processes real photography
│   └── screenshots.cjs captures the review screenshots
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

**The number `+961 71 555 019` is invented.** It appears in `js/site.js`
(`WA_NUMBER`), in every `tel:` link, in the floating button's static `href`,
and in the `Hotel` JSON-LD. Search for `555019` and `555 019` to replace them
all.

## Swapping in real photography

Every image slot is already the right shape: the `<img>` carries the exact
`width` and `height` the layout uses, the WebP is offered first through
`<picture><source>`, and the JPEG is the fallback. Replacing a photo is a
file swap — no markup change.

```
img/hero-village   1600×1000   home hero — the village across the valley
img/house-facade   1200×900    the front of the house, triple-arch window
img/arch-window     800×1000   interior, triple-arched window (rooms page head)
img/room-garden    1200×900    a Garden Room
img/room-arch      1200×900    an Arch Room
img/room-suite     1200×900    the Liwan, vaulted ceiling
img/breakfast      1200×800    the breakfast table, from above
img/terraces       1200×800    olive terraces and dry-stone walls
img/souk            800×1000   the old souk
img/stone-stair     800×1000   a village staircase
img/valley-dusk    1600×900    the valley at dusk
img/courtyard      1600×700    the courtyard
img/og-cover       1200×630    social card
```

With real photographs in a folder, run:

```sh
tools/fetch-photos.sh ~/Downloads/dar-chams-photos
```

It resizes each file to the dimensions above, strips EXIF, writes a `.webp` and
a `.jpg` under 150 KB each, and refuses anything that is not a real image. It
needs either `cwebp` + ImageMagick, or Python with Pillow — it checks and tells
you which one it found.

Then update `CREDITS.md` with the photographer and source URL for each file.

## Decisions taken without asking

- **Four pages, no more.** The souk, the seasons and the directions live inside
  `village.html` rather than becoming thin pages of their own.
- **No hero overlay, no Book Now band, no testimonial slider, no icon cards.**
  The hero is an asymmetric split — type on one side, one large image bleeding
  to the opposite edge. The room previews sit on a twelve-column grid at three
  different widths so they do not read as a card row.
- **Illustrated map instead of an embedded one.** A Google Maps iframe is
  roughly 300 KB of third-party JavaScript, breaks offline, and looks like
  every other hotel site. `contact.html` draws the road from Beirut as inline
  SVG, with the coordinates and an OpenStreetMap link beside it.
- **System sans for body text, one web serif for display.** Cormorant Garamond
  is used above about 20 px only, where its thin strokes are an asset. Body
  text is the platform UI font: 0 KB and correct on every device.
- **Self-hosted fonts.** Google Fonts would add two DNS lookups and a
  render-blocking stylesheet on a 3G connection. The woff2 subsets are in
  `fonts/` and preloaded.
- **Western digits in the Arabic text.** That is what Lebanese price lists,
  road signs and hotel invoices use.
- **Prices, policies and distances were invented once and used everywhere.**
  $95 / $135 / $175 / $185, breakfast 8:00–10:30, check-in 15:00, check-out
  11:00, two-night weekend minimum, free cancellation to seven days. If you
  change one, change it in `rooms.html`, `index.html`, `contact.html`, the
  `<select>` options and the JSON-LD.

## Checks that were run

Chromium, driven headlessly (`tools/screenshots.cjs` uses the same setup):

- no console errors and no failed requests on any page, in either language;
- every internal link and every `#anchor` resolves;
- every image loads and renders, and every `<img>` has `width`, `height` and
  `alt`;
- one `<h1>` per page and no skipped heading levels;
- no horizontal scroll at 360, 390, 414, 768, 1024, 1440 px, in both languages;
- every standalone tap target at least 44 px tall; no text below 15 px;
- every text colour at 4.5:1 or better against its real background
  (3:1 for large type);
- the mobile menu moves focus into the panel, traps Tab, closes on Escape and
  returns focus to the button;
- the enquiry form rejects an empty submission, a past date and a check-out
  before check-in, and the composed WhatsApp URL decodes to a clean sentence;
- the Arabic build leaves no English strings on the page;
- page weight, uncompressed and with fonts: 210–287 KB in English,
  379 KB for the Arabic home page. Budget was 500 KB;
- the whole suite above run twice, once with the site served from the domain
  root and once from a `/dar-chams/` subpath, to prove no path depends on where
  the site is mounted.

## Running it

```sh
python3 -m http.server 8123
# then open http://127.0.0.1:8123/
```

To rehearse the GitHub Pages subpath instead, serve the folder above this one
and open `http://127.0.0.1:8123/dar-chams/`. Both work, and both are checked.

Opening `index.html` straight off the file system works as well — images, the
scroll reveals, the enquiry form and the Arabic toggle all behave — with one
exception no static site can avoid: browsers refuse to load self-hosted
webfonts over `file://` (a CORS check against the `null` origin), so the type
falls back to the system serif and sans and the console shows two blocked font
requests. Serve it over HTTP to see it as designed.

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
