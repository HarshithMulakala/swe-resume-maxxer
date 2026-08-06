"""Print a resume PDF exactly as the hiring-agent scorer sees it after extraction.

Usage: python extract_view.py <resume.pdf> [out.md]

Uses the vendored copy of the scorer's own pymupdf_rag module.
Requires: pip install pymupdf==1.26.3 pymupdf4llm==0.0.27
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pymupdf_rag  # vendored

def main() -> None:
    pdf = sys.argv[1]
    md = pymupdf_rag.to_markdown(pdf)
    if len(sys.argv) > 2:
        Path(sys.argv[2]).write_text(md, encoding="utf-8")
        print(f"wrote {sys.argv[2]} ({len(md)} chars)")
    else:
        print(md)

if __name__ == "__main__":
    main()
