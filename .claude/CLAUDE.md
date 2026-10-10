# Branna (fork of PdfCraft)

This repository is **Branna**, an Amharic-first fork of PdfCraft owned by @omerito. Read
`BRANNA.md` first: it holds the owner's decisions, the phase plan, how the GitHub Actions build and
publishing work, the weekly upstream sync, and the Amharic style guide.

The root `CLAUDE.md` and `AGENTS.md` are upstream PdfCraft's instructions. Their engineering rules
still apply here (never crash, assets and licences, clean-room, quality gates), with these
differences:

- `plan/` (STATUS.md, execution-plan.md) does not exist in this fork; `BRANNA.md` is the plan.
- Builds and tests run in GitHub Actions. Read results from the `ci-logs-test` and `ci-logs-web`
  branches and try the built web app from `site-preview` (see `BRANNA.md`).
- Mark Branna-specific code with a `// Branna:` comment and keep upstream files' diffs small.
