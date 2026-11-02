"""Make the preview drawings and the logo from the bill PDFs in templates/.

The page shows a drawing of each blank bill (assets/*_bg.svg) with one copy of the
logo laid on top (assets/logo.png, placed where assets/logo.json says), so the
screen preview and the printout look exactly like the PDF.

Run this after changing a template PDF, then run tools/build.py.
Needs Poppler (pdftocairo, pdfimages), Pillow and pdfplumber.
"""
import json
import re
import subprocess
import tempfile
from pathlib import Path

import pdfplumber
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / "templates"
ASSETS = ROOT / "assets"
BILLS = {
    "pharmacy": ("RxPx_Hospitals_Pharmacy_Bill.pdf", "ph-"),
    "lab": ("RxPx_Hospitals_Lab_Bill.pdf", "lb-"),
}
LOGO_WIDTH_PX = 1130  # about 300 dpi at the logo's printed width
LOGO_COLOURS = 64


def blank_bill_svg(pdf: Path, prefix: str) -> str:
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "page.svg"
        subprocess.run(["pdftocairo", "-svg", str(pdf), str(out)], check=True)
        s = out.read_text(encoding="utf-8")

    # Take the logo out; the page lays a single, lighter copy of it on top.
    s = re.sub(r'<image id="source-\d+"[^>]*/>\s*', "", s)
    s = re.sub(r'<mask id="[^"]+">.*?</mask>\s*', "", s, flags=re.S)
    s = re.sub(r'<g mask="url\(#[^)]+\)">\s*<use xlink:href="#source-\d+"[^>]*/>\s*</g>\s*', "", s)
    s = re.sub(r'<filter id="[^"]+".*?</filter>\s*', "", s, flags=re.S)
    if "source-" in s or "<image" in s:
        raise SystemExit(f"{pdf.name}: could not take the logo out of the drawing")

    # Make it smaller: fewer decimals, short colours, no spaces between tags.
    s = re.sub(r"(-?\d+\.\d{4,})", lambda m: ("%.3f" % float(m.group(1))).rstrip("0").rstrip("."), s)
    s = s.replace("rgb(9.01947%, 9.803772%, 10.980225%)", "#171a1c").replace("rgb(100%, 100%, 100%)", "#fff")
    s = re.sub(
        r"rgb\(([\d.]+)%, ([\d.]+)%, ([\d.]+)%\)",
        lambda m: "#%02x%02x%02x" % tuple(round(float(v) * 2.55) for v in m.groups()),
        s,
    )

    # Give every id a per-bill prefix so the two drawings can never clash.
    s = re.sub(r'id="([^"]+)"', lambda m: f'id="{prefix}{m.group(1)}"', s)
    s = re.sub(r'(xlink:href|href)="#([^"]+)"', lambda m: f'{m.group(1)}="#{prefix}{m.group(2)}"', s)
    s = re.sub(r"url\(#([^)]+)\)", lambda m: f"url(#{prefix}{m.group(1)})", s)
    s = re.sub(r"<\?xml[^>]*\?>\s*", "", s)
    return re.sub(r">\s+<", "><", s)


def logo(pdf: Path) -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["pdfimages", "-png", str(pdf), f"{tmp}/img"], check=True)
        listing = subprocess.run(["pdfimages", "-list", str(pdf)], check=True, capture_output=True, text=True)
        kinds = [line.split()[2] for line in listing.stdout.splitlines()[2:] if line.strip()]
        files = sorted(Path(tmp).glob("img-*.png"))
        picture = Image.open(files[kinds.index("image")]).convert("RGB")
        if "smask" in kinds:
            picture.putalpha(Image.open(files[kinds.index("smask")]).convert("L"))
        else:
            picture = picture.convert("RGBA")

    height = round(picture.height * LOGO_WIDTH_PX / picture.width)
    small = picture.resize((LOGO_WIDTH_PX, height), Image.LANCZOS)
    small.quantize(colors=LOGO_COLOURS, method=Image.Quantize.FASTOCTREE).save(ASSETS / "logo.png", optimize=True)

    with pdfplumber.open(pdf) as doc:
        img = max(doc.pages[0].images, key=lambda i: (i["x1"] - i["x0"]) * (i["bottom"] - i["top"]))
    return {
        "x": round(img["x0"], 2),
        "y": round(img["top"], 2),
        "w": round(img["x1"] - img["x0"], 2),
        "h": round(img["bottom"] - img["top"], 2),
    }


def main() -> None:
    ASSETS.mkdir(exist_ok=True)
    for name, (pdf, prefix) in BILLS.items():
        svg = blank_bill_svg(TEMPLATES / pdf, prefix)
        (ASSETS / f"{name}_bg.svg").write_text(svg, encoding="utf-8")
        print(f"assets/{name}_bg.svg  {len(svg) / 1024:.0f} KB")
    box = logo(TEMPLATES / BILLS["pharmacy"][0])
    (ASSETS / "logo.json").write_text(json.dumps(box) + "\n", encoding="utf-8")
    print(f"assets/logo.png  {(ASSETS / 'logo.png').stat().st_size / 1024:.0f} KB, placed at {box}")


if __name__ == "__main__":
    main()
