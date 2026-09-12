# Photograph originals

The full-size files as delivered. Nothing here is served by the site — the
pipeline reads from here and writes sized copies into `img/`. `robots.txt`
keeps crawlers out of this directory.

Name each file after the slot it fills. The slots, with the dimensions the
markup declares, are listed in the project `README.md` and defined once in the
`SLOTS` table at the top of `tools/fetch-photos.sh`:

```
hero-valley  roof-tiles  terrace  room-linen
shutters     olive-branch  stone-steps  valley-road
```

Then, from the repository root:

```sh
tools/fetch-photos.sh
```

It fits each file to its slot, strips EXIF, and writes a WebP and a JPEG under
the byte budget at the best quality that fits. Files matching no slot are
listed rather than ignored. Slots with no file keep whatever is in `img/`.

`room-linen.jpg` is a hand crop of `linen.jpg`, kept here so the pipeline is
reproducible; both are left in place. `rejected/` holds delivered files that
are not used, with the reason recorded in `CREDITS.md`.

Afterwards: add the photographer and source URL to `CREDITS.md`, and re-read
the `alt` text of anything you replaced — if the photograph shows something
other than what the alt text says, change the alt text.
