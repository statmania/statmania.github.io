#!/usr/bin/env python3
"""
Discovers per-course question-bank .tex files under courses/<slug>/ so
question/build_quiz.py doesn't need a manual SOURCES edit for every new
course. Each course's display label is read from its _quarto.yml
website.title (formatted "Stat Mania · <Course Name>" by convention).

Run standalone to sanity-check what would be discovered:
    python3 discover_quiz_banks.py
"""
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None


def _label_from_quarto_yml(quarto_yml_path, fallback_slug):
    fallback = fallback_slug.replace("_", " ").replace("-", " ").title()
    if not quarto_yml_path.exists():
        return fallback
    try:
        text = quarto_yml_path.read_text(encoding="utf-8")
    except OSError:
        return fallback

    title = None
    if yaml is not None:
        try:
            data = yaml.safe_load(text)
            title = (data or {}).get("website", {}).get("title")
        except yaml.YAMLError:
            title = None
    if title is None:
        # Fallback: scan for a "title:" line under the "website:" key.
        in_website = False
        for line in text.splitlines():
            stripped = line.strip()
            if stripped == "website:":
                in_website = True
                continue
            if in_website:
                if line.startswith((" ", "\t")):
                    if stripped.startswith("title:"):
                        title = stripped.split(":", 1)[1].strip().strip('"').strip("'")
                        break
                else:
                    break

    if not title or "·" not in title:
        return fallback
    return title.split("·", 1)[1].strip()


def discover_quiz_banks(courses_dir):
    """Returns sorted [(label, path), ...] for each courses/<slug>/*_question_bank.tex found."""
    courses_dir = Path(courses_dir)
    discovered = []
    for bank_path in courses_dir.glob("*/*_question_bank.tex"):
        slug = bank_path.parent.name
        quarto_yml = bank_path.parent / "_quarto.yml"
        label = _label_from_quarto_yml(quarto_yml, slug)
        discovered.append((label, bank_path))
    discovered.sort(key=lambda pair: pair[0])
    return discovered


if __name__ == "__main__":
    for label, path in discover_quiz_banks(Path(__file__).parent):
        print("%s\t%s" % (label, path))
