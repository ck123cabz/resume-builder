#!/usr/bin/env bash
# resume_theme_check.sh <resume.md> [outdir] — render a resume in every theme and check that
# each one is ATS-safe: the extracted text matches the unthemed PDF (ignoring case and the
# "·" separator), it holds no Type 3 fonts and no images, and it reports its page count.
# Exit 1 if any theme fails. Needs poppler (pdftotext, pdffonts, pdfimages, pdfinfo).
set -euo pipefail
md="${1:?usage: resume_theme_check.sh <resume.md> [outdir]}"
out="${2:-$(dirname "$md")/pdf/designs}"
here="$(cd "$(dirname "$0")" && pwd)"
stem="$(basename "$md" .md)"

norm() { pdftotext "$1" - 2>/dev/null | tr -d '·' | tr -s '[:space:]' ' ' | tr '[:upper:]' '[:lower:]'; }

python3 "$here/resume_pdf.py" --outdir "$out" "$md" >/dev/null
base="$(norm "$out/$stem.pdf")"
fail=0
for css in "$here"/resume-themes/*.css; do
  theme="$(basename "$css" .css)"
  python3 "$here/resume_pdf.py" --theme "$theme" --outdir "$out" "$md" >/dev/null
  pdf="$out/$stem-$theme.pdf"
  pages="$(pdfinfo "$pdf" | awk '/^Pages/{print $2}')"
  type3="$(pdffonts "$pdf" | awk 'NR>2 && /Type 3/' | wc -l | tr -d ' ')"
  images="$(pdfimages -list "$pdf" | tail -n +3 | wc -l | tr -d ' ')"
  if [ "$(norm "$pdf")" = "$base" ]; then text=same; else text=DIFFERENT; fi
  status=ok
  if [ "$text" != same ] || [ "$type3" != 0 ] || [ "$images" != 0 ]; then status=FAIL; fail=1; fi
  printf "%-10s %-4s pages=%s text=%s type3=%s images=%s\n" "$theme" "$status" "$pages" "$text" "$type3" "$images"
done
exit "$fail"
