#!/usr/bin/env bash
# Render blog posts, commit blog/ + blograw/, and push to GitHub Pages.
#
#   ./publish.sh posts/my-post.qmd            render one post, commit, push
#   ./publish.sh posts/a.qmd posts/b.qmd      render several posts, commit, push
#   ./publish.sh --all                        full `quarto render` (after changing site.js/CSS/config)
#   ./publish.sh                              no render: just refresh data + commit/push current changes
#
# Options:  -m "message"   commit message (default: "Blog: update <files>")
#           --no-push      render and commit, but do not push
#
# Only blog/ and blograw/ are committed; other changes in the repo are left alone.
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"      # .../blograw
repo="$(git -C "$here" rev-parse --show-toplevel)"
msg="" push=1 all=0 files=()

while [ $# -gt 0 ]; do
  case "$1" in
    -m)        msg="${2:?-m needs a message}"; shift 2 ;;
    --no-push) push=0; shift ;;
    --all)     all=1; shift ;;
    -h|--help) sed -n '2,13p' "${BASH_SOURCE[0]}"; exit 0 ;;
    -*)        echo "Unknown option: $1" >&2; exit 2 ;;
    *)         files+=("$1"); shift ;;
  esac
done

cd "$here"
command -v quarto >/dev/null || { echo "quarto not found" >&2; exit 1; }

if [ "$all" -eq 1 ]; then
  echo "==> Full render"
  quarto render
elif [ "${#files[@]}" -gt 0 ]; then
  for f in "${files[@]}"; do
    [ -f "$f" ] || { echo "No such file: $f" >&2; exit 1; }
    echo "==> Rendering $f"
    quarto render "$f"      # quarto takes one file per call
  done
else
  echo "==> Refreshing site data"
  python3 scripts/build_site_data.py
fi

cd "$repo"
git add blog blograw
if git diff --cached --quiet; then
  echo "Nothing to commit."
  exit 0
fi

if [ -z "$msg" ]; then
  if [ "$all" -eq 1 ]; then msg="Blog: full rebuild"
  elif [ "${#files[@]}" -gt 0 ]; then
    names=""
    for f in "${files[@]}"; do b="$(basename "$f")"; names="${names:+$names, }${b%.*}"; done
    msg="Blog: update $names"
  else msg="Blog: update"
  fi
fi

git commit -q -m "$msg"
echo "==> Committed: $msg"

if [ "$push" -eq 1 ]; then
  git pull --rebase --autostash -q
  git push
  echo "==> Pushed. GitHub Pages updates in a minute or two."
else
  echo "==> Not pushed (--no-push)."
fi
