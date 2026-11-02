"""One-off migration: read CATALOG*.md and README*.md, write data/prompts.yaml.

The generated YAML becomes the single source of truth. This script is kept for
auditability; after the migration you should edit data/prompts.yaml directly and
run tools/build.py.
"""
from __future__ import annotations

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent

CATEGORY_IDS = [
    "translation",
    "polishing",
    "restructuring",
    "paper-sections",
    "experiments-figures",
    "review-submission",
]

UPSTREAMS = [
    {
        "id": "leey21",
        "name": "Leey21/awesome-ai-research-writing",
        "url": "https://github.com/Leey21/awesome-ai-research-writing",
        "license": "unknown",
        "license_url": "",
    },
    {
        "id": "ahmetbersoz",
        "name": "ahmetbersoz/chatgpt-prompts-for-academic-writing",
        "url": "https://github.com/ahmetbersoz/chatgpt-prompts-for-academic-writing",
        "license": "unknown",
        "license_url": "",
    },
    {
        "id": "alfonso0512",
        "name": "alfonso0512/research-writing-skill",
        "url": "https://github.com/alfonso0512/research-writing-skill",
        "license": "MIT",
        "license_url": "https://github.com/alfonso0512/research-writing-skill/blob/main/LICENSE",
    },
    {
        "id": "imbad0202",
        "name": "Imbad0202/academic-research-skills",
        "url": "https://github.com/Imbad0202/academic-research-skills",
        "license": "CC-BY-NC-4.0",
        "license_url": "https://github.com/Imbad0202/academic-research-skills/blob/main/LICENSE",
    },
    {
        "id": "original",
        "name": "written for this catalog",
        "url": "",
        "license": "CC-BY-4.0",
        "license_url": "LICENSE",
    },
]


def parse_catalog(path: Path) -> list[dict]:
    """Parse a catalog into categories -> scenarios -> candidates, ignoring fences."""
    lines = path.read_text(encoding="utf-8").splitlines()
    categories: list[dict] = []
    cur_cat = cur_sc = cur_cand = None
    in_fence = False
    for line in lines:
        if line.startswith("```"):
            in_fence = not in_fence
            if cur_cand is not None:
                cur_cand["lines"].append(line)
            continue
        if in_fence:
            if cur_cand is not None:
                cur_cand["lines"].append(line)
            continue
        if line.startswith("# ") and not line.startswith("## "):
            cur_cat = {"heading": line[2:].strip(), "scenarios": []}
            categories.append(cur_cat)
            cur_sc = cur_cand = None
        elif line.startswith("## "):
            m = re.match(r"## (\d+\.\d+) (.+)", line)
            if m and cur_cat is not None:
                cur_sc = {"id": m.group(1), "heading": m.group(2), "candidates": []}
                cur_cat["scenarios"].append(cur_sc)
                cur_cand = None
        elif line.startswith("### "):
            if cur_sc is not None:
                cur_cand = {"kind": line[4:].strip(), "lines": []}
                cur_sc["candidates"].append(cur_cand)
        elif cur_cand is not None:
            cur_cand["lines"].append(line)

    for cat in categories:
        for sc in cat["scenarios"]:
            for cand in sc["candidates"]:
                cand["source"] = _first(cand["lines"], ("> 来源：", "> Source:"))
                cand["highlight"] = _first(cand["lines"], ("💡 **亮点**：", "💡 **Highlights**:"))
                cand["note"] = _note(cand["lines"])
                cand["blocks"] = _blocks(cand["lines"])
                del cand["lines"]
    return categories


def _first(lines: list[str], prefixes: tuple[str, ...]) -> str:
    for line in lines:
        for prefix in prefixes:
            if line.startswith(prefix):
                value = line[len(prefix) :].strip()
                return value.lstrip("：: ").strip()
    return ""


def _note(lines: list[str]) -> str:
    out = []
    seen_highlight = False
    for line in lines:
        if line.startswith("💡"):
            seen_highlight = True
            continue
        if seen_highlight and line.strip() and not line.startswith("```"):
            out.append(line.strip())
    return "\n".join(out)


def _blocks(lines: list[str]) -> list[str]:
    blocks, buf, in_fence = [], None, False
    for line in lines:
        if line.startswith("```"):
            if not in_fence:
                in_fence, buf = True, []
            else:
                in_fence = False
                blocks.append("\n".join(buf).rstrip("\n"))
                buf = None
            continue
        if in_fence and buf is not None:
            buf.append(line)
    return blocks


def parse_summaries(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    return dict(re.findall(r"<summary><b>(\d+\.\d+)</b> (.*?)</summary>", text))


def split_title(heading: str) -> tuple[str, str]:
    """'中转英 (Chinese → English)' -> ('中转英', 'Chinese → English')."""
    m = re.match(r"(.+?) \(([^()]*)\)$", heading)
    if m:
        return m.group(1).strip(), m.group(2).strip()
    return heading.strip(), heading.strip()


def upstream_id(source: str) -> str:
    if "Leey21" in source:
        return "leey21"
    if "ahmetbersoz" in source:
        return "ahmetbersoz"
    if "alfonso0512" in source:
        return "alfonso0512"
    if "Imbad0202" in source:
        return "imbad0202"
    return "original"


def language(blocks: list[str]) -> str:
    text = "\n".join(blocks)
    cjk = len(re.findall(r"[\u4e00-\u9fff]", text))
    latin = len(re.findall(r"[A-Za-z]", text))
    if cjk and latin:
        return "mixed" if cjk * 4 > latin else "en"
    return "zh" if cjk else "en"


def main() -> None:
    zh_cats = parse_catalog(ROOT / "CATALOG.md")
    en_cats = parse_catalog(ROOT / "CATALOG_EN.md")
    zh_sum = parse_summaries(ROOT / "README.md")
    en_sum = parse_summaries(ROOT / "README_EN.md")

    zh_cats = [c for c in zh_cats if c["scenarios"]]
    en_cats = [c for c in en_cats if c["scenarios"]]
    assert len(zh_cats) == len(en_cats) == 6

    data = {
        "schema": 1,
        "title_zh": "科研写作 Prompt 合集",
        "title_en": "Research Writing Prompt Collection",
        "updated": "2026-11-02",
        "upstreams": UPSTREAMS,
        "categories": [],
    }

    for idx, (zc, ec) in enumerate(zip(zh_cats, en_cats)):
        assert len(zc["scenarios"]) == len(ec["scenarios"])
        cat = {
            "id": CATEGORY_IDS[idx],
            "title_zh": re.sub(r"^[一二三四五六七八九十]+、", "", zc["heading"]).split(" (")[0],
            "title_en": re.sub(r"^[IVX]+\. ", "", ec["heading"]),
            "scenarios": [],
        }
        for zs, es in zip(zc["scenarios"], ec["scenarios"]):
            assert zs["id"] == es["id"]
            tzh, _ = split_title(zs["heading"])
            ten, _ = split_title(es["heading"])
            sc = {
                "id": zs["id"],
                "title_zh": tzh,
                "title_en": ten,
                "summary_zh": zh_sum[zs["id"]],
                "summary_en": en_sum[es["id"]],
                "category": cat["id"],
                "candidates": [],
            }
            for i, (zca, eca) in enumerate(zip(zs["candidates"], es["candidates"])):
                assert zca["blocks"] == eca["blocks"], (zs["id"], i)
                tier = "primary" if i == 0 else "alternative"
                uid = upstream_id(zca["source"])
                sc["candidates"].append(
                    {
                        "tier": tier,
                        "source_zh": zca["source"],
                        "source_en": eca["source"],
                        "upstream": uid,
                        "blocks": zca["blocks"],
                        "language": language(zca["blocks"]),
                        "highlight_zh": zca["highlight"],
                        "highlight_en": eca["highlight"],
                        "note_zh": zca["note"],
                        "note_en": eca["note"],
                    }
                )
            cat["scenarios"].append(sc)
        data["categories"].append(cat)

    out = ROOT / "data" / "prompts.yaml"
    out.parent.mkdir(exist_ok=True)
    out.write_text(dump_yaml(data), encoding="utf-8")
    print(f"wrote {out.relative_to(ROOT)}: "
          f"{sum(len(c['scenarios']) for c in data['categories'])} scenarios, "
          f"{sum(len(s['candidates']) for c in data['categories'] for s in c['scenarios'])} candidates")


class Dumper(yaml.SafeDumper):
    pass


def _str_presenter(dumper: yaml.SafeDumper, data: str):
    if "\n" in data:
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


Dumper.add_representer(str, _str_presenter)


def dump_yaml(data: dict) -> str:
    return yaml.dump(
        data,
        Dumper=Dumper,
        allow_unicode=True,
        sort_keys=False,
        width=1000,
        default_flow_style=False,
    )


if __name__ == "__main__":
    main()
