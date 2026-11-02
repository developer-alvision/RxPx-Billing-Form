"""Build index.html: the billing page with everything it needs inside one file.

Puts the two bill PDFs (templates/), the preview drawings and logo (assets/) and
the pdf-lib library (node_modules/) into src/app.html, so the page works offline
and can be opened straight from disk or uploaded to any web host.

Run `npm install` once first. Run tools/make_assets.py before this if a template PDF changed.
"""
import base64
import re
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def b64(path: Path, width: int = 160) -> str:
    data = base64.b64encode(path.read_bytes()).decode("ascii")
    return "\n" + "\n".join(textwrap.wrap(data, width)) + "\n"


def main() -> None:
    html = (ROOT / "src" / "app.html").read_text(encoding="utf-8")
    pdflib_path = ROOT / "node_modules" / "pdf-lib" / "dist" / "pdf-lib.min.js"
    if not pdflib_path.exists():
        raise SystemExit("pdf-lib is missing: run `npm install` first.")
    pdflib = re.sub(r"\n//# sourceMappingURL=.*\s*$", "\n", pdflib_path.read_text(encoding="utf-8"))

    parts = {
        "__PDF_PHARMACY__": b64(ROOT / "templates" / "RxPx_Hospitals_Pharmacy_Bill.pdf"),
        "__PDF_LAB__": b64(ROOT / "templates" / "RxPx_Hospitals_Lab_Bill.pdf"),
        "__BG_PHARMACY__": (ROOT / "assets" / "pharmacy_bg.svg").read_text(encoding="utf-8"),
        "__BG_LAB__": (ROOT / "assets" / "lab_bg.svg").read_text(encoding="utf-8"),
        "__LOGO__": b64(ROOT / "assets" / "logo.png"),
        "__LOGO_BOX__": (ROOT / "assets" / "logo.json").read_text(encoding="utf-8").strip(),
        "__PDFLIB__": pdflib,
    }
    for key, value in parts.items():
        if html.count(key) != 1:
            raise SystemExit(f"src/app.html should contain {key} exactly once")
        if "</script" in value.lower() or "<!--" in value:
            raise SystemExit(f"{key} contains text that would break the page")
    for key, value in parts.items():
        html = html.replace(key, value)

    out = ROOT / "index.html"
    out.write_text(html, encoding="utf-8")
    print(f"index.html  {len(html.encode('utf-8')) / 1024:.0f} KB")


if __name__ == "__main__":
    main()
