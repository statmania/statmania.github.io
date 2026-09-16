# Quiz App — Draft Plan

# Option 1

**Source:** question/bank/stat1_mcq_bank.tex and stat2_mcq_bank.tex

## File Strcuture in the source

The chapters and topics are divided into latex subsection and subsubsections. The questions are 3 types. 

### 1. Simple questions 

\question \textbf{$\sqrt{\beta_1}=-0.23$ implies--}
\choice{Left Skew}{Symmetry}{Right Skew}{Mesokurtic}{a}

### 2. Situation Set 
% Situation Set Starts
\textbf{Answer the next two questions based on the following information}

\begin{center}
The first and second moments of a distribution around 2 are 13 and 195, respectively.
\end{center}

\question \textbf{What is the arithmetic mean?}
\choice{15}{12}{11}{26}{a}

\question \textbf{What is its variance?}
\choice{20}{21}{26}{25}{c}
% Situation Set Ends

### 3. Multiple Completion

% Multiple Completion Starts
\question \textbf{In a negatively skewed distribution --}

i. there is a long tail on the left \\
ii. median is greater than mean \\
iii. high values have frquencies  

\textbf{Which one is correct?}

\choice{i and ii}{i and iii}{ii and iii}{i, ii and iii}{d}
% Multiple Completion Ends

## Output Format

question/stat-prob.html.

This feteches all the questions from the both the file in the mentioned source. 

## UX/UI

User can select chapter and topic from dropdown and then number of questions. Maintain the futuristic look in line with the site design. 

User can also choose to see the answer after each question is answered or later after all are submitted. 

## Reproducibility

Make a python script so whenever it is run, the output is generated from the sources when. 

## Improvement

1. Answering a question should proceed to the next one (without having to click Next button)

# Option 2 (Later) -- Ignore everything that follows


## Goal

A self-contained interactive quiz, built from the content in `slide/*.qmd`, letting a student pick a chapter and a question type (MCQ or short-answer) and practice with instant feedback. Lives in its own `quiz/` folder at the repo root, independent of the Jekyll and Quarto pipelines.

## Why not Quarto

Per `CLAUDE.md`, `ds/`, `games/`, and `utility/` are hand-written static HTML with inline CSS/JS and no build step — that's the right precedent here too. A quiz is an interactive app, not a document; Quarto/revealjs isn't a good fit (the existing `slide/quiz.qmd` prototype shows why — one hardcoded question, no chapter/type selection, and it's tangled into the revealjs slide pipeline). `quiz/` will follow the `games/`/`utility/` convention instead: hand-authored, self-contained, dark "futuristic" theme matching `utility/timer.html` / `games/index.html`.

## Content source

`slide/*.qmd` chapters (01 through 09, e.g. `01-stat-intro.qmd`, `03-central-tendency.qmd`, `04-binomial_dist.qmd`, ...) already contain, per chapter:
- Definitions / key terms (good for short-answer or definition-recall MCQs)
- Formulas and theorems (good for "which formula" MCQs or short derivations)
- Worked "Problem N" / "Creative Question" sections (good for short-answer numeric problems, since these already have known correct answers or are provable statements)

I will **not** auto-generate questions from prose with a script — chapter content varies too much in structure for reliable extraction, and question quality matters more than coverage. Instead:
- I go chapter by chapter, hand-authoring a modest question set (aim ~8–12 questions per chapter to start) drawing directly from each `.qmd`'s definitions, theorems, and existing Problem/Creative Question sections, adapting them into MCQ or short-answer form.
- You review/edit the generated question files before they go live — same review loop as the lesson-plan xlsx work.

## Data format

One JSON file per chapter under `quiz/data/`, e.g. `quiz/data/01-stat-intro.json`:

```json
{
  "chapter": "01-stat-intro",
  "title": "Introduction to Statistics",
  "questions": [
    {
      "id": "01-01",
      "type": "mcq",
      "question": "Which scale of measurement has no true zero?",
      "options": ["Nominal", "Ordinal", "Interval", "Ratio"],
      "answer": 2,
      "explanation": "Interval scales (e.g. temperature in Celsius) have an arbitrary zero point."
    },
    {
      "id": "01-02",
      "type": "short",
      "question": "Find the value of $\\sum_{i=1}^{10}(x_i - 4)$ given $\\sum_{i=1}^{10} x_i = 20$.",
      "answer": "-20",
      "explanation": "$\\sum(x_i-4) = \\sum x_i - 10\\times4 = 20 - 40 = -20$."
    }
  ]
}
```

- `type: "mcq"` → auto-graded (single correct option index).
- `type: "short"` → **not** auto-graded as free text (too unreliable for math answers with formatting variance). Instead: student types/thinks their answer, clicks "Reveal Answer", sees the correct answer + explanation, and self-marks (Got it / Missed it) — this also drives the score tally. This mirrors how the lesson plans already separate "Application" (practice problems) from "Confirmation" (self-check questions).
- Math renders via MathJax/KaTeX (KaTeX preferred — lighter, no external fetch needed beyond one CDN script, per the CDN allowlist).

## App structure (single HTML output)

```
quiz/
  index.html        <- the shipped, self-contained quiz app (what you open/share)
  plan.md            <- this file
  data/
    01-stat-intro.json
    02-data-collection-organization-presentation.json
    03-central-tendency.json
    ...
  build.py           <- small script: reads data/*.json, embeds it as one inline
                        JS object into index.html, so the shipped file has zero
                        runtime fetch()/CORS issues when opened directly via file://
                        (same "generate the artifact from source data" pattern as
                        resources/lesson_plan/generate_lesson_plans.py)
```

Editing workflow: edit the per-chapter JSON (easy to review/diff), run `python3 build.py`, get a refreshed self-contained `index.html`. If you'd rather skip the build step entirely and just hand-edit one big inline JS blob directly in `index.html` (simpler, but worse for reviewing diffs as the bank grows), say so and I'll drop `data/`+`build.py` and keep everything in the one file.

## UI / UX

- Landing view: chapter picker (grid of chapter cards, dark theme, matches `games/index.html` cards) + question-type toggle (MCQ / Short-answer / Mixed) + question-count picker.
- Quiz view: one question at a time, progress bar, instant feedback (green/red for MCQ; reveal-and-self-mark for short-answer), running score.
- Summary view at the end: score, list of missed questions with explanations, "Retry missed only" button.
- Everything client-side, no backend, no `localStorage` persistence needed initially (can add "remember last chapter" as a small nice-to-have via `localStorage`, matching the browser-storage guidance for artifacts/static pages).

## Open questions for you

1. Chapter scope: start with just the `slide/0X-*.qmd` numbered chapters (01–09 + normal distribution), or include the non-numbered ones too (`probability.qmd`, `permutation-combination.qmd`, `dispersion.qmd`, etc.)?
2. Question volume: ~8–12 per chapter as a first pass, or a specific target?
3. Build step: keep the `data/*.json` + `build.py` split (better for review/diffs), or single hand-edited `index.html` (simpler, no build step)?
4. Should short-answer questions ever be auto-graded (e.g. exact-match on simple numeric answers like "0.375"), with self-mark reserved only for symbolic/derivation answers? Or keep self-mark uniform for all short-answer questions for simplicity?

Once you confirm these, I'll build out chapter 01 as a first sample for you to review before doing the rest.
