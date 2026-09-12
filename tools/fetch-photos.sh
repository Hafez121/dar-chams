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

SLOTS="hero-village:1600:1000
house-facade:1200:900
arch-window:800:1000
room-garden:1200:900
room-arch:1200:900
room-suite:1200:900
breakfast:1200:800
terraces:1200:800
souk:800:1000
stone-stair:800:1000
valley-dusk:1600:900
courtyard:1600:700
og-cover:1200:630"

have() { command -v "$1" >/dev/null 2>&1; }

# The slot loop below runs in a subshell, so matched files are recorded in a
# file rather than a variable. Anything left over is reported at the end: a
# photograph that matches no slot must never be dropped in silence.
USED=$(mktemp); OVER=$(mktemp); trap 'rm -f "$USED" "$OVER"' EXIT INT TERM
OVERSIZE=0

if have magick;      then IM="magick";
elif have convert;   then IM="convert";
else                      IM=""; fi
have cwebp && CWEBP=1 || CWEBP=0
python3 -c "import PIL" 2>/dev/null && PILLOW=1 || PILLOW=0

if [ -z "$IM" ] && [ "$PILLOW" -eq 0 ]; then
  echo "Neither ImageMagick nor Python Pillow is installed, so nothing can be" >&2
  echo "resized. Install one of them and run this again:" >&2
  echo "  Debian/Ubuntu : sudo apt install imagemagick webp" >&2
  echo "  Arch          : sudo pacman -S imagemagick libwebp" >&2
  echo "  macOS         : brew install imagemagick webp" >&2
  echo "  or            : python3 -m pip install pillow" >&2
  exit 1
fi
echo "tools: ImageMagick=${IM:-none} cwebp=$CWEBP pillow=$PILLOW"

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

  if [ -n "$IM" ]; then
    $IM "$found" -auto-orient -strip -resize "${w}x${h}^" \
        -gravity center -extent "${w}x${h}" -quality 82 "$DEST/$name.jpg"
    if [ "$CWEBP" -eq 1 ]; then
      cwebp -quiet -q 80 -m 6 -metadata none "$DEST/$name.jpg" -o "$DEST/$name.webp"
    else
      $IM "$DEST/$name.jpg" -quality 80 "$DEST/$name.webp"
    fi
  else
    python3 - "$found" "$DEST/$name" "$w" "$h" <<'PY'
import sys
from PIL import Image, ImageOps
src, out, w, h = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
im = ImageOps.fit(im, (w, h), Image.LANCZOS, centering=(0.5, 0.5))
clean = Image.new("RGB", im.size)          # drops every EXIF block
clean.paste(im)
clean.save(out + ".jpg", "JPEG", quality=82, optimize=True, progressive=True)
clean.save(out + ".webp", "WEBP", quality=80, method=6)
PY
  fi

  # Keep every file under the 150 KB ceiling. The ladder goes down to q=34;
  # a photograph that will not fit even there is reported, never shipped in
  # silence at four times the budget.
  for f in "$DEST/$name.jpg" "$DEST/$name.webp"; do
    q=82
    while [ "$(wc -c < "$f")" -gt 153600 ] && [ "$q" -ge 34 ]; do
      case "$f" in
        *.webp) if [ "$CWEBP" -eq 1 ]; then cwebp -quiet -q "$q" -m 6 "$DEST/$name.jpg" -o "$f";
                else python3 -c "from PIL import Image;i=Image.open('$DEST/$name.jpg');i.save('$f','WEBP',quality=$q,method=6)"; fi ;;
        *)      if [ -n "$IM" ]; then $IM "$f" -quality "$q" "$f";
                else python3 -c "from PIL import Image;i=Image.open('$f');i.save('$f','JPEG',quality=$q,optimize=True,progressive=True)"; fi ;;
      esac
      q=$((q - 6))
    done
    kb=$(( $(wc -c < "$f") / 1024 ))
    if [ "$kb" -gt 150 ]; then
      printf '  %-14s %-22s %s KB  ** OVER THE 150 KB BUDGET **\n' "$name" "$(basename "$f")" "$kb"
      echo x >> "$OVER"
    else
      printf '  %-14s %-22s %s KB\n' "$name" "$(basename "$f")" "$kb"
    fi
  done
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
  echo "$n_over file(s) are over the 150 KB budget even at the lowest quality on the"
  echo "ladder. Do not ship them as they are. Either crop the source tighter, or"
  echo "reduce the slot's declared dimensions in this script and in the markup."
fi

echo
echo "Done. Now fill in CREDITS.md with the photographer and source URL for each"
echo "file, and check every page at 390 px before calling it finished."
