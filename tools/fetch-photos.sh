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

  # keep every file under the 150 KB ceiling
  for f in "$DEST/$name.jpg" "$DEST/$name.webp"; do
    q=78
    while [ "$(wc -c < "$f")" -gt 153600 ] && [ "$q" -ge 50 ]; do
      case "$f" in
        *.webp) if [ "$CWEBP" -eq 1 ]; then cwebp -quiet -q "$q" -m 6 "$DEST/$name.jpg" -o "$f";
                else python3 -c "from PIL import Image;i=Image.open('$DEST/$name.jpg');i.save('$f','WEBP',quality=$q,method=6)"; fi ;;
        *)      if [ -n "$IM" ]; then $IM "$f" -quality "$q" "$f";
                else python3 -c "from PIL import Image;i=Image.open('$f');i.save('$f','JPEG',quality=$q,optimize=True,progressive=True)"; fi ;;
      esac
      q=$((q - 8))
    done
    printf '  %-14s %s  %s KB\n' "$name" "$(basename "$f")" "$(( $(wc -c < "$f") / 1024 ))"
  done
done

echo
echo "Done. Now fill in CREDITS.md with the photographer and source URL for each"
echo "file, and check every page at 390 px before calling it finished."
