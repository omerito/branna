# ብራና · Branna

Branna is a free PDF workbench with an Amharic interface, published at
<https://omerito.github.io/branna>. It is a fork of [PdfCraft](https://github.com/storytold/pdfcraft)
by the ArtCraft team (MIT OR Apache-2.0). ብራና is the parchment Ethiopia's manuscripts were written on.

This file is the fork's plan and working notes. Read it before working in this repository. Where it
differs from `CLAUDE.md` and `AGENTS.md` (upstream's instructions), this file wins for Branna-specific
matters; everything else in those files still applies (never crash, asset licensing, clean-room,
quality gates).

## Decisions (2026-10-10, by the owner, @omerito)

- **Language:** Branna opens in Amharic for everyone. English and the other upstream languages stay
  one click away in Preferences.
- **Launch:** go public after Phase 1 (Amharic interface). Amharic-in-PDF features follow as updates.
- **Logo:** an original Branna logo (contributor-original, MIT OR Apache-2.0), replaceable later.
- **Upstream:** merge PdfCraft's updates weekly, automatically, and translate new strings.
- **Free:** Branna is free and stays open source.

## Licence obligations (keep these true)

- Keep `LICENSE-MIT`, `LICENSE-APACHE`, `NOTICE`, `ATTRIBUTION.toml` and `ATTRIBUTION.md`, and state in
  `NOTICE` and the README that Branna is a modified version of PdfCraft.
- **Remove the ArtCraft brand.** `docs/brand/LICENSE-brand.txt` allows the ArtCraft name, wordmark and
  logos only unmodified and only in PdfCraft; forks must remove them. Never present Branna as an
  ArtCraft product. A plain-text credit ("based on PdfCraft by the ArtCraft team") is fine.
- Fonts and other assets follow `AGENTS.md` §1: open licences only, one `ATTRIBUTION.toml` entry each,
  no font files committed (Branna's fonts are fetched at build time, pinned by SHA-256).

## How building and publishing work

This repository's workspace sessions often can't reach the Rust download servers, so GitHub Actions
builds everything (`.github/workflows/branna.yml`). Every push to any branch:

1. **Test**: fmt, clippy, `cargo test --workspace` (with craft-fonts and the Ethiopic fonts), `cargo xtask assets`.
2. **Web build**: `trunk build --release` with only the Ethiopic fonts, then the site goes to the
   `site-preview` branch.
3. Each job writes its logs to `ci-logs-test` / `ci-logs-web` (`git fetch origin ci-logs-web`), so
   results can be read without Actions access.
4. On `main`, when `PUBLISH_SITE` in the workflow is `"true"` and the tests pass, the site is published
   to `gh-pages`, which GitHub Pages serves (`PUBLISH_SITE` is `"true"` since the launch on 2026-10-10).

Branches `gh-pages`, `site-preview` and `ci-logs-*` are rewritten as a single commit on every publish
(`packaging/branna/publish.sh`), so build output never piles up in history.

Reading results without Actions access (the `gh` CLI works; the Actions API may not):

```sh
gh api repos/omerito/branna/commits/<sha>/check-runs --jq '.check_runs[] | [.name, .status, .conclusion // "-"] | @tsv'
git fetch -q --depth 1 origin "+refs/heads/ci-logs-test:refs/remotes/origin/ci-logs-test"
git show origin/ci-logs-test:summary.txt; git show origin/ci-logs-test:test.log | grep -nE "panicked|FAILED|^error"
git fetch -q --depth 1 origin "+refs/heads/site-preview:refs/remotes/origin/site-preview"
git archive origin/site-preview | tar -x -C <empty dir>   # the built site, to serve and look at
```

**Download size:** GitHub Pages can't be told to compress the 35 MB WebAssembly file, so the web
build ships a gzip copy (about 13 MB) and `packaging/branna/precompress.py` changes trunk's loader in
the built `index.html` to fetch it and unpack it with the browser's `DecompressionStream` (falling
back to the full file). Those dozen generated lines are Branna's only JavaScript; upstream's "no
handwritten JS" rule otherwise holds.

**Without cargo** (sessions that can't reach crates.io), two scripts stand in for the Rust checks;
CI's real checks stay the authority:

- `python3 packaging/branna/catalog.py` validates `am.tsv` like `catalog.rs` and lists what Amharic
  lacks (entries Italian has, `tl!`/`bt!` literals).
- `python3 packaging/branna/assets.py [--rehash] [--write]` is `cargo xtask assets [--write]`;
  `--rehash` first updates the SHA-256 of `am.tsv`, `en.tsv` and `assets/branna/*` in
  `ATTRIBUTION.toml`. Run it after every change to those files.
- `rustfmt --edition 2024 --check <file.rs>` usually works locally.

**Fonts:** `packaging/branna/fonts.sh` assembles the `CRAFT_FONTS_DIR` build input: Noto Sans Ethiopic
Regular and SemiBold (v2.102, OFL-1.1, Monotype for the Noto project), plus craft-fonts' Japanese
faces for the desktop app and tests. The web build carries only the Ethiopic faces.

The inherited PdfCraft workflows (desktop releases, FreeBSD, Windows ARM, nightly fuzzing) are removed
in this fork. Desktop releases come back in Phase 3 if wanted.

## Keeping up with PdfCraft

PdfCraft changes fast (often 50–150 commits a day, many touching UI strings). A weekly scheduled
task does this:

1. From `main`, make a branch `sync/<YYYY-MM-DD>`, `git fetch https://github.com/storytold/pdfcraft main`
   and merge `FETCH_HEAD` into it.
2. Resolve conflicts:
   - What this fork deleted stays deleted (`git rm`): `.github/workflows/` except `branna.yml`,
     `docs/brand/`, `docs/images/pdfcraft-tools.png`.
   - `README.md` stays Branna's.
   - Everywhere else (`NOTICE`, `ATTRIBUTION.toml`, `links.rs`, `index.html`, code) keep both
     sides: upstream's change and Branna's lines (marked `// Branna:` in code). Leave out anything
     that brings back the ArtCraft brand or the Discord and ArtCraft website links. Then regenerate
     `ATTRIBUTION.md` (`assets.py --write`).
   - A new upstream language goes after Amharic in `LANGUAGES` (and `DATE_LANGUAGES`; fix the array
     lengths). If the web build has no font for its script, leave it out in `branna::drawable_on_web`.
   - `Cargo.lock`: take upstream's (`git checkout --theirs Cargo.lock`), then re-add Branna's one
     change, `"js-sys",` in the `dependencies` of `pdfcraft-engine`.
3. Translate what's new: `catalog.py` lists it. Follow the style guide below, keep the meaning of
   the English, and add the entries to `am.tsv` (anywhere; the end of the main section is fine).
   An upstream English string that names PdfCraft also needs an `en.tsv` entry. Then
   `assets.py --rehash`.
4. Push the branch and wait for the Branna workflow (about 10 minutes). Fix what fails, then
   fast-forward `main` to the branch and push; that publishes the site.
5. If upstream breaks something Branna can't fix quickly, leave `main` alone, push the branch, and
   open an issue saying what's wrong.

Keep Branna's changes small and in as few upstream files as possible, so merges stay easy. Mark
Branna-specific code with a `// Branna:` comment.

## Phases

- [x] **Phase 0 — Setup.** Workflow, fonts script, placeholder site, this plan.
- [x] **Phase 1 — Branna v0.1, the Amharic interface (public launch, 2026-10-10).**
  - [x] `crates/ui-egui/src/i18n/am.tsv`: every UI string in Amharic (first draft, over 2,100 entries);
    coverage tests in `crates/ui-egui/src/branna.rs`.
  - [x] Noto Sans Ethiopic in the interface font stacks, drawn 10% larger (`theme::ETHIOPIC_SCALE`),
    including the web build (`crates/fonts/build.rs` keeps `Ethi` faces on wasm).
  - [x] Amharic is the default ("Auto" resolves to Amharic, `branna::AMHARIC_BY_DEFAULT`).
  - [x] Rebrand: name, original mark (`assets/branna/branna-mark.svg`), links (Help menu, About,
    Home, top bar), update checks; ArtCraft logos and community links removed.
  - [x] README, NOTICE, ATTRIBUTION for the fork.
  - [x] Amharic loading screen (`apps/pdfcraft-web/index.html`); the web build leaves the Japanese
    font out (about 4.7 MB).
  - [x] Check the built site in a browser in Amharic (home, documents, Amharic search and typing,
    menus, command palette, Preferences, About, print, protect, dark theme); then set
    `PUBLISH_SITE: "true"`.
  - [x] Integrate `phase-1` into `main` and verify the public deployment. The
    [release workflow](https://github.com/omerito/branna/actions/runs/38087535832) passed;
    the live Amharic app opened and rendered a synthetic two-page PDF and navigated to page 2.
  - [ ] A fluent Amharic speaker reviews `am.tsv` (a first draft; wording fixes are welcome).
- [ ] **Phase 2 — Amharic inside PDFs.** Today, Amharic typed into form fields is drawn as `?`
  (`crates/forms/src/appearance.rs` falls back to WinAnsi Helvetica) and adding or editing text in
  Amharic fails (`crates/edit/src/text.rs` only has Japanese fallback faces).
  - [ ] Form fields: draw Amharic values with an embedded Ethiopic font.
  - [ ] Added and edited text, free-text comments: Ethiopic fallback face.
  - [ ] Rendering: substitute an Ethiopic face for common non-embedded Ethiopic fonts (Nyala, Ebrima, …).
  - [ ] Typing: test Windows' Amharic input, Keyman and phone keyboards in the web app.
- [ ] **Phase 3 — Later, if people use Branna.** Built-in phonetic Amharic keyboard; desktop
  downloads; phone app. Not planned: Amharic text recognition (the OCR engine reads Latin only).

## How the rebrand works (keep it this way: it keeps merges easy)

- Upstream's English strings stay in the code untouched; they are every catalog's lookup keys.
- `crates/ui-egui/src/i18n/en.tsv` renames the app in the English text (each entry: upstream's text
  with Branna for PdfCraft). `branna.rs` tests fail if a new English string names PdfCraft without
  an entry there.
- Every catalog's translations are rebranded as they load (`branna::rebrand`, PdfCraft → Branna), so
  the other upstream languages name Branna too. Text that must name the upstream project writes it
  through a `{upstream}` placeholder.
- Strings only Branna shows use `bt!("…")` (not `tl!`), so upstream's per-language coverage tests
  don't require them in every catalog; `am.tsv` translates them (its last section).
- Known leftovers: saved PDFs still record PdfCraft as their Producer (the engine is PdfCraft's), and
  the desktop app icons in `assets/app-icon/` are still PdfCraft's (desktop builds are Phase 3).
- After changing `am.tsv`, `en.tsv` or `assets/branna/*`, update their SHA-256 in `ATTRIBUTION.toml`
  (`python3 packaging/branna/assets.py --rehash`).

Other Branna changes to upstream code, all marked `// Branna:`:

- On the web the engine reads the browser's clock and time zone (`crates/engine/src/lib.rs`,
  `js-sys`); upstream has no clock there, so its dates read 1970.
- The language lists on the web offer only languages the bundled fonts can draw (`branna::offered`),
  because the web build carries no Japanese, Chinese or Telugu faces.
- The default comment author without a login name (the web) is translated ("Guest", `comments.rs`),
  and the print dialog's Print / Save as PDF button goes through `tl!` (`print_ui.rs`).
- Discord, the ArtCraft website and the ArtCraft logos are gone from the top bar, Help menu, Home and
  About (`chrome.rs`, `commands.rs`, `home.rs`, `dialogs.rs`, `widgets.rs`); the update check and
  links point to this repository (`links.rs`, `updates.rs`).

## Amharic style guide (for `am.tsv`)

- **Commands and buttons** use the short imperative: ክፈት, አስቀምጥ, አትም, ዝጋ, ቀልብስ, ድገም.
- **Sentences addressed to the reader** use the polite form: ይምረጡ, ፋይልዎ, እባክዎ … ይሞክሩ.
- **Names:** Branna is ብራና. "PDF" is ፒዲኤፍ in running text. Technical names (JavaScript, OCR,
  XFA, ISO 32000, PDF/A, file extensions) stay in Latin letters.
- **Numbers** use Western digits (1, 2, 3). Keep every `{placeholder}` and every trailing `…`.
- **Punctuation:** ። ends a sentence, ፣ separates list items; `:` and `?` as in English labels.
- **Terms** (keep consistent): ሰነድ document, ገጽ page, ፋይል file, ቅጽ form, መስክ field,
  አስተያየት comment, ዕልባት bookmark, ፊርማ signature, ማህተም stamp, አባሪ attachment,
  ንብርብር layer, ድንክዬ thumbnail, ምርጫዎች preferences, የይለፍ ቃል password, ማጉላት zoom.
- Clean-room: translate from the meaning of the English text; never copy another product's strings.
