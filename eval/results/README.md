# Results

**No multi-model baseline has been published yet.** This page defines how to add
one without turning a small smoke test into a leaderboard.

## What to keep

For each model, keep the raw files produced by `eval/run.py`:

```
results/<model-slug>/
  raw.jsonl
  translate-escape.md
  polish-minimal.md
  ...
  scores.md
```

Do not edit `raw.jsonl` or the per-case Markdown. Put rubric scores in
`scores.md` and keep the scorer's name (or “LLM judge + model version”).

## Score table template

| Case | Fidelity | Constraints | Format | Calibration | Total | Pass | Notes |
|---|---:|---:|---:|---:|---:|---|---|
| translate-escape | | | | | | | |
| polish-minimal | | | | | | | |
| zh-polish-restraint | | | | | | | |
| deai-english | | | | | | | |
| shorten-params | | | | | | | |
| logic-contradiction | | | | | | | |
| litreview-nocite | | | | | | | |
| results-noinvent | | | | | | | |
| response-todo | | | | | | | |

## Reporting rules

- Report model name, version, provider, date and temperature.
- Report per-case scores, not only the mean.
- A fidelity 0 is a failure even if the other dimensions are 2.
- Do not compare runs that used different prompt versions, case sets or
  temperatures.
- Include at least one case where the model fails; a table with nine perfect
  scores and no raw outputs is not evidence.

## Status

| Date | Model | Cases | Mean | Notes |
|---|---|---:|---:|---|
| — | — | — | — | Protocol only; no run yet. |
