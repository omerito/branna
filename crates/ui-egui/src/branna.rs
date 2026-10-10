//! Branna: what this fork changes in the interface (see BRANNA.md at the repository root).
//!
//! - The app is called Branna (ብራና in Amharic). Catalog translations are rebranded as they load
//!   ([`rebrand`]), and `i18n/en.tsv` renames the app in the English text, so upstream's English
//!   strings (the catalog keys) stay as they are and merges from PdfCraft stay easy.
//! - Amharic (`i18n/am.tsv`) is the default interface language ([`AMHARIC_BY_DEFAULT`]).
//! - Strings only Branna shows go through [`bt!`]: translated by `am.tsv` like any other, but kept
//!   out of upstream's per-language coverage checks, which Branna's own tests below replace.
//! - The ArtCraft brand (its logos and community links) is removed, as its licence requires of
//!   forks; [`mark`] is Branna's own mark.

/// "Auto" in Preferences ▸ Interface language opens Branna in Amharic.
pub const AMHARIC_BY_DEFAULT: bool = true;

/// The app's name in the current interface language: ብራና in Amharic, Branna otherwise.
pub fn name() -> &'static str {
    t("Branna")
}

/// A Branna-only interface string in the current language (use [`bt!`]).
pub fn t(s: &'static str) -> &'static str {
    crate::i18n::tr(crate::i18n::current(), s)
}

/// A catalog translation as Branna shows it: the app's name is Branna. Strings that must name
/// the upstream project write it through a placeholder (`{upstream}`), which this leaves alone.
pub fn rebrand(translation: String) -> String {
    if translation.contains("PdfCraft") { translation.replace("PdfCraft", "Branna") } else { translation }
}

/// Branna's mark (contributor-original, `assets/branna/branna-mark.svg`), `size` points square.
pub fn mark(ui: &mut egui::Ui, size: f32) -> egui::Response {
    ui.add(
        egui::Image::from_bytes("bytes://branna-mark.svg", include_bytes!("../../../assets/branna/branna-mark.svg"))
            .fit_to_exact_size(egui::vec2(size, size))
            .alt_text(name()),
    )
}

/// Buttons for Branna's links: report a problem (prominent), the web page and the source code.
/// Returns the address of the one clicked.
pub fn links(ui: &mut egui::Ui) -> Option<&'static str> {
    use pdfcraft_engine::links;
    let mut clicked = None;
    ui.horizontal_wrapped(|ui| {
        ui.spacing_mut().item_spacing = egui::vec2(8.0, 8.0);
        if crate::widgets::icon_pill(ui, "messages-square", bt!("Report a problem"), true).on_hover_text(links::FEEDBACK).clicked() {
            clicked = Some(links::FEEDBACK);
        }
        for l in links::LINKS {
            if crate::widgets::icon_pill(ui, l.icon, tl!(l.label), false).on_hover_text(l.url).clicked() {
                clicked = Some(l.url);
            }
        }
    });
    clicked
}

#[cfg(test)]
mod tests {
    use crate::i18n::{Lang, has, tr};

    fn am() -> Lang {
        Lang::from_code("am").expect("am registered")
    }

    /// Every string literal passed to `macro` (`tl!(`, `bt!(`, also when it starts on the next line)
    /// in the UI source outside test modules, unescaped.
    fn literals(macro_call: &str) -> std::collections::BTreeSet<String> {
        let mut stack = vec![std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("src")];
        let mut found: std::collections::BTreeSet<String> = std::collections::BTreeSet::new();
        while let Some(dir) = stack.pop() {
            for entry in std::fs::read_dir(dir).expect("UI source directory") {
                let path = entry.expect("UI source entry").path();
                if path.is_dir() {
                    if path.file_name().is_some_and(|name| name != "i18n") {
                        stack.push(path);
                    }
                } else if path.extension().is_some_and(|ext| ext == "rs") {
                    let source = std::fs::read_to_string(&path).expect("UI source file").replace("\r\n", "\n");
                    let mut rest = source.split("#[cfg(test)]\nmod ").next().unwrap_or_default();
                    while let Some((_, after)) = rest.split_once(macro_call) {
                        let Some(after) = after.trim_start().strip_prefix('"') else {
                            rest = after;
                            continue;
                        };
                        let mut escaped = false;
                        let end = after
                            .char_indices()
                            .find_map(|(i, c)| {
                                if c == '"' && !escaped {
                                    return Some(i);
                                }
                                escaped = c == '\\' && !escaped;
                                None
                            })
                            .expect("closed literal");
                        let (raw, tail) = after.split_at(end);
                        let closing = tail.strip_prefix('"').expect("closing quote").trim_start();
                        if closing.strip_prefix(',').unwrap_or(closing).trim_start().starts_with(')') {
                            found.insert(serde_json::from_str(&format!("\"{raw}\"")).expect("literal escapes"));
                        }
                        rest = tail.strip_prefix('"').expect("closing quote");
                    }
                }
            }
        }
        found
    }

    /// Amharic translates every `tl!` and `bt!` literal in the UI source, so no string ships in
    /// English by accident after a merge from PdfCraft.
    #[test]
    fn amharic_covers_ui_literals() {
        let mut all = literals("tl!(");
        assert!(all.len() > 900, "source scan found only {} literals", all.len());
        let branna = literals("bt!(");
        assert!(branna.contains("Report a problem"), "bt! scan found {branna:?}");
        all.extend(branna);
        all.insert("Branna".into());
        let missing: Vec<_> = all.iter().filter(|label| !has(am(), label)).collect();
        assert!(missing.is_empty(), "untranslated Amharic UI literals: {missing:#?}");
    }

    /// Amharic translates every registered command and every All tools group, section and item.
    #[test]
    fn amharic_covers_commands_and_catalogue() {
        for command in pdfcraft_engine::commands::COMMANDS {
            assert!(has(am(), command.label), "missing command: {}", command.label);
            if let Some(menu) = command.menu {
                assert!(has(am(), menu), "missing menu: {menu}");
            }
        }
        for group in pdfcraft_engine::catalog::TOOL_GROUPS {
            assert!(has(am(), group.label), "missing group: {}", group.label);
            for section in group.sections {
                assert!(has(am(), section.title), "missing section: {}", section.title);
                for item in section.items {
                    assert!(has(am(), item.label), "missing item: {}", item.label);
                }
            }
        }
    }

    /// The English interface names Branna, never PdfCraft or ArtCraft, wherever upstream's English
    /// text does; and no catalog shows the ArtCraft brand.
    #[test]
    fn the_interface_names_branna() {
        let mut english: Vec<String> = literals("tl!(").into_iter().collect();
        english.extend(pdfcraft_engine::commands::COMMANDS.iter().map(|c| c.label.to_owned()));
        for s in english.iter().filter(|s| s.contains("PdfCraft") || s.contains("ArtCraft")) {
            let shown = tr(Lang::EN, s);
            assert!(!shown.contains("PdfCraft") && !shown.contains("ArtCraft"), "English shows {shown:?} for {s:?}: add it to i18n/en.tsv");
            assert!(!tr(am(), s).contains("ArtCraft"), "Amharic names ArtCraft for {s:?}");
        }
        assert_eq!(tr(Lang::EN, "Welcome to PdfCraft"), "Welcome to Branna");
        assert_eq!(tr(am(), "Welcome to PdfCraft"), "እንኳን ወደ ብራና በደህና መጡ");
        let ja = Lang::from_code("ja").expect("ja registered");
        assert!(!tr(ja, "Welcome to PdfCraft").contains("PdfCraft"), "other catalogs are rebranded too");
        assert_eq!(super::rebrand("Based on {upstream}".into()), "Based on {upstream}");
    }

    /// Amharic is the default and plural rules follow CLDR `am` (0 and 1 singular).
    #[test]
    fn amharic_is_registered_with_its_plural_rule() {
        assert!(super::AMHARIC_BY_DEFAULT);
        assert_eq!(crate::i18n::lang_from_tag("am_ET.UTF-8"), Some(am()));
        assert_eq!(crate::i18n::lang_from_tag("am"), Some(am()));
        assert_eq!(am().name(), "አማርኛ");
        assert_eq!(crate::i18n::trn(am(), 0, "{n} page", "{n} pages"), "0 ገጽ");
        assert_eq!(crate::i18n::trn(am(), 1, "{n} page", "{n} pages"), "1 ገጽ");
        assert_eq!(crate::i18n::trn(am(), 3, "{n} page", "{n} pages"), "3 ገጾች");
        assert!(pdfcraft_engine::dates::date_language("am").is_some(), "Amharic month and weekday names");
    }

    /// With the Ethiopic faces built in, every Amharic translation has glyphs: with all interface
    /// faces (desktop) and with the Ethiopic faces as the only build-input faces (the web build).
    #[test]
    fn amharic_labels_have_glyphs() {
        let ethiopic: Vec<String> = pdfcraft_fonts::ui_ethiopic_fonts().iter().map(|f| f.name()).collect();
        if ethiopic.is_empty() {
            eprintln!("skipping Amharic glyph checks: build with CRAFT_FONTS_DIR from packaging/branna/fonts.sh");
            return;
        }
        let text = include_str!("i18n/am.tsv");
        let labels: String = text
            .lines()
            .filter(|l| !l.starts_with('#'))
            .filter_map(|l| l.split('\t').nth(2))
            .flat_map(str::chars)
            .chain(am().name().chars())
            .filter(|c| !c.is_control())
            .collect();
        let mut ethiopic_only = crate::theme::font_definitions();
        for family in ethiopic_only.families.values_mut() {
            family.retain(|name| !pdfcraft_fonts::CRAFT_FONTS.iter().any(|face| face.name() == *name) || ethiopic.contains(name));
        }
        use egui::epaint::text::{Fonts, TextOptions};
        for (build, defs) in [("all faces", crate::theme::font_definitions()), ("Ethiopic faces only", ethiopic_only)] {
            let mut fonts = Fonts::new(TextOptions::default(), defs);
            for id in [egui::FontId::proportional(13.0), egui::FontId::monospace(13.0), crate::theme::medium(13.0), crate::theme::semibold(17.0)] {
                assert!(fonts.has_glyphs(&id, &labels), "{build}: {id:?} lacks an Amharic label glyph");
            }
        }
    }
}
