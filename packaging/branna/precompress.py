"""Make the web app download compressed from any static host (Branna's GitHub Pages site).

Usage: python3 packaging/branna/precompress.py SITE_DIR

GitHub Pages can't be told to compress the 35 MB WebAssembly file, so this writes a gzip copy beside
it (about 13 MB) and changes trunk's loader in index.html to fetch that copy and unpack it in the
browser (DecompressionStream). Browsers without DecompressionStream, or a failed download, fall
back to the uncompressed file. trunk's preload of the uncompressed file is removed, so nothing
downloads it twice.
"""
import gzip
import pathlib
import re
import sys

site = pathlib.Path(sys.argv[1])
index = site / "index.html"
html = index.read_text(encoding="utf-8")
wasm_files = sorted(site.glob("*_bg.wasm"))
if len(wasm_files) != 1:
    sys.exit(f"expected one *_bg.wasm in {site}, found {[p.name for p in wasm_files]}")
wasm = wasm_files[0]
gz = wasm.with_name(wasm.name + ".gz")
gz.write_bytes(gzip.compress(wasm.read_bytes(), compresslevel=9, mtime=0))

init_call = re.compile(r"init\(\{\s*module_or_path:\s*'\./" + re.escape(wasm.name) + r"'\s*\}\)")
if len(init_call.findall(html)) != 1:
    sys.exit("trunk's init({ module_or_path: ... }) call not found exactly once in index.html")
loader = (
    "init({ module_or_path: (async () => {\n"
    "  // Branna: fetch the gzip copy and unpack it here (packaging/branna/precompress.py).\n"
    "  if (typeof DecompressionStream === 'function') {\n"
    "    try {\n"
    f"      const r = await fetch('./{gz.name}');\n"
    "      if (r.ok) {\n"
    "        const body = r.headers.get('content-encoding') ? r.body : r.body.pipeThrough(new DecompressionStream('gzip'));\n"
    "        return new Response(body, { headers: { 'Content-Type': 'application/wasm' } });\n"
    "      }\n"
    "    } catch (e) {\n"
    "      console.warn('Branna: the compressed download failed; using the full file', e);\n"
    "    }\n"
    "  }\n"
    f"  return fetch('./{wasm.name}');\n"
    "})() })"
)
html = init_call.sub(lambda _: loader, html)

preload = re.compile(r"<link[^>]*rel=\"preload\"[^>]*href=\"\./" + re.escape(wasm.name) + r"\"[^>]*>")
html, removed = preload.subn("", html)
if removed != 1:
    sys.exit(f"expected one preload link for {wasm.name}, removed {removed}")
index.write_text(html, encoding="utf-8")
print(f"wrote {gz.name} ({gz.stat().st_size} bytes, from {wasm.stat().st_size}); index.html loads it")
