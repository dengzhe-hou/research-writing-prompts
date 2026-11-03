# Third-party notices

This repository collects and adapts prompts from several public projects. The
catalog text, the arrangement and the prompts written for this repository are
licensed under CC BY 4.0 (see `LICENSE`). Scripts under `tools/` are licensed
under MIT (see `LICENSE-CODE`). **Third-party prompts are not relicensed by
this repository.** Their copyright remains with their authors.

Each candidate in `CATALOG.md` / `CATALOG_EN.md` starts with a `来源` / `Source`
line that states whether it is verbatim, adapted (and which upstream section it
came from), or written for this catalog. The table below summarizes the
upstream projects as of 2026-11-02.

| Upstream | Entries | License status | Notes |
|---|---:|---|---|
| [Leey21/awesome-ai-research-writing](https://github.com/Leey21/awesome-ai-research-writing) | 15 | No license file found | Included with attribution. Rights remain with the author. |
| [ahmetbersoz/chatgpt-prompts-for-academic-writing](https://github.com/ahmetbersoz/chatgpt-prompts-for-academic-writing) | 11 | No license file found | Included with attribution. Rights remain with the author. |
| [alfonso0512/research-writing-skill](https://github.com/alfonso0512/research-writing-skill) | 9 | MIT | See the upstream LICENSE. |
| [Imbad0202/academic-research-skills](https://github.com/Imbad0202/academic-research-skills) | 3 | CC BY-NC 4.0 | Non-commercial use only; see the upstream license. |
| Written for this catalog | 8 | CC BY 4.0 | See `LICENSE`. |

`figures4papers` is linked from entry 5.2 as further reading. It is not
reproduced here and is not counted as a candidate. Its upstream license is
CC BY-NC 4.0.

## Site design

The catalog layout and visual tokens are adapted from
[Look et al.](https://looketal.com), a design reference for academic pages,
specifically the [Vermilion Editorial Rail](https://looketal.com/s/icml-2026-foca.html)
reference. Look et al.'s code is MIT and its `DESIGN.md` text is CC BY-NC 4.0;
only the catalog layout, colors, type choices and component patterns are
reused here. The prompts and their licensing are unaffected. The site credits
Look et al. in its footer.

## If you are an upstream author

If you own one of the unlicensed upstream collections and want an entry removed,
or want a specific license and attribution format applied, please open an issue
at <https://github.com/dengzhe-hou/research-writing-prompts/issues>. We will
remove or update the entry promptly.

## What "adapted" means

Entries marked `改编` / `adapted` were abridged or rewritten for this catalog:
roles were made field-neutral, placeholders were added, output contracts and
anti-fabrication rules were tightened, and wording was adjusted for
copy-paste use. The source line records the upstream section used. Entries
marked `原文` / `verbatim` match the upstream apart from formatting or typo
fixes.
