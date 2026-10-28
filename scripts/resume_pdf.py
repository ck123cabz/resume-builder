#!/usr/bin/env python3
"""Render a resume markdown file to a styled, ATS-parseable PDF.

markdown -> (pandoc) -> html -> (headless Chrome) -> pdf

Chrome emits real selectable text, which is what an ATS reads. Styling lives in
resume-pdf.css; --theme NAME layers resume-themes/NAME.css on top of it and names
the PDF <stem>-<NAME>.pdf. A theme may change looks only, never content or order.
"""
import argparse
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import time

from resume_md import preprocess

HERE = pathlib.Path(__file__).resolve().parent
CSS = HERE / "resume-pdf.css"
THEMES = HERE / "resume-themes"
CHROME_PATHS = ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                "google-chrome", "google-chrome-stable", "chromium", "chromium-browser"]


def find_chrome():
    """$CHROME wins; then the Mac app path; then a Chrome or Chromium on PATH."""
    for c in [os.environ.get("CHROME", "")] + CHROME_PATHS:
        if c and (pathlib.Path(c).exists() or shutil.which(c)):
            return shutil.which(c) or c
    return None

def to_html(md_text, css_text):
    frag = subprocess.run(
        ["pandoc", "-f", "markdown+raw_html", "-t", "html5"],
        input=md_text, capture_output=True, text=True, check=True, timeout=60,
    ).stdout
    return (
        "<!doctype html><html><head><meta charset='utf-8'>"
        f"<style>{css_text}</style></head><body>{frag}</body></html>"
    )


def render(md_path, outdir, theme=None):
    md_path = pathlib.Path(md_path)
    css = CSS.read_text() + ((THEMES / f"{theme}.css").read_text() if theme else "")
    pdf_path = pathlib.Path(outdir) / (md_path.stem + (f"-{theme}" if theme else "") + ".pdf")
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    # The wait loop watches this file's size, so an old copy must go first.
    pdf_path.unlink(missing_ok=True)

    html = to_html(preprocess(md_path.read_text()), css)
    with tempfile.TemporaryDirectory() as tmp:
        html_file = pathlib.Path(tmp) / "resume.html"
        html_file.write_text(html)
        # MacAppCodeSignClone off: otherwise each launch copies Chrome.app
        # (1.4 GB) to a temp folder, and the terminate() below leaves it behind.
        cmd = [find_chrome(), "--headless=new", "--disable-gpu", "--no-sandbox",
               "--disable-features=MacAppCodeSignClone",
               f"--user-data-dir={tmp}/profile", "--no-pdf-header-footer",
               "--no-first-run", "--disable-extensions",
               "--disable-background-networking", "--virtual-time-budget=4000",
               f"--print-to-pdf={pdf_path}", html_file.as_uri()]
        # Headless Chrome sometimes never exits: wait until the PDF size settles.
        proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)
        last, stable, waited = -1, 0, 0.0
        while waited < 60 and proc.poll() is None:
            time.sleep(0.25)
            waited += 0.25
            size = pdf_path.stat().st_size if pdf_path.exists() else 0
            stable = stable + 1 if size and size == last else 0
            last = size
            if stable >= 4:  # 1s unchanged
                break
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()
    if not pdf_path.exists() or pdf_path.stat().st_size == 0:
        raise RuntimeError(f"Chrome produced no PDF for {md_path}")
    return pdf_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--outdir", help="default: a pdf/ folder next to each resume")
    ap.add_argument("--theme", choices=sorted(t.stem for t in THEMES.glob("*.css")))
    args = ap.parse_args()

    if not shutil.which("pandoc"):
        sys.exit("pandoc not found (brew install pandoc)")
    if not find_chrome():
        sys.exit("Chrome or Chromium not found; set CHROME=/path/to/chrome")

    for f in args.files:
        pdf = render(f, args.outdir or pathlib.Path(f).parent / "pdf", args.theme)
        kb = pdf.stat().st_size / 1024
        print(f"{pdf}  ({kb:.0f} KB)")


if __name__ == "__main__":
    main()
