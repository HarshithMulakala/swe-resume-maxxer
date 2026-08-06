"""Render resume content JSON -> HTML (Jinja2) -> PDF (headless Chrome) -> extraction check.

Usage: python make_resume.py <content.json> <out.pdf> [--template <template.html.j2>]

Env (optional):
  RESUME_MAXXER_CHROME   path to Chrome/Chromium/Edge binary if not auto-found

Requires: pip install pymupdf==1.26.3 pymupdf4llm==0.0.27 jinja2
The extraction check uses the vendored copy of the scorer's own pymupdf_rag module,
so what it prints is exactly what the scorer will see.
"""
import json
import os
import shutil
import subprocess
import sys
import traceback
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

HERE = Path(__file__).resolve().parent

CHROME_CANDIDATES = [
    os.environ.get("RESUME_MAXXER_CHROME"),
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium-browser",
    "/usr/bin/chromium",
    shutil.which("google-chrome"),
    shutil.which("chromium"),
    shutil.which("chrome"),
]


def find_chrome() -> str:
    for c in CHROME_CANDIDATES:
        if c and Path(c).exists():
            return c
    sys.exit("No Chrome/Chromium found. Set RESUME_MAXXER_CHROME to your browser binary.")


def main() -> None:
    args = sys.argv[1:]
    template_path = HERE.parent / "templates" / "template.html.j2"
    if "--template" in args:
        i = args.index("--template")
        template_path = Path(args[i + 1])
        del args[i:i + 2]
    content_path, out_pdf = Path(args[0]).resolve(), Path(args[1]).resolve()
    out_pdf.parent.mkdir(parents=True, exist_ok=True)

    content = json.loads(content_path.read_text(encoding="utf-8"))
    env = Environment(loader=FileSystemLoader(template_path.parent))
    html = env.get_template(template_path.name).render(**content)
    html_path = out_pdf.with_suffix(".html")
    html_path.write_text(html, encoding="utf-8")

    subprocess.run(
        [find_chrome(), "--headless", "--disable-gpu", "--no-pdf-header-footer",
         f"--print-to-pdf={out_pdf}", html_path.as_uri()],
        check=True, capture_output=True, timeout=120,
    )

    try:
        import fitz
    except ImportError:
        print(f"rendered {out_pdf} (pip install pymupdf==1.26.3 for page/link/extraction checks)")
        return

    doc = fitz.open(out_pdf)
    print(f"pages: {len(doc)}" + ("  <-- MUST BE 1: tighten content or typography knobs" if len(doc) > 1 else ""))
    links = [l.get("uri") for page in doc for l in page.get_links() if l.get("uri")]
    print(f"links ({len(links)}):")
    for u in links:
        print("  ", u)

    try:
        sys.path.insert(0, str(HERE))
        import pymupdf_rag  # vendored from hiring-agent
        md = pymupdf_rag.to_markdown(str(out_pdf))
        md_path = out_pdf.with_suffix(".extracted.md")
        md_path.write_text(md, encoding="utf-8")
        print(f"scorer's-eye extraction -> {md_path} ({len(md)} chars). READ IT before scoring.")
    except Exception:
        print("extraction check failed (likely a pymupdf version mismatch; "
              "install pymupdf==1.26.3 pymupdf4llm==0.0.27). PDF itself rendered fine.")
        traceback.print_exc(limit=1)


if __name__ == "__main__":
    main()
