#!/usr/bin/env sh
# ---------------------------------------------------------------------------
# Dar Chams — put real photographs into img/
#
#   tools/fetch-photos.sh [folder-of-photos]      (default: img/incoming)
#
# For every slot the site uses, this looks for a source file whose name starts
# with the slot name (hero-village.jpg, hero-village-2.png, hero_village.HEIC…),
# resizes and centre-crops it to the exact dimensions the markup declares,
# strips EXIF, and writes both a .webp and a .jpg under 150 KB.
#
# It prefers cwebp + ImageMagick and falls back to Python with Pillow. If it
# finds none of them it says so and stops rather than half-doing the job.
# ---------------------------------------------------------------------------
set -eu

DEST=$(CDPATH= cd -- "$(dirname -- "$0")/../img" && pwd)

# Per-file ceiling. The binding constraint is the 500 KB per-page budget, not
# this number: a page carries up to three photographs plus 115 KB of fonts and
# about 70 KB of markup, CSS and JS, so ~100 KB each is what actually fits.
BUDGET=${BUDGET:-94208}
SRC=${1:-$DEST/incoming}

if [ ! -d "$SRC" ]; then
  echo "usage: tools/fetch-photos.sh [folder-of-photos]   (default: img/incoming)" >&2
  exit 2
fi
if [ -z "$(find "$SRC" -type f \( -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.png' \
           -o -iname '*.webp' -o -iname '*.tif' -o -iname '*.tiff' -o -iname '*.heic' \) 2>/dev/null)" ]; then
  echo "No photographs found in $SRC — nothing to do." >&2
  echo "Drop files named after the image slots (see README.md) and run this again." >&2
  exit 2
fi

SLOTS="hero-valley:940:588
roof-tiles:800:1200
terrace:740:987
room-linen:1100:917
shutters:1160:652
olive-branch:660:990
stone-steps:440:660
valley-road:1020:573"

have() { command -v "$1" >/dev/null 2>&1; }

# The slot loop below runs in a subshell, so matched files are recorded in a
# file rather than a variable. Anything left over is reported at the end: a
# photograph that matches no slot must never be dropped in silence.
USED=$(mktemp); OVER=$(mktemp); trap 'rm -f "$USED" "$OVER"' EXIT INT TERM
OVERSIZE=0

if ! python3 -c "import PIL" 2>/dev/null; then
  echo "Python Pillow is not installed, so nothing can be resized. Install it:" >&2
  echo "  python3 -m pip install pillow" >&2
  echo "  Debian/Ubuntu: sudo apt install python3-pil" >&2
  echo "  Arch         : sudo pacman -S python-pillow" >&2
  exit 1
fi
echo "encoder: Pillow $(python3 -c 'import PIL;print(PIL.__version__)')"

echo "$SLOTS" | while IFS=: read -r name w h; do
  [ -n "$name" ] || continue
  found=""
  for ext in jpg jpeg JPG JPEG png PNG webp WEBP tif tiff heic HEIC; do
    for cand in "$SRC/$name".$ext "$SRC/$name"-*.$ext "$SRC/$(echo "$name" | tr '-' '_')".$ext; do
      [ -f "$cand" ] || continue
      found="$cand"; break
    done
    [ -n "$found" ] && break
  done

  if [ -z "$found" ]; then
    echo "  MISSING  $name  (${w}x${h}) — keeping the current placeholder"
    continue
  fi
  printf '%s\n' "$found" >> "$USED"

  # a 404 page saved with an image extension is not an image
  if ! head -c 12 "$found" | od -An -tx1 | grep -Eq 'ff d8 ff|89 50 4e 47|52 49 46 46|49 49 2a|4d 4d 00'; then
    echo "  BAD FILE $found — not a real image, skipped"
    continue
  fi

  if ! python3 "$(dirname -- "$0")/_process_photo.py" "$found" "$DEST/$name" "$w" "$h" "$BUDGET"; then
    echo x >> "$OVER"
  fi
done

# ---------------------------------------------------------------------------
# Anything in the source folder that matched no slot. These are not errors —
# a set of detail crops will not be named after the slots a layout happens to
# have - but they must be listed, because a silently ignored photograph looks
# exactly like a photograph that was used.
echo
UNMATCHED=0
for f in "$SRC"/*; do
  [ -f "$f" ] || continue
  case "$f" in *.md|*.txt|*.json) continue ;; esac
  if ! grep -qxF "$f" "$USED" 2>/dev/null; then
    [ "$UNMATCHED" -eq 0 ] && echo "Not used — these matched no slot:"
    UNMATCHED=$((UNMATCHED + 1))
    base=$(basename "$f")
    stem=${base%.*}
    # a near miss is worth pointing at: stone-steps vs the stone-stair slot
    near=$(echo "$SLOTS" | cut -d: -f1 | awk -v s="$stem" '
      { a = $0; n = 0
        for (i = 1; i <= length(s) && i <= length(a); i++)
          if (substr(s, i, 1) == substr(a, i, 1)) n++
        if (n > best && n >= 5) { best = n; hit = a } }
      END { if (hit != "") print hit }')
    if [ -n "$near" ]; then
      echo "    $base   (did you mean the \"$near\" slot? rename it, or change the slot list)"
    else
      echo "    $base"
    fi
  fi
done
[ "$UNMATCHED" -eq 0 ] && echo "Every file in $SRC was used."

n_over=$(wc -l < "$OVER" 2>/dev/null | tr -d ' ')
if [ "${n_over:-0}" -gt 0 ]; then
  echo
  echo "$n_over file(s) will not fit $((BUDGET / 1024)) KB at quality 46 or better."
  echo "Do not ship them as they are, and do not lower the quality floor: reduce the"
  echo "slot's declared dimensions here and in the markup, or crop the source tighter."
fi

echo
echo "Done. Now fill in CREDITS.md with the photographer and source URL for each"
echo "file, and check every page at 390 px before calling it finished."
