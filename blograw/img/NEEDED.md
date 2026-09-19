# Thumbnails still needed

These posts have no dedicated `image:` in their front matter and currently
fall back to the generic `img/log.jpg` placeholder set in `../index.qmd`.
Add an image below, then reference it as `image: "../img/<filename>"` in the
post's front matter.

| Post (`posts/*.qmd`) | Suggested filename | Topic / suggested image content |
|---|---|---|
| `a-b-testing.qmd` | `ab-testing.jpeg` | Split-test visual — two variants (A/B) side by side, or a conversion-funnel/results dashboard |
| `ANN-vs-SVM.qmd` | `ann-vs-svm.jpeg` | Neural network diagram next to a max-margin/SVM decision-boundary plot |
| `arima-sarima-r.qmd` | `arima-sarima.jpeg` | Time-series plot with a fitted ARIMA/SARIMA forecast band |
| `ar-ma-time-series.qmd` | `ar-ma-time-series.jpeg` | Time-series plot with autocorrelation (ACF/PACF) panels |
| `auto-arima-explanation.qmd` | `auto-arima.jpeg` | R console/output screenshot of an `auto.arima()` model summary |
| `qdraw-new-features.qmd` | `qdraw-features.jpeg` | Screenshot of the qdraw tool showing shapes/pages/eraser UI |
| `regression-interaction.qmd` | `regression-interaction.jpeg` | Regression plot with crossing/diverging interaction lines |
| `spatio-temporal.qmd` | `spatio-temporal.jpeg` | Map or heatmap with a time-dimension element (e.g. small multiples over time) |
| `t-test-to-anova.qmd` | `t-test-anova.jpeg` | Boxplots comparing multiple groups (visual bridge from 2-group t-test to k-group ANOVA) |
| `z-score.qmd` | `z-score.jpeg` | Standard normal curve with a shaded/marked z-score point |

## Notes

- Existing images already reused elsewhere in `img/` (`rlogo.jpeg`,
  `binom.jpeg`, `gitignore.jpeg`, `linux-hung.jpeg`, `dispersion-board.jpeg`,
  `sarimax-r.png`) were matched to other posts on 2026-09-19 — don't reuse
  those again unless the topic is genuinely the same.
- `img/charts/*` (rainfall-station line/bar/pie/donut charts) are demo
  assets from the scatter-plot/chart-maker tool, not blog thumbnails — they
  depict a specific rainfall dataset, not general chart types, so they don't
  fit any post above.
- Once a post gets an image, remove its row from this table.
