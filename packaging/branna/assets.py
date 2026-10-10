"""Check (or fix) the asset list like `cargo xtask assets [--write]`, for sessions without cargo.

Usage: python3 packaging/branna/assets.py [--rehash [PATH ...]] [--write]

  (no options)  check ATTRIBUTION.toml and ATTRIBUTION.md like `cargo xtask assets`
  --rehash      first update the SHA-256 in ATTRIBUTION.toml of PATHs (default: Branna's own
                assets, i18n/am.tsv, i18n/en.tsv and assets/branna/*) after editing them
  --write       first regenerate ATTRIBUTION.md from ATTRIBUTION.toml

A port of xtask/src/assets.rs (its licence allowlist is read from the Rust source). CI runs the real
`cargo xtask assets`, which stays the authority: if the two ever disagree, fix this port.
"""
import hashlib
import os
import re
import subprocess
import sys
import tomllib

root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
args = sys.argv[1:]
write = "--write" in args
BRANNA_ASSETS = ["crates/ui-egui/src/i18n/am.tsv", "crates/ui-egui/src/i18n/en.tsv"]


def rehash(paths):
    """Set each path's `sha256 = "…"` in its [[asset]] entry to the file's current hash."""
    toml_path = os.path.join(root, "ATTRIBUTION.toml")
    text = open(toml_path, encoding="utf-8").read()
    for path in paths:
        digest = hashlib.sha256(open(os.path.join(root, path), "rb").read()).hexdigest()
        entry = re.compile(r'(\npath = "' + re.escape(path) + r'"\n(?:(?!\n\[\[)[^\n]*\n)*?sha256 = ")[0-9a-f]{64}(")')
        text, n = entry.subn(lambda m: m.group(1) + digest + m.group(2), text)
        if n != 1:
            sys.exit(f"{path}: expected one [[asset]] entry with a sha256 in ATTRIBUTION.toml, found {n}")
        print(f"{path}: sha256 {digest}")
    open(toml_path, "w", encoding="utf-8").write(text)


if "--rehash" in args:
    named = [a for a in args[args.index("--rehash") + 1:] if not a.startswith("--")]
    if not named:
        branna_dir = os.path.join(root, "assets", "branna")
        named = BRANNA_ASSETS + sorted("assets/branna/" + f for f in os.listdir(branna_dir))
    rehash(named)

BRAND = "LicenseRef-Storyteller-Trademark"
EXT = set("""png jpg jpeg gif svg ico icns webp bmp tif tiff avif heic ttf otf ttc woff woff2 pfb
pfa afm icc icm pdf eps ps ai psd mp3 wav ogg flac mp4 mov webm cur ani brotli tsv""".split())

# The licence allowlist, read from the Rust source so this port never drifts.
src = open(os.path.join(root, "xtask/src/assets.rs"), encoding="utf-8").read()
start = src.index("pub const ALLOWED_LICENCES")
block = src[start: src.index("];", start)]
ALLOWED = {part.split('"')[1] for part in block.split(",") if '"' in part}

m = tomllib.load(open(os.path.join(root, "ATTRIBUTION.toml"), "rb"))
assets = m.get("asset", [])
bundled = m.get("bundled", [])
fetched = m.get("fetched", [])
inputs = m.get("build_input", [])


def esc(t):
    return t.replace("|", "\\|")


s = []
s.append("# Attribution\n\n")
s.append("<!-- Generated from ATTRIBUTION.toml by `cargo xtask assets --write`. Do not edit by hand. -->\n\n")
s.append("Every asset PdfCraft includes, bundles or uses to build its published material, with its author, source and licence. ")
s.append("The policy is in [AGENTS.md](AGENTS.md) §1. The machine-readable list, with SHA-256 hashes, is [ATTRIBUTION.toml](ATTRIBUTION.toml). ")
s.append("Licence texts are kept beside the assets and summarised in [NOTICE](NOTICE).\n\n")
s.append(f"## In this repository ({len(assets)})\n\n| Asset | Title | Author | Licence | Source | Used for |\n|---|---|---|---|---|---|\n")
for a in assets:
    s.append(f"| `{a['path']}` | {esc(a['title'])} | {esc(a['author'])} | {a['licence']} | {esc(a['source'])} | {esc(a['usage'])} |\n")
s.append(f"\n## Compiled in through dependencies ({len(bundled)})\n\n| Crate | File | Title | Author | Licence | Source | Used for |\n|---|---|---|---|---|---|---|\n")
for b in bundled:
    note = " (non-visual data, AGENTS.md §1.1)" if b.get("adobe_data") else ""
    s.append(f"| `{b['crate']}` {b['version']} | `{b['path']}` | {esc(b['title'])}{note} | {esc(b['author'])} | {b['licence']} | {esc(b['source'])} | {esc(b['usage'])} |\n")
s.append(
    f"\n## Downloaded at build time ({len(fetched)})\n\nFonts are fetched by `cargo xtask demo-pdf` into `target/demo-fonts/`, OCR models by `cargo xtask models` into `assets/models/`; each is verified by SHA-256 and never committed.\n\n| File | Title | Author | Licence | Source | Used for |\n|---|---|---|---|---|---|\n"
)
for f in fetched:
    s.append(f"| `{f['file']}` | {esc(f['title'])} | {esc(f['author'])} | {f['licence']} | {esc(f['source'])} | {esc(f['usage'])} |\n")
s.append(
    f"\n## Optional build inputs ({len(inputs)})\n\nNot in this repository and never downloaded by it: compiled in only when the build sets the option (official releases do). Each input attributes its own files.\n\n| Input | Option | Title | Author | Licence | Source | Attribution | Used for |\n|---|---|---|---|---|---|---|---|\n"
)
for b in inputs:
    s.append(f"| `{b['name']}` | `{b['option']}` | {esc(b['title'])} | {esc(b['author'])} | {b['licence']} | {esc(b['source'])} | {esc(b['attribution'])} | {esc(b['usage'])} |\n")
markdown = "".join(s)

problems = []
md_path = os.path.join(root, "ATTRIBUTION.md")
if write:
    open(md_path, "w", encoding="utf-8").write(markdown)
    print("wrote ATTRIBUTION.md")
if open(md_path, encoding="utf-8").read() != markdown:
    problems.append("ATTRIBUTION.md is out of date")


def ids(expr):
    return [t for t in expr.replace("(", " ").replace(")", " ").split() if t not in ("OR", "AND", "WITH")]


visual = {"icon", "image", "font", "logo", "cursor", "video", "translation"}
seen = set()
for a in assets:
    if a["path"] in seen:
        problems.append(f"{a['path']}: listed twice")
    seen.add(a["path"])
    brand = a["licence"] == BRAND and a["kind"] == "logo" and a["path"].startswith("docs/brand/")
    if not brand:
        for i in ids(a["licence"]):
            if i not in ALLOWED:
                problems.append(f"{a['path']}: licence {i} not allowed")
    if not os.path.isfile(os.path.join(root, a["licence_file"])):
        problems.append(f"{a['path']}: licence file {a['licence_file']} missing")
    if a["kind"] in visual and any("adobe" in a[k].lower() for k in ("author", "source", "title")):
        problems.append(f"{a['path']}: Adobe")
    p = os.path.join(root, a["path"])
    if not os.path.isfile(p):
        problems.append(f"{a['path']}: listed but missing")
    elif hashlib.sha256(open(p, "rb").read()).hexdigest() != a["sha256"]:
        problems.append(f"{a['path']}: SHA-256 mismatch")
files = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"], cwd=root, capture_output=True, check=True).stdout
for f in files.split(b"\0"):
    f = f.decode()
    if f and f.rsplit(".", 1)[-1].lower() in EXT and "." in f and f not in seen and os.path.isfile(os.path.join(root, f)):
        problems.append(f"{f}: asset has no ATTRIBUTION.toml entry")
for b in inputs:
    for i in ids(b["licence"]):
        if i not in ALLOWED:
            problems.append(f"{b['name']}: licence {i} not allowed")
    if not b["source"].startswith("https://") or not b["attribution"].startswith("https://"):
        problems.append(f"{b['name']}: URLs must be https")
for p in problems:
    print("  ✗", p)
print(f"assets: {'ok' if not problems else str(len(problems)) + ' problem(s)'} ({len(assets)} repository assets)")
sys.exit(1 if problems else 0)
