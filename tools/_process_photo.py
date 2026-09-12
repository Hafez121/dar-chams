#!/usr/bin/env python3
"""
Resize one photograph into a site image slot: WebP + JPEG fallback, EXIF
stripped, both under a byte budget.

    tools/_process_photo.py SRC DEST_STEM WIDTH HEIGHT [BUDGET_BYTES]

Every encode starts from the same resized pixels. Re-encoding an already
encoded JPEG at a lower quality does not reliably shrink it — it re-encodes
the previous pass's artefacts as if they were image detail, and can make the
file substantially larger. That mistake is why this file exists.
"""
import io
import sys
from PIL import Image, ImageOps

# Floor at 46: below this these photographs show visible blocking in the stone
# and foliage texture. If a slot cannot fit its budget at 46 or better, the
# answer is smaller dimensions, not a worse encode.
QUALITIES = list(range(88, 45, -3))


def encode(img, fmt, quality):
    buf = io.BytesIO()
    if fmt == "JPEG":
        img.save(buf, "JPEG", quality=quality, optimize=True, progressive=True)
    else:
        img.save(buf, "WEBP", quality=quality, method=6)
    return buf.getvalue()


def best_under(img, fmt, budget):
    """Highest quality whose encode fits the budget, else the smallest we can do."""
    fallback = None
    for q in QUALITIES:
        data = encode(img, fmt, q)
        if len(data) <= budget:
            return data, q, True
        fallback = (data, q)
    return fallback[0], fallback[1], False


def main():
    src, stem, w, h = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    budget = int(sys.argv[5]) if len(sys.argv) > 5 else 150 * 1024

    img = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
    img = ImageOps.fit(img, (w, h), Image.LANCZOS, centering=(0.5, 0.5))

    clean = Image.new("RGB", img.size)     # drops EXIF, ICC and every other block
    clean.paste(img)

    over = 0
    for fmt, ext in (("WEBP", "webp"), ("JPEG", "jpg")):
        data, q, fitted = best_under(clean, fmt, budget)
        with open(f"{stem}.{ext}", "wb") as fh:
            fh.write(data)
        kb = len(data) // 1024
        if fitted:
            print(f"    {ext:<4} {w}x{h}  q{q:<3} {kb:>4} KB")
        else:
            print(f"    {ext:<4} {w}x{h}  q{q:<3} {kb:>4} KB  ** OVER BUDGET **")
            over += 1
    sys.exit(1 if over else 0)


if __name__ == "__main__":
    main()
