# Drop real photographs here

Name each file after the slot it fills — `hero-village.jpg`, `room-arch.jpg`,
`souk.jpg` and so on. The full list of slots, with the dimensions the markup
declares, is in the project `README.md`.

Then run, from the repository root:

```sh
tools/fetch-photos.sh
```

It resizes and centre-crops each photograph to the exact dimensions the layout
uses, strips EXIF, writes a `.webp` and a `.jpg` under 150 KB each into `img/`,
and refuses anything that is not really an image. Files whose names match no
slot are ignored; slots with no matching file keep the illustration that is
there now.

Afterwards: record the photographer and source URL for each file in
`CREDITS.md`, and re-read the `alt` text of every image you replaced — if a
photograph shows something other than what the alt text describes, change the
alt text rather than leaving it wrong.

This file is a placeholder so the directory exists in git. Delete it once real
photographs are in.
