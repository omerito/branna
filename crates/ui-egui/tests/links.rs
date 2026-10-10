//! Branna's links: the feedback button is one click away everywhere; Help menu, About dialog and
//! home screen open Branna's pages. The ArtCraft brand and community links are gone (BRANNA.md).

use egui_kittest::Harness;
use egui_kittest::kittest::Queryable;
use pdfcraft_engine::links;
use pdfcraft_ui_egui::{Dialog, PdfCraftApp};

fn harness(setup: impl FnOnce(&mut PdfCraftApp) + 'static) -> Harness<'static, PdfCraftApp> {
    let mut h = Harness::builder().with_size(egui::vec2(1400.0, 900.0)).build_eframe(move |_cc| {
        let mut app = PdfCraftApp::new();
        app.set_option("language", "en").unwrap();
        setup(&mut app);
        app
    });
    h.run_steps(4);
    h
}

#[test]
fn feedback_button_in_the_top_bar_opens_the_issue_tracker() {
    let mut h = harness(|_| {});
    h.get_by_label("Feedback").click();
    h.run_steps(2);
    assert_eq!(h.state().last_opened_url.as_deref(), Some(links::FEEDBACK));
    assert_eq!(links::FEEDBACK, "https://github.com/omerito/branna/issues");
}

#[test]
fn home_screen_links() {
    for (label, url) in [
        ("Report a problem", links::FEEDBACK),
        ("Branna web page", "https://omerito.github.io/branna"),
        ("Branna on GitHub", "https://github.com/omerito/branna"),
    ] {
        let mut h = harness(|_| {});
        h.get_by_label("Help make Branna better");
        h.get_by_label(label).click();
        h.run_steps(2);
        assert_eq!(h.state().last_opened_url.as_deref(), Some(url), "{label}");
    }
    let h = harness(|_| {});
    assert_eq!(h.query_all_by_label_contains("ArtCraft").count(), 0, "no ArtCraft brand on the home screen");
    assert_eq!(h.query_all_by_label_contains("Discord").count(), 0);
}

#[test]
fn about_dialog_shows_the_brand_and_links() {
    let pdf = b"%PDF-1.7\n1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 200 200] >> endobj\ntrailer << /Root 1 0 R >>\n%%EOF";
    // With a document open, so the home screen's own links are not on screen.
    let mut h = harness(move |app| {
        app.open_bytes("one.pdf", None, pdf.to_vec()).unwrap();
        app.dialog = Some(Dialog::About);
    });
    assert!(h.query_all_by_label("Branna").count() >= 2, "the mark (alt text) and the name");
    h.get_by_label("Based on PdfCraft by the ArtCraft team.");
    h.get_by_label("Report a problem").click();
    h.run_steps(2);
    assert_eq!(h.state().last_opened_url.as_deref(), Some(links::FEEDBACK));
}

#[test]
fn help_commands_open_each_link() {
    for l in links::LINKS {
        let mut h = harness(|_| {});
        assert!(h.state_mut().execute(l.command), "{}", l.command);
        assert_eq!(h.state().last_opened_url.as_deref(), Some(l.url));
        assert_eq!(pdfcraft_engine::commands::command(l.command).unwrap().menu, Some("Help"));
    }
}

#[test]
fn about_dialog_has_contributors_and_models_tabs() {
    let mut h = harness(|app| app.dialog = Some(Dialog::About));
    h.get_by_label("Contributors").click();
    // Tab changes resize and recenter the modal as the compiled-in credits grow.
    // Let its layout settle before clicking the next control at its new position.
    h.run_steps(4);
    // The owner is always in the compiled-in credits (contributors/contributors.json), shown by username.
    h.get_by_label("@echelon");
    h.get_by_label("Table").click();
    h.run_steps(4);
    h.get_by_label("PRs");
    h.get_by_label("Display name").click();
    h.run_steps(4);
    h.get_by_label("Brandon Thomas");
    h.get_by_label("Models").click();
    h.run_steps(4);
    assert!(h.query_all_by_label("Anthropic").count() >= 1);
}
