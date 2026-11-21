#!/usr/bin/env python3
"""Build the GitHub Pages version of the game into site/ (or the folder given).

The page, map scripts and fonts are copied from rpg/web/; the Python package is zipped into
rpg.zip, which the browser unpacks and runs with Pyodide (static/py-worker.js). Saves go to the
browser's IndexedDB. Try it locally with:  python3 tools/build_static.py && python3 -m http.server -d site
"""
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WEB, STATIC = ROOT / "rpg" / "web", ROOT / "static"


def build(out):
    out = Path(out)
    if out.exists():
        shutil.rmtree(out)
    shutil.copytree(WEB, out, ignore=shutil.ignore_patterns("*.py", "__pycache__"))
    for f in ("py-worker.js", "bridge.js"):
        shutil.copy(STATIC / f, out / f)
    page = (out / "index.html").read_text()
    hook = '<script src="atlas.js"></script>'
    assert hook in page, "index.html no longer loads atlas.js where the bridge expects"
    (out / "index.html").write_text(page.replace(hook, '<script src="bridge.js"></script>\n' + hook, 1))
    with zipfile.ZipFile(out / "rpg.zip", "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted((ROOT / "rpg").rglob("*")):
            rel = f.relative_to(ROOT)
            if f.is_file() and "__pycache__" not in rel.parts and "web" not in rel.parts[1:2]:
                z.write(f, rel.as_posix())
    (out / ".nojekyll").write_text("")
    return out


if __name__ == "__main__":
    out = build(sys.argv[1] if len(sys.argv) > 1 else ROOT / "site")
    print(f"built {out}  ({sum(f.stat().st_size for f in out.rglob('*') if f.is_file()) // 1024} KB)")
