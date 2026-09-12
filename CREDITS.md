# Image credits

Every image on the site is a photograph. The generated illustrations that stood
in for them until now have been deleted; they are in git history up to commit
`e72ca1d` if anyone needs to see what was there before.

## Attribution

Five of the nine delivered files still carried their download filenames, which
encode the photographer and the photo ID. Those are recorded below. **Four did
not, and I could not identify them** — including the one now used as the home
page hero. Those rows have to be completed by hand before this site is shown
anywhere public: an unattributed photograph is a licensing problem waiting to
happen, whatever its source.

The URLs below are reconstructed from the delivered filenames. This build
environment has no network access to Unsplash or Pexels, so **none of them has
been opened and confirmed** — check each one before relying on it.

| Slot | Photographer | Source | Delivered filename |
|---|---|---|---|
| `img/hero-valley` | **unknown — must be identified** | — | `valley-dusk.jpg` |
| `img/roof-tiles` | Baris Turkoz | Pexels, photo `34802849` — `https://www.pexels.com/photo/34802849/` | `pexels-baris-turkoz-214377915-34802849.jpg` |
| `img/terrace` | **unknown — must be identified** | — | `terrace.jpg` |
| `img/room-linen` | Susan Wilkinson | Unsplash, photo `gSOdp7YlgNQ` — `https://unsplash.com/photos/gSOdp7YlgNQ` | `susan-wilkinson-gSOdp7YlgNQ-unsplash.jpg` |
| `img/shutters` | Maria Lin Kim | Unsplash, photo `z5eHJ6iLVIk` — `https://unsplash.com/photos/z5eHJ6iLVIk` | `maria-lin-kim-z5eHJ6iLVIk-unsplash.jpg` |
| `img/olive-branch` | Frank Albrecht | Unsplash, photo `k-ICgGQLdkM` — `https://unsplash.com/photos/k-ICgGQLdkM` | `frank-albrecht-k-ICgGQLdkM-unsplash.jpg` |
| `img/stone-steps` | **unknown — must be identified** | — | `stone-steps.jpg` |
| `img/valley-road` | **unknown — must be identified** | — | `hero-village.jpg` |
| `img/og-cover` | same photograph as `hero-valley` | — | — |

Unsplash and Pexels both permit commercial use without attribution; crediting
the photographer is courtesy rather than obligation. Knowing *which* photograph
you are using is not optional either way.

## Not used

**`stone-wall.jpg`** — Nicole Moore, Unsplash, photo `1yV65pbzhU4`. Moved to
`img/incoming/rejected/`. Two independent reasons:

1. **It carries a burned-in watermark** — "Nicole Moore PHOTOGRAPHY" across the
   lower third of the frame. The Unsplash licence permits the use; publishing
   another photographer's branding across a guesthouse's own website is still
   not something to do.
2. **It is not Lebanon.** Grey fieldstone rubble walling, a red brick arch, a
   cedar-shingle roof and North American maple leaves on the ground. Lebanese
   village building is pale limestone with clay tile. It would have read as
   wrong to anyone who knows the country, which is the client.

## Crops

Two files were cropped by hand before the pipeline rather than centre-cropped:

- **`room-linen`** — taken from the left 86% and lower 84% of the frame, to
  keep the bed, the light and the side table while leaving a framed floral
  print on the right-hand wall out of shot.
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
