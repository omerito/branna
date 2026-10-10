<p align="center">
  <img src="assets/branna/branna-mark.svg" alt="" width="96">
</p>

<h1 align="center">ብራና · Branna</h1>

<p align="center">
  <b>በአማርኛ ነጻ የፒዲኤፍ መሣሪያ።</b><br>
  <b>A free PDF workbench with an Amharic interface.</b>
</p>

<p align="center">
  <a href="https://omerito.github.io/branna"><b>omerito.github.io/branna</b></a> ·
  <a href="https://github.com/omerito/branna/issues">ችግር ሪፖርት ያድርጉ / Report a problem</a>
</p>

---

## ስለ ብራና

ብራና ፒዲኤፎችን ለማንበብ፣ ለማደራጀት፣ ለማዋሃድ፣ ለመከፋፈል፣ አስተያየት ለመስጠት፣ ቅጾችን ለመሙላት፣ ለመፈረም እና ለመጠበቅ የሚያገለግል ነጻ መሣሪያ ነው። መላው በይነገጹ በአማርኛ ነው፤ እንግሊዝኛና ሌሎች ቋንቋዎችም በ«ምርጫዎች» ውስጥ ይገኛሉ።

- **በአሳሽዎ ውስጥ ይሠራል።** ምንም መጫን አያስፈልግም፤ ፋይሎችዎ ከኮምፒውተርዎ አይወጡም።
- **ነጻና ክፍት ምንጭ ነው።** መለያ፣ ማስታወቂያ ወይም የአጠቃቀም ክትትል የለም።
- ስሙ፣ ብራና፣ ጥንታዊ የኢትዮጵያ መጻሕፍት የተጻፉበት የቆዳ ወረቀት ነው።

የመጀመሪያው ጭነት ወደ 14 MB ያወርዳል፤ በዝግተኛ ኢንተርኔት ጥቂት ደቂቃዎች ሊወስድ ይችላል።

## About Branna

Branna reads, organizes, combines, splits, comments on, fills in, signs and protects PDFs, with its
whole interface in Amharic. English and the other languages are in Preferences.

- **Runs in your browser.** Nothing to install; your files never leave your computer.
- **Free and open source.** No account, no ads, no tracking.
- ብራና is the parchment Ethiopia's old manuscripts were written on.

The first visit downloads about 14 MB, so it can take a few minutes on a slow connection.

### What's coming

Amharic *inside* PDFs: filling in forms, adding text and comments in Amharic, and showing PDFs that
use Ethiopian fonts they don't embed. See [BRANNA.md](BRANNA.md) for the plan.

### Help make Branna better

- Found a problem or have an idea? [Open an issue](https://github.com/omerito/branna/issues).
- Speak Amharic? Better wording for the interface is very welcome: the translations are in
  [`crates/ui-egui/src/i18n/am.tsv`](crates/ui-egui/src/i18n/am.tsv) (English text, then Amharic).

## Built on PdfCraft

Branna is a modified version of [PdfCraft](https://github.com/storytold/pdfcraft), the open-source,
clean-room PDF application written in Rust by the ArtCraft team. Branna adds the Amharic interface,
the Ge'ez fonts and its own name and design, and follows PdfCraft's updates every week. Branna is
not an ArtCraft product, and it doesn't use the ArtCraft name or logos.

For how the engine works, how to build it and how to contribute to it, see
[PdfCraft's README](https://github.com/storytold/pdfcraft#readme). Branna's own build, publishing
and translation notes are in [BRANNA.md](BRANNA.md).

## License and credits

Branna, like PdfCraft, is dual-licensed under [MIT](LICENSE-MIT) or [Apache-2.0](LICENSE-APACHE), at
your option. Copyright the ArtCraft Team and the PdfCraft contributors, and the Branna contributors.

Bundled fonts, icons and other assets keep their own open licenses, listed with their authors and
sources in [ATTRIBUTION.md](ATTRIBUTION.md) and [NOTICE](NOTICE). Amharic text is drawn with
[Noto Sans Ethiopic](https://github.com/notofonts/ethiopic) (SIL Open Font License 1.1).

<sub>Adobe and Acrobat are trademarks or registered trademarks of Adobe Inc. in the United States and/or other countries. Branna and PdfCraft are independent, open-source projects and are not affiliated with, sponsored by or endorsed by Adobe Inc.</sub>
