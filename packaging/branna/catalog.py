"""Check the Amharic catalog without cargo (the Rust tests in crates/ui-egui stay the authority).

Usage: python3 packaging/branna/catalog.py

Validates crates/ui-egui/src/i18n/am.tsv the way crates/ui-egui/src/i18n/catalog.rs does (three
columns, escapes, {placeholders}, a trailing "…", two plural forms, no duplicates), then lists what
Amharic still lacks, like the tests in crates/ui-egui/src/branna.rs:
  - entries the Italian catalog has (amharic_has_every_italian_entry), and
  - tl!/bt! literals in the UI source (amharic_covers_ui_literals).
It can't see the engine's command and tool lists (amharic_covers_commands_and_catalogue): the
Italian check covers them in practice, and CI runs the real tests.

Exits 1 when there is anything to fix.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
I18N = os.path.join(ROOT, "crates", "ui-egui", "src", "i18n")
AMHARIC_PLURAL_FORMS = 2


def unescape(text):
    out, i = [], 0
    while i < len(text):
        c = text[i]
        if c != "\\":
            out.append(c)
            i += 1
            continue
        nxt = text[i + 1] if i + 1 < len(text) else ""
        if nxt not in ("n", "t", "\\"):
            raise ValueError(f"unknown escape \\{nxt}" if nxt else "trailing backslash")
        out.append({"n": "\n", "t": "\t", "\\": "\\"}[nxt])
        i += 2
    return "".join(out)


def placeholders(text):
    names, rest = [], text
    while "{" in rest:
        after = rest.split("{", 1)[1]
        if "}" not in after:
            break
        name, rest = after.split("}", 1)
        names.append(name)
    return sorted(names)


def entries(path):
    """[(line number, columns)] of the catalog's entry lines."""
    with open(path, encoding="utf-8") as f:
        return [(no, line.split("\t")) for no, line in enumerate(f.read().splitlines(), 1) if line.strip() and not line.startswith("#")]


def validate(path, forms):
    errors, seen = [], set()
    for no, cols in entries(path):
        if len(cols) != 3:
            errors.append(f"line {no}: expected 3 tab-separated columns, got {len(cols)}")
            continue
        try:
            ctx, src, tr = (unescape(c) for c in cols)
        except ValueError as e:
            errors.append(f"line {no}: {e}")
            continue
        if not src or not tr:
            errors.append(f"line {no}: empty text")
            continue
        if ctx == "@plural":
            english = src.split("|")
            if len(english) != 2 or not all(english) or placeholders(english[0]) != placeholders(english[1]):
                errors.append(f"line {no}: the English plural must be 'one|other' with the same placeholders")
            translated = tr.split("|")
            if len(translated) != forms or not all(translated):
                errors.append(f"line {no}: expected {forms} plural forms separated by |")
            elif any(placeholders(t) != placeholders(english[-1]) for t in translated):
                errors.append(f"line {no}: plural forms must keep the English placeholders")
        elif ctx.startswith("@") and ctx != "@id":
            errors.append(f"line {no}: unknown reserved context {ctx}")
        elif ctx != "@id":
            if placeholders(src) != placeholders(tr):
                errors.append(f"line {no}: placeholders differ: {placeholders(src)} vs {placeholders(tr)}")
            if src.endswith("…") != tr.endswith("…"):
                errors.append(f"line {no}: the translation must end with … exactly when the English does")
        if (ctx, src) in seen:
            errors.append(f"line {no}: duplicate entry {src!r}")
        seen.add((ctx, src))
    return errors


def keys(path):
    return {(cols[0], cols[1]) for _, cols in entries(path) if len(cols) >= 2}


def literals(macro_call):
    """String literals passed to `macro_call` in the UI source outside test modules (branna.rs `literals`)."""
    found = set()
    for d, dirs, files in os.walk(os.path.join(ROOT, "crates", "ui-egui", "src")):
        dirs[:] = [x for x in dirs if x != "i18n"]
        for name in files:
            if not name.endswith(".rs"):
                continue
            with open(os.path.join(d, name), encoding="utf-8") as f:
                rest = f.read().replace("\r\n", "\n").split("#[cfg(test)]\nmod ")[0]
            while macro_call in rest:
                after = rest.split(macro_call, 1)[1].lstrip()
                if not after.startswith('"'):
                    rest = after
                    continue
                after = after[1:]
                escaped, end = False, None
                for i, c in enumerate(after):
                    if c == '"' and not escaped:
                        end = i
                        break
                    escaped = c == "\\" and not escaped
                if end is None:
                    break
                raw, tail = after[:end], after[end + 1:]
                closing = tail.lstrip()
                if closing.removeprefix(",").lstrip().startswith(")"):
                    found.add(json.loads('"' + raw + '"'))
                rest = tail
    return found


def main():
    amharic_path = os.path.join(I18N, "am.tsv")
    problems = [f"am.tsv {e}" for e in validate(amharic_path, AMHARIC_PLURAL_FORMS)]
    amharic = keys(amharic_path)
    for ctx, src in sorted(keys(os.path.join(I18N, "it.tsv")) - amharic):
        problems.append(f"untranslated (Italian has it): context {ctx!r}, English {src!r}")
    english = {unescape(src) for ctx, src in amharic if ctx == ""}
    for label in sorted((literals("tl!(") | literals("bt!(") | {"Branna"}) - english):
        problems.append(f"untranslated UI literal: {label!r}")
    for p in problems:
        print("  ✗", p)
    print(f"am.tsv: {len(amharic)} entries, {len(problems)} problem(s)")
    sys.exit(1 if problems else 0)


main()
