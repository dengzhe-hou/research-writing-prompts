# Changelog

All notable changes to this collection are recorded here. The catalog is
versioned as a whole; individual prompts keep stable numeric IDs.

## Unreleased

### Changed

- Redesigned the static site after the [Look et al.](https://looketal.com)
  Vermilion Editorial Rail reference: warm paper and dot grid, a fixed
  contents rail, Source Serif 4 / Noto Serif SC headings, vermilion accents,
  single-column prompt cards, a scroll-progress bar, and the same search,
  filtering, copy and deep-link behavior. This replaces the interim Look et
  al. catalog skin. The site is intentionally light-only, matching the
  reference.

## v1.0.0 — 2026-11-02

First release with a single source of truth and a verifiable build.

### Added

- `data/prompts.yaml` as the only source for prompts, metadata, sources and
  highlights. `tools/build.py` renders the READMEs, catalogs and the static
  site; `tools/check.py` validates the data and the generated files.
- Static, searchable site at `docs/index.html` with category filters,
  one-click copy and stable `#p-1-1` deep links.
- `LICENSE` (CC BY 4.0) for the catalog and original prompts, `LICENSE-CODE`
  (MIT) for scripts, and `THIRD_PARTY_NOTICES.md` for upstream terms.
- `examples/` with three before/after examples (1.1, 2.1, 5.1).
- `eval/` with a fixed-case protocol, a four-dimension rubric and an
  OpenAI-compatible runner. No multi-model baseline is claimed yet.
- CI that rebuilds the site/docs and fails on stale generated files.
- Issue templates for bug reports and prompt requests.

### Changed

- Promoted the structured candidate to primary for 4.1–4.7; the original
  one-line prompts are now the quick alternatives.
- 3.1/3.2 now use a 10–20% range (or a user-supplied target) instead of a fixed
  5–15 word window.
- 2.x and 3.x support `MODE: diff` for a unified diff instead of a full rewrite.
- 5.5 now returns a layout spec plus an image-model prompt instead of asking a
  text model to draw the figure.
- 6.1 uses the target venue's review form when available, otherwise
  novelty/rigor/clarity/impact.
- README now starts with a 30-second selection table, three common paths and a
  per-category index; every prompt has a stable anchor.

### Fixed

- Removed the duplicated hard-coded prompt list and summaries from
  `tools/build_readme.py`; generated files can no longer drift silently.
- Fixed stale counts in badges and generated sections.

## 2026-10-28

- Added 4.8 Paper Title, 4.9 Related Work and 6.3 Cover Letter (25 scenarios,
  46 candidates).
- Made prompt roles field-neutral and added target-venue placeholders.
- Added anti-fabrication rules to 4.3, 4.4 and 6.2.

## 2026-10-03

- Trimmed the catalog to 22 scenarios / 41 candidates and moved the word list to
  an optional reference.

## 2026-09

- Initial public release: curated prompts from Leey21, ahmetbersoz,
  alfonso0512 and Imbad0202, with per-entry attribution.
