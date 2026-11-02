# Contributing

Thanks for improving the collection. The most useful contributions are not
"one more prompt" but a prompt that fixes an observable failure mode, with a
source and a minimal example.

## The only source file

Edit `data/prompts.yaml`. Everything else is generated:

- `README.md`, `README_EN.md`
- `CATALOG.md`, `CATALOG_EN.md`
- `docs/index.html`, `docs/prompts.json`

Do not hand-edit those files. After editing, run:

```bash
python tools/build.py
python tools/check.py
```

`python tools/build.py --check` fails if the generated files are stale; CI runs
the same check.

## Adding or changing a prompt

1. Find the scenario in `data/prompts.yaml` (or add one under the right
   category). Keep the numeric ID stable once it has been published; it is used
   in anchors and links.
2. Put the recommended prompt under `tier: primary`. Keep at most one
   alternative unless the two solve genuinely different tasks.
3. Record the source:
   - `source_zh` / `source_en` must state whether the entry is verbatim,
     adapted, or written for this catalog.
   - For an adaptation, name the upstream section.
   - Set `upstream` to one of the IDs in `upstreams:`.
   - If the upstream has no license, say so; do not guess.
4. Add or update `highlight_zh` / `highlight_en`: one or two concrete,
   observable properties, not a ranking claim.
5. If the prompt has a new failure mode, add a case to `eval/cases.yaml`.

## Prompt quality bar

A prompt is ready to merge when it has:

- an explicit input schema (what the user pastes, and where);
- an explicit output contract (parts, language, format);
- an anti-fabrication rule when it touches numbers, citations or reviewer
  responses;
- no arbitrary constraints that cannot be checked (for example "remove exactly
  5-15 words"); use a range, a percentage, or a user-supplied target instead;
- a minimal-edit or diff path when it rewrites existing text;
- field and venue placeholders instead of assuming computer science.

## Example and evaluation contributions

- Examples go in `examples/` and must use a synthetic input. Numbers in the
  output must match the input table exactly.
- Evaluation cases go in `eval/cases.yaml`; the protocol is in
  `eval/README.md`. Do not claim a model ranking without publishing the raw
  outputs and the rubric scores.

## License and attribution

By contributing, you agree that prompts you write are licensed under CC BY 4.0
and scripts under MIT. Do not paste third-party text unless you record its
source and license status. See `THIRD_PARTY_NOTICES.md`.

## Review checklist

- [ ] `python tools/build.py --check` passes.
- [ ] `python tools/check.py` passes.
- [ ] The source line is accurate; no license is guessed.
- [ ] The summary says what the user gets, not why the prompt is "better".
- [ ] Any number or citation in an example can be traced to the input.
- [ ] No generated file was edited by hand.
