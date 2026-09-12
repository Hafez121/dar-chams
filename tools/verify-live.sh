#!/usr/bin/env sh
# ---------------------------------------------------------------------------
# Dar Chams — verify the DEPLOYED site, not the local copy.
#
#   tools/verify-live.sh [base-url]
#
# Default base: https://hafez121.github.io/dar-chams/
#
# Checks, in order:
#   1. the base URL answers 200, not 404
#   2. that response really is index.html (the site's own markup, not a
#      GitHub Pages 404 page, which also renders HTML)
#   3. all four pages answer 200
#   4. images return image bytes — content-type AND magic number — so an HTML
#      404 saved under a .webp name cannot pass
#   5. the self-hosted fonts load over https (the thing file:// cannot do)
#   6. the stylesheet, the scripts and the SEO files answer 200
#   7. no retired identifier is still being served, and the real phone number
#      is. Removing something from the repository is not the same as it being
#      gone from the deployment, and this site was briefly live with invented
#      contact details that resolved to real people.
#
# A new Pages site takes a minute or two to build, so check 1 retries for up
# to five minutes before giving up. Everything after it runs once.
#
# Exit status 0 = every check passed. Non-zero = the number of failures.
# ---------------------------------------------------------------------------
set -u

BASE=${1:-https://hafez121.github.io/dar-chams/}
case "$BASE" in *[!/]) BASE="$BASE/";; esac

FAIL=0
pass() { printf '  \033[32mPASS\033[0m  %s\n' "$1"; }
fail() { printf '  \033[31mFAIL\033[0m  %s\n' "$1"; FAIL=$((FAIL + 1)); }

TMP=${TMPDIR:-/tmp}/darchams-verify.$$
trap 'rm -f "$TMP"' EXIT INT TERM

code_of()  { curl -sS -o /dev/null -w '%{http_code}' -m 25 "$1" 2>/dev/null; }
ctype_of() { curl -sS -o /dev/null -w '%{content_type}' -m 25 "$1" 2>/dev/null; }
# Download and read the signature locally. A Range request would be cheaper but
# not every static server honours one, and a server that ignores Range hands
# back the whole file - which then has to be inspected anyway.
magic_of() { curl -sS -m 40 -o "$TMP" "$1" 2>/dev/null && head -c 16 "$TMP" | od -An -tx1 | tr -d ' \n'; }

echo "Verifying ${BASE}"
echo

# -- 1. the base URL, with a wait for the very first deploy ------------------
echo "1. base URL responds"
n=0
while :; do
  code=$(code_of "$BASE")
  [ "$code" = "200" ] && break
  n=$((n + 1))
  if [ "$n" -ge 20 ]; then break; fi
  printf '  waiting for the first deploy… (attempt %s, last status %s)\n' "$n" "$code"
  sleep 15
done
if [ "$code" = "200" ]; then
  pass "$BASE -> 200"
else
  fail "$BASE -> $code after $n attempts (~5 min). Pages is probably not enabled yet."
  echo
  echo "Stopping: nothing below can pass while the site is not being served."
  exit 1
fi

# -- 2. it is really index.html, not a Pages 404 page ------------------------
echo
echo "2. the root path serves index.html"
body=$(curl -sS -m 25 "$BASE" 2>/dev/null)
if printf '%s' "$body" | grep -q 'Dar Chams — a stone guesthouse in Douma'; then
  pass 'served markup contains the index.html <title>'
else
  fail 'served markup is not index.html (a Pages 404 page also returns HTML)'
fi
printf '%s' "$body" | grep -q 'rel="canonical" href="https://hafez121.github.io/dar-chams/"' \
  && pass 'canonical tag matches the deployed URL' \
  || fail 'canonical tag does not match the deployed URL'

# -- 3. every page ------------------------------------------------------------
echo
echo "3. every page responds 200"
for p in "" index.html rooms.html village.html contact.html "index.html?lang=ar"; do
  c=$(code_of "${BASE}${p}")
  [ "$c" = "200" ] && pass "${p:-/} -> 200" || fail "${p:-/} -> $c"
done

# -- 4. images are image bytes, not an HTML error page ------------------------
echo
echo "4. images return image bytes"
for f in img/hero-valley.webp img/hero-valley.jpg img/roof-tiles.webp \
         img/terrace.webp img/room-linen.webp img/shutters.webp \
         img/olive-branch.webp img/stone-steps.webp img/valley-road.webp \
         img/og-cover.jpg favicon-32.png; do
  url="${BASE}${f}"
  c=$(code_of "$url")
  if [ "$c" != "200" ]; then fail "$f -> $c"; continue; fi
  ct=$(ctype_of "$url")
  sig=$(magic_of "$url")
  case "$ct" in
    image/*) ok_ct=1 ;;
    *)       ok_ct=0 ;;
  esac
  case "$sig" in
    52494646*57454250*) ok_magic=1 ;;   # "RIFF" .... "WEBP"
    ffd8ff*)            ok_magic=1 ;;   # JPEG
    89504e470d0a1a0a*)  ok_magic=1 ;;   # PNG
    *)                  ok_magic=0 ;;
  esac
  if [ "$ok_ct" = 1 ] && [ "$ok_magic" = 1 ]; then
    pass "$f -> 200, $ct, real image bytes"
  elif [ "$ok_ct" = 0 ]; then
    fail "$f -> 200 but content-type is '$ct' (an HTML error page?)"
  else
    fail "$f -> 200, $ct, but the file starts ${sig%"${sig#????????}"} - not an image signature"
  fi
done

# -- 5. the fonts, which file:// cannot serve ---------------------------------
echo
echo "5. self-hosted fonts load over https"
for f in fonts/cormorant-400.woff2 fonts/cormorant-600.woff2 \
         fonts/plexar-400.woff2 fonts/plexar-600.woff2; do
  url="${BASE}${f}"
  c=$(code_of "$url")
  if [ "$c" != "200" ]; then fail "$f -> $c"; continue; fi
  sig=$(magic_of "$url")
  ct=$(ctype_of "$url")
  case "$sig" in
    774f4632*) pass "$f -> 200, $ct, wOF2 signature present" ;;
    3c21444f*|3c68746d*)
      fail "$f -> 200 but the body is HTML, not a font (an error page)" ;;
    *) fail "$f -> 200 but the file starts ${sig%"${sig#????????}"}, not 774f4632 (wOF2)" ;;
  esac
done

# -- 6. the rest of what the pages ask for ------------------------------------
echo
echo "6. stylesheet, scripts and SEO files"
for f in css/style.css css/print.css js/i18n.js js/site.js \
         favicon.svg apple-touch-icon.png robots.txt sitemap.xml; do
  c=$(code_of "${BASE}${f}")
  [ "$c" = "200" ] && pass "$f -> 200" || fail "$f -> $c"
done

# -- 7. what is actually being served, not what is in the repository ----------
echo
echo "7. retired identifiers are gone from the served pages"
# "~" stands in for a space so the list can stay a shell word list. Both the
# dialling form and the printed form have to be here: the printed form is what
# a human copies off the page.
RETIRED="96171555019 71555019 +961~71~555~019 71~555~019 stay@darchams.com \
instagram.com/darchams facebook.com/darchams Rue~du~Vieux~Souk 34.2172 35.8339 \
Abou~Elias Douma~1304"
PAGE_HTML=""
for p in index.html rooms.html village.html contact.html js/i18n.js js/site.js; do
  PAGE_HTML="$PAGE_HTML
$(curl -sS -m 25 "${BASE}${p}" 2>/dev/null)"
done
for bad in $RETIRED; do
  needle=$(printf '%s' "$bad" | tr '~' ' ')
  if printf '%s' "$PAGE_HTML" | grep -qF "$needle"; then
    fail "the live site still serves \"$needle\""
  else
    pass "not served: $needle"
  fi
done
if printf '%s' "$PAGE_HTML" | grep -qF '96181520553'; then
  pass "the current WhatsApp number is served"
else
  fail "the current WhatsApp number (96181520553) is NOT on the live site"
fi

echo
if [ "$FAIL" -eq 0 ]; then
  echo "All checks passed against ${BASE}"
else
  echo "$FAIL check(s) failed against ${BASE}"
fi
exit "$FAIL"
