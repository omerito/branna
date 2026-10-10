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
   to `gh-pages`, which GitHub Pages serves. Until launch, `gh-pages` holds a placeholder page.

Branches `gh-pages`, `site-preview` and `ci-logs-*` are rewritten as a single commit on every publish
(`packaging/branna/publish.sh`), so build output never piles up in history.

**Fonts:** `packaging/branna/fonts.sh` assembles the `CRAFT_FONTS_DIR` build input: Noto Sans Ethiopic
Regular and SemiBold (v2.102, OFL-1.1, Monotype for the Noto project), plus craft-fonts' Japanese
faces for the desktop app and tests. The web build carries only the Ethiopic faces.

The inherited PdfCraft workflows (desktop releases, FreeBSD, Windows ARM, nightly fuzzing) are removed
in this fork. Desktop releases come back in Phase 3 if wanted.

## Keeping up with PdfCraft

PdfCraft changes fast (often 50–150 commits a day, many touching UI strings). Weekly:

1. `git fetch https://github.com/storytold/pdfcraft main` and merge it into a branch `sync/<date>`.
2. Resolve conflicts. Files Branna replaces wholesale keep Branna's version; workflows upstream
   edits that this fork deleted stay deleted.
3. Translate new strings: the Amharic coverage tests list every untranslated `tl!` literal.
4. Push the branch, wait for the Branna workflow to pass (read `ci-logs-*`), then merge to main.

Keep Branna's changes small and in as few upstream files as possible, so merges stay easy. Mark
Branna-specific code with a `// Branna:` comment.

## Phases

- [x] **Phase 0 — Setup.** Workflow, fonts script, placeholder site, this plan.
- [ ] **Phase 1 — Branna v0.1, the Amharic interface (public launch).**
  - [ ] `crates/ui-egui/src/i18n/am.tsv`: every UI string in Amharic; coverage tests like Italian's.
  - [ ] Noto Sans Ethiopic in the interface font stacks (slightly enlarged for legibility), including the web build.
  - [ ] Amharic is the default ("Auto" resolves to Amharic).
  - [ ] Rebrand: name, original logo, links (Help menu, About, Home), update checks; ArtCraft logos removed.
  - [ ] README, NOTICE, ATTRIBUTION for the fork.
  - [ ] Amharic loading screen; smaller download.
  - [ ] Check the built site in a browser in Amharic; then set `PUBLISH_SITE: "true"`.
- [ ] **Phase 2 — Amharic inside PDFs.** Today, Amharic typed into form fields is drawn as `?`
  (`crates/forms/src/appearance.rs` falls back to WinAnsi Helvetica) and adding or editing text in
  Amharic fails (`crates/edit/src/text.rs` only has Japanese fallback faces).
  - [ ] Form fields: draw Amharic values with an embedded Ethiopic font.
  - [ ] Added and edited text, free-text comments: Ethiopic fallback face.
  - [ ] Rendering: substitute an Ethiopic face for common non-embedded Ethiopic fonts (Nyala, Ebrima, …).
  - [ ] Typing: test Windows' Amharic input, Keyman and phone keyboards in the web app.
- [ ] **Phase 3 — Later, if people use Branna.** Built-in phonetic Amharic keyboard; desktop
  downloads; phone app. Not planned: Amharic text recognition (the OCR engine reads Latin only).

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
