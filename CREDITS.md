# Image credits

Every image on the site is a photograph. The generated illustrations that stood
in for them have been deleted; they are in git history up to commit `e72ca1d`.

All attributions below were opened and verified. Unsplash and Pexels both allow
commercial use without attribution — these credits are courtesy, and a record
of what is actually in use.

## Photographs

| On the site | Where it appears | Credit |
|---|---|---|
| `img/hero-valley` | home page hero, and cropped to `img/og-cover` for the social card on all four pages | Photo by [Ali Hamada](https://unsplash.com/@alihamada32) on [Unsplash](https://unsplash.com/photos/0O2NJiYtP7w) |
| `img/roof-tiles` | home page, *The house* | Photo by [Barış Türköz](https://www.pexels.com/@baris-turkoz-214377915/) on Pexels — photo ID `34802849` |
| `img/terrace` | home page, *What a day here looks like* | Photo by [Patricia Jekki](https://unsplash.com/@jekkiliciouss) on [Unsplash](https://unsplash.com/photos/ND1FSqlzFG4) |
| `img/room-linen` | rooms page head | Photo by [Susan Wilkinson](https://unsplash.com/@susan_wilkinson) on [Unsplash](https://unsplash.com/photos/gSOdp7YlgNQ) |
| `img/shutters` | rooms page, the band between the room types and the rates | Photo by [Maria Lin Kim](https://unsplash.com/@mrsmaria) on [Unsplash](https://unsplash.com/photos/z5eHJ6iLVIk) |
| `img/olive-branch` | village page, *The olive terraces* | Photo by [Frank Albrecht](https://unsplash.com/@shotaspot) on [Unsplash](https://unsplash.com/photos/k-ICgGQLdkM) |
| `img/stone-steps` | village page, *The stairs and the roofs* | Photo by [Nicolas Hoch](https://unsplash.com/@nico67xvi) on [Unsplash](https://unsplash.com/photos/iBiRuI5AKYY) |
| `img/valley-road` | village page, *Getting here* | Photo by [Ahmad Bader](https://unsplash.com/@palo1987) on [Unsplash](https://unsplash.com/photos/YpaZ13PbkWM) |

Eight photographs, eight slots, no photograph used twice. `img/og-cover` is a
1200×630 crop of the hero rather than a ninth image.

The delivered filenames were not the slot names — `valley-dusk.jpg` became the
hero, `hero-village.jpg` became `valley-road` — so the originals are kept in
`img/incoming/` under their slot names, and the mapping is recorded in the
commit that made it (`4521bc8`).

## Crops

Two files were cropped by hand before the pipeline rather than centre-cropped:

- **`room-linen`** — the left 86% and lower 84% of the frame, to keep the bed,
  the light and the side table while leaving a framed floral print on the
  right-hand wall out of shot.
- **`og-cover`** — a 1200×630 letterbox of the hero photograph.

Everything else is a centre crop to the slot's ratio, done by
`tools/fetch-photos.sh`.

## Fonts

| Family | Use | Licence | Source |
|---|---|---|---|
| Cormorant Garamond 400 / 600 | Latin display | SIL Open Font License 1.1 | Google Fonts (`fonts/cormorant-*.woff2`, Latin subset) |
| IBM Plex Sans Arabic 400 / 600 | all Arabic text | SIL Open Font License 1.1 | Google Fonts (`fonts/plexar-*.woff2`, Arabic subset) |
| System UI stack | Latin body text | — | the visitor's device |

Noto Naskh Arabic was dropped: 92 KB for Arabic headings alone, on a site that
promises to work on 3G, was not a trade worth making. Arabic now uses IBM Plex
Sans Arabic at two weights throughout.

## Icons

The WhatsApp glyph and the Dar Chams mark are drawn as inline SVG paths in this
repository. No icon font, no icon library.
