#!/usr/bin/env bash
# package.sh <dest> [--scan <person-dir>]...
# Build a shareable copy of resume-builder in <dest>: the skill files, plus the AI-writing linter
# and its phrase file in <dest>/lint/ when the source repo has them, so the repo keeps one copy.
# Then scan <dest> for every term in each --scan folder's never-on-resume.txt, the person's name
# from its profile.md, and absolute home paths. Exit 1 on any match; publish only a clean build.
set -euo pipefail
dest="${1:?usage: package.sh <dest> [--scan <person-dir>]...}"; shift
scans=()
while [ $# -gt 0 ]; do
  case "$1" in
    --scan) scans+=("${2:?--scan needs a folder}"); shift 2 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done

skill="$(cd "$(dirname "$0")/.." && pwd)"
repo="$(cd "$skill/../.." && pwd)"
mkdir -p "$dest"
rsync -a --delete --exclude '__pycache__' --exclude '.DS_Store' --exclude 'lint/' \
  --exclude '.git/' "$skill/" "$dest/"

if [ -f "$repo/scripts/ai_slop_lint.py" ] && [ -f "$repo/config/ai-slop-phrases.json" ]; then
  mkdir -p "$dest/lint/scripts" "$dest/lint/config"
  cp "$repo/scripts/ai_slop_lint.py" "$dest/lint/scripts/"
  rsync -a --delete --exclude '__pycache__' "$repo/scripts/ai_slop/" "$dest/lint/scripts/ai_slop/"
  cp "$repo/config/ai-slop-phrases.json" "$dest/lint/config/"
  scrub="$repo/config/resume-builder-scrub.txt"
  if [ -f "$scrub" ]; then
    while IFS= read -r line; do
      case "$line" in "#"*|"") continue ;; esac
      from="${line%% => *}"; to="${line#* => }"
      grep -rlF -- "$from" "$dest/lint" | while IFS= read -r f; do
        FROM="$from" TO="$to" perl -pi -e 's/\Q$ENV{FROM}\E/$ENV{TO}/g' "$f"
      done
    done < "$scrub"
  fi
  echo "linter: packaged from $repo"
else
  echo "linter: not found in $repo, package ships without it"
fi

fail=0
hit() { echo "LEAK  $1: $2" >&2; fail=1; }
for dir in "${scans[@]+"${scans[@]}"}"; do
  list="$dir/never-on-resume.txt"
  [ -f "$list" ] || { echo "no $list" >&2; exit 2; }
  while IFS= read -r line; do
    term="$(printf '%s' "$line" | sed -nE 's/^\[(leak|claim)\][[:space:]]+(.+)$/\2/p')"
    [ -n "$term" ] || continue
    found="$(grep -rliF -- "$term" "$dest" || true)"
    [ -z "$found" ] || hit "'$term'" "$(echo "$found" | head -3 | tr '\n' ' ')"
  done < "$list"
  name="$(sed -nE 's/^# Profile: (.+)$/\1/p' "$dir/profile.md" 2>/dev/null | head -1)"
  if [ -n "$name" ]; then
    found="$(grep -rliF -- "$name" "$dest" || true)"
    [ -z "$found" ] || hit "name '$name'" "$(echo "$found" | head -3 | tr '\n' ' ')"
  fi
done
if [ -f "$repo/config/resume-builder-scrub.txt" ]; then
  while IFS= read -r line; do
    case "$line" in "#"*|"") continue ;; esac
    from="${line%% => *}"
    found="$(grep -rlw -- "$from" "$dest" || true)"
    [ -z "$found" ] || hit "scrub term '$from'" "$(echo "$found" | head -3 | tr '\n' ' ')"
  done < "$repo/config/resume-builder-scrub.txt"
fi
found="$(grep -rlE '/(Users|home)/[A-Za-z0-9_.-]+/' "$dest" --include='*.md' --include='*.py' --include='*.sh' --include='*.txt' || true)"
[ -z "$found" ] || hit "absolute home path" "$(echo "$found" | head -3 | tr '\n' ' ')"

[ "$fail" -eq 0 ] && echo "package: $dest clean" || { echo "package: leaks found, do not publish" >&2; exit 1; }
