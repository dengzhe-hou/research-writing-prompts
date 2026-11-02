# Rubric

Score each dimension 0–2. Use the raw output, not the model's self-report.

## 1. Fidelity (0–2)

| Score | Anchor |
|---:|---|
| 0 | Invents a number, citation, dataset, result or claim; or changes the meaning of the input. |
| 1 | Mostly faithful, but adds an unsupported qualifier (for example “significantly”) or drops a constraint. |
| 2 | Every number, citation and claim is traceable to the input; uncertainty and missing information are marked. |

**Fidelity must be 2 for a case to pass.**

## 2. Constraint adherence (0–2)

| Score | Anchor |
|---:|---|
| 0 | Ignores the requested output parts, language or format; or returns a list when a paragraph was required. |
| 1 | Follows the main request but misses a length/range constraint or one output part. |
| 2 | Follows every stated constraint, including `MODE: diff`, word ranges and output language. |

## 3. Format validity (0–2)

| Score | Anchor |
|---:|---|
| 0 | LaTeX does not compile, or escapes are broken (`%`, `_`, `&`), or placeholders are mangled. |
| 1 | Compiles but has a formatting defect (unbalanced braces, stray Markdown in a Word-bound output, wrong caption case). |
| 2 | Compiles cleanly; escapes, placeholders and code fences are intact. |

For non-LaTeX outputs, treat “format” as the requested structure (parts, table
columns, diff syntax).

## 4. Calibration (0–2)

| Score | Anchor |
|---:|---|
| 0 | Presents guesses as facts; fills every gap with invented detail. |
| 1 | Marks some gaps but still overclaims in one place. |
| 2 | Marks missing information with `[待补]` / `[待检索]` / `[to verify]`; states limitations; does not claim significance from a single run. |

## Reporting

For each case, report:

```
case: translate-escape
model: <name and version>
date: <ISO date>
temperature: 0
fidelity: 2
constraints: 2
format: 2
calibration: 2
total: 8
pass: yes
notes: <one sentence>
```

Do not average away a fidelity 0. Report it as a failure and keep the raw
output.
