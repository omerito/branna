#!/usr/bin/env bash
# Assemble Branna's font build input (the directory CRAFT_FONTS_DIR points at).
#
# Usage: packaging/branna/fonts.sh OUT_DIR [CRAFT_FONTS_CHECKOUT]
#
# Writes OUT_DIR/fonts/manifest.txt in craft-fonts' format plus the font files it lists:
# - Noto Sans Ethiopic Regular and SemiBold (OFL-1.1, Monotype for the Noto project), downloaded
#   from the official notofonts release and checked against a pinned SHA-256. Branna's Amharic
#   interface draws Ge'ez text with them.
# - With CRAFT_FONTS_CHECKOUT, everything in that craft-fonts checkout too (the Japanese faces the
#   desktop app and the test suite expect). The web build leaves it out to keep the download small.
#
# Font files are never committed to this repository (AGENTS.md §1.4); this script fetches them at
# build time, pinned by hash, the same way craft-fonts is pinned by commit.
set -euo pipefail

OUT="${1:?usage: fonts.sh OUT_DIR [CRAFT_FONTS_CHECKOUT]}"
CRAFT="${2:-}"

NOTO_ETHIOPIC_VERSION="NotoSansEthiopic-v2.102"
NOTO_ETHIOPIC_URL="https://github.com/notofonts/ethiopic/releases/download/${NOTO_ETHIOPIC_VERSION}/${NOTO_ETHIOPIC_VERSION}.zip"
NOTO_ETHIOPIC_ZIP_SHA256="4e3e53aa1586344ba842f310ab35c65281fa11e8cc2d259613ad06a9ae994d52"

mkdir -p "$OUT/fonts"
if [ -n "$CRAFT" ]; then
  [ -f "$CRAFT/fonts/manifest.txt" ] || { echo "error: $CRAFT has no fonts/manifest.txt" >&2; exit 1; }
  cp -R "$CRAFT/fonts/." "$OUT/fonts/"
else
  : > "$OUT/fonts/manifest.txt"
fi

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
curl -fsSL --retry 3 -o "$WORK/noto-ethiopic.zip" "$NOTO_ETHIOPIC_URL"
echo "$NOTO_ETHIOPIC_ZIP_SHA256  $WORK/noto-ethiopic.zip" | sha256sum -c --quiet -

DEST="$OUT/fonts/noto-sans-ethiopic"
mkdir -p "$DEST"
# Read only the named members (the archive also holds a "../OFL.txt" entry, so never unzip it whole).
python3 -I - "$WORK/noto-ethiopic.zip" "$DEST" <<'PY'
import sys, zipfile, pathlib
archive, dest = sys.argv[1], pathlib.Path(sys.argv[2])
members = {
    "NotoSansEthiopic/unhinted/ttf/NotoSansEthiopic-Regular.ttf": "NotoSansEthiopic-Regular.ttf",
    "NotoSansEthiopic/unhinted/ttf/NotoSansEthiopic-SemiBold.ttf": "NotoSansEthiopic-SemiBold.ttf",
    "../OFL.txt": "OFL.txt",
}
with zipfile.ZipFile(archive) as z:
    for name, target in members.items():
        (dest / target).write_bytes(z.read(name))
PY

SOURCE="https://github.com/notofonts/ethiopic/releases/tag/${NOTO_ETHIOPIC_VERSION}"
{
  echo ""
  echo "# Branna: Ge'ez script for the Amharic interface (packaging/branna/fonts.sh)."
  for style in Regular SemiBold; do
    file="fonts/noto-sans-ethiopic/NotoSansEthiopic-${style}.ttf"
    sum="$(sha256sum "$OUT/$file" | cut -d' ' -f1)"
    echo "Noto Sans Ethiopic | ${style} | ${file} | Ethi | OFL-1.1 | fonts/noto-sans-ethiopic/OFL.txt | ${sum} | ${SOURCE}"
  done
} >> "$OUT/fonts/manifest.txt"

echo "wrote $OUT/fonts/manifest.txt:"
grep -v '^#' "$OUT/fonts/manifest.txt" | grep -v '^$' | cut -d'|' -f1-4
