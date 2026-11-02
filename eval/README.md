# Evaluation protocol

This directory is for checking whether a prompt actually does what its summary
claims. It is not a leaderboard, and the repository does not publish a
multi-model ranking yet.

## What is fixed

- **Cases**: `cases.yaml` contains nine synthetic cases covering translation,
  polishing, de-AI rewriting, shortening, logic checking, literature review,
  experiment analysis and reviewer responses.
- **Prompt**: the primary candidate of the named scenario, exactly as rendered
  from `data/prompts.yaml`.
- **Model settings**: record model name/version, date, temperature and maximum
  output tokens. The runner defaults to temperature 0.
- **Rubric**: `rubric.md`, four dimensions scored 0–2.

## What to report

For every model × case, keep the raw output and score four dimensions:

| Dimension | What it checks |
|---|---|
| Fidelity | Every number, citation and claim is traceable to the input; no invented content |
| Constraint adherence | Output parts, language, length/range and `MODE:` behavior are followed |
| Format validity | LaTeX compiles, escapes are correct, code fences and placeholders are intact |
| Calibration | Missing information is marked `[待补]` / `[待检索]` / `[to verify]`; no overclaiming |

A case passes when the total is at least 6/8 **and** fidelity is 2. A model run
is not comparable if it used a different prompt version, temperature or case
set.

## Run it

```bash
# Validate the cases and print prompt sizes; no network calls.
python eval/run.py --dry-run

# Call any OpenAI-compatible endpoint.
export OPENAI_API_KEY=...
export OPENAI_BASE_URL=https://api.openai.com/v1   # optional
python eval/run.py --model gpt-4.1-mini --out eval/results/gpt-4.1-mini
```

The runner writes one Markdown file per case plus `raw.jsonl`. Do not edit the
raw outputs; score them in a separate file.

## Known limitations

- Nine cases are a smoke test, not a benchmark. They are designed to catch
  fabrication and format failures, not to estimate average quality.
- The inputs are synthetic and short; long papers and domain-specific notation
  are not covered.
- LLM-as-judge scores are biased toward fluent text. Prefer two human scorers
  for any claim about ranking, and report disagreements.
- A single run at temperature 0 is still not deterministic across providers.

## Adding a case

Add an entry to `cases.yaml` with:

- `id`: short slug;
- `prompt`: scenario ID such as `5.1`;
- `input`: synthetic text only;
- `must_keep`: strings that must survive (numbers, terms, placeholders);
- `must_not`: strings that must not appear (invented citations, new claims);
- `notes`: what failure mode the case targets.

Then run `python eval/run.py --dry-run`.
