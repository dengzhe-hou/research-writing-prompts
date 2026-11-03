#!/usr/bin/env python3
"""Render README*, CATALOG* and the static site from data/prompts.yaml.

Usage:
    python tools/build.py          # write generated files
    python tools/build.py --check  # fail if generated files are stale
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from urllib.parse import quote

import yaml

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "prompts.yaml"
TEMPLATES = ROOT / "templates"
DOCS = ROOT / "docs"

CN_NUM = "一二三四五六七八九十"
ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]

QUICK_PICKS_ZH = [
    ("中文草稿 → 英文论文", ["1.1"], ["2.1", "2.3"]),
    ("英文润色 / 去 AI 味", ["2.1"], ["2.3"]),
    ("中文润色 / 去 AI 味", ["2.2"], ["2.4"]),
    ("缩写 / 扩写", ["3.1", "3.2"], []),
    ("只查致命逻辑", ["3.3"], []),
    ("选题 / 找研究空白", ["4.1"], []),
    ("摘要 / 结论", ["4.2"], ["4.6"]),
    ("文献综述 / 相关工作", ["4.3"], ["4.9"]),
    ("方法 / 结果与讨论", ["4.4"], ["4.5"]),
    ("实验数据 → 分析 / 选图", ["5.1"], ["5.2"]),
    ("图标题 / 表标题 / 架构图", ["5.3", "5.4"], ["5.5"]),
    ("投稿前自审", ["6.1"], []),
    ("回复审稿人 / 投稿信", ["6.2"], ["6.3"]),
    ("标题 / 未来工作", ["4.8"], ["4.7"]),
]

QUICK_PICKS_EN = [
    ("Chinese draft → English paper", ["1.1"], ["2.1", "2.3"]),
    ("English polish / de-AI", ["2.1"], ["2.3"]),
    ("Chinese polish / de-AI", ["2.2"], ["2.4"]),
    ("Shorten / expand", ["3.1", "3.2"], []),
    ("Fatal logic check only", ["3.3"], []),
    ("Topic / research gap", ["4.1"], []),
    ("Abstract / conclusion", ["4.2"], ["4.6"]),
    ("Literature review / related work", ["4.3"], ["4.9"]),
    ("Method / results and discussion", ["4.4"], ["4.5"]),
    ("Results table → analysis / figure", ["5.1"], ["5.2"]),
    ("Figure / table caption / diagram", ["5.3", "5.4"], ["5.5"]),
    ("Self-review before submission", ["6.1"], []),
    ("Response / cover letter", ["6.2"], ["6.3"]),
    ("Title / future work", ["4.8"], ["4.7"]),
]


def load_data() -> dict:
    return yaml.safe_load(DATA.read_text(encoding="utf-8"))


def scenarios(data: dict):
    for cat in data["categories"]:
        for sc in cat["scenarios"]:
            yield cat, sc


def counts(data: dict) -> dict:
    scs = list(scenarios(data))
    cands = [ca for _, sc in scs for ca in sc["candidates"]]
    per_upstream = {}
    for ca in cands:
        per_upstream[ca["upstream"]] = per_upstream.get(ca["upstream"], 0) + 1
    return {
        "scenarios": len(scs),
        "candidates": len(cands),
        "originals": per_upstream.get("original", 0),
        "per_upstream": per_upstream,
    }


def anchor(sid: str) -> str:
    return "p-" + sid.replace(".", "-")


def display_title(sc: dict, zh: bool) -> str:
    tzh, ten = sc["title_zh"], sc["title_en"]
    if zh:
        return tzh if tzh == ten else f"{tzh} ({ten})"
    return ten


def badge(label: str, value: str, color: str) -> str:
    safe = quote(str(label).replace("-", "--"), safe="")
    return f'<img alt="{label}: {value}" src="https://img.shields.io/badge/{safe}-{quote(str(value), safe="")}-{color}"/>'


def render_badges(data: dict, zh: bool) -> str:
    c = counts(data)
    items = [
        badge("场景" if zh else "scenarios", c["scenarios"], "4d6bfe"),
        badge("候选模板" if zh else "candidates", c["candidates"], "4d6bfe"),
        badge("原创" if zh else "original", c["originals"], "8250df"),
        badge("license", "CC BY 4.0", "2ea44f"),
    ]
    return "\n  ".join(f'<a href="{"CATALOG.md" if zh else "CATALOG_EN.md"}">{x}</a>' for x in items)


def link(sid: str, sc: dict, zh: bool) -> str:
    return f'[{sid} {sc["title_zh"] if zh else sc["title_en"]}](#{anchor(sid)})'


def render_quick_pick(data: dict, zh: bool) -> str:
    byid = {sc["id"]: sc for _, sc in scenarios(data)}
    rows = QUICK_PICKS_ZH if zh else QUICK_PICKS_EN
    head = "| 你现在要做什么 | 用哪条 | 备选 |\n|---|---|---|" if zh else "| What you need | Use | Alternative |\n|---|---|---|"
    out = [head]
    for task, primary, alt in rows:
        use = " / ".join(link(i, byid[i], zh) for i in primary)
        other = " / ".join(link(i, byid[i], zh) for i in alt) if alt else "—"
        out.append(f"| {task} | {use} | {other} |")
    return "\n".join(out)


def render_index(data: dict, zh: bool) -> str:
    head = "| 类别 | 场景 |\n|---|---|" if zh else "| Category | Scenarios |\n|---|---|"
    out = [head]
    for cat in data["categories"]:
        title = cat["title_zh"] if zh else cat["title_en"]
        links = " · ".join(link(sc["id"], sc, zh) for sc in cat["scenarios"])
        out.append(f"| **{title}** | {links} |")
    return "\n".join(out)


def render_nav(data: dict, zh: bool) -> str:
    head = "| 类别 | 场景 |\n|---|---|" if zh else "| Category | Scenarios |\n|---|---|"
    out = [head]
    for cat in data["categories"]:
        title = cat["title_zh"] if zh else cat["title_en"]
        links = " · ".join(link(sc["id"], sc, zh) for sc in cat["scenarios"])
        out.append(f"| [{title}](#cat-{cat['id']}) | {links} |")
    return "\n".join(out)


def render_prompts(data: dict, zh: bool) -> str:
    out = []
    for cat in data["categories"]:
        out.append(f"### {cat['title_zh'] if zh else cat['title_en']}\n")
        for sc in cat["scenarios"]:
            primary = sc["candidates"][0]
            has_alt = len(sc["candidates"]) > 1
            summary = sc["summary_zh"] if zh else sc["summary_en"]
            out += [
                f'<a id="{anchor(sc["id"])}"></a>',
                "<details>",
                f'<summary><b>{sc["id"]}</b> {summary}</summary>',
                "",
            ]
            for block in primary["blocks"]:
                out += ["```text", block, "```", ""]
            if sc["id"] == "2.3":
                out.append("[可选参考词表](CATALOG.md#p-2-3)" if zh else "[Optional word-list reference](CATALOG_EN.md#p-2-3)")
                out.append("")
            if has_alt:
                out.append(f"[替代候选 →]({'CATALOG.md' if zh else 'CATALOG_EN.md'}#{anchor(sc['id'])})")
                out.append("")
            out += ["</details>", ""]
    return "\n".join(out).rstrip() + "\n"


def render_catalog(data: dict, zh: bool) -> str:
    out = []
    for i, cat in enumerate(data["categories"]):
        numeral = CN_NUM[i] if zh else ROMAN[i]
        out += [f"# {numeral}、{cat['title_zh']}" if zh else f"# {numeral}. {cat['title_en']}", ""]
        out += [f'<a id="cat-{cat["id"]}"></a>', ""]
        for sc in cat["scenarios"]:
            out += [f"## {sc['id']} {display_title(sc, zh)}", ""]
            out += [f'<a id="{anchor(sc["id"])}"></a>', ""]
            for j, cand in enumerate(sc["candidates"]):
                label = ("首选候选" if j == 0 else "替代候选") if zh else ("Primary Candidate" if j == 0 else "Alternative Candidate")
                out += [f"### {label}", ""]
                source = cand["source_zh"] if zh else cand["source_en"]
                out += [f"> 来源：{source}" if zh else f"> Source: {source}", ""]
                for block in cand["blocks"]:
                    out += ["```text", block, "```", ""]
                highlight = cand["highlight_zh"] if zh else cand["highlight_en"]
                if highlight:
                    out += [f"💡 **亮点**：{highlight}" if zh else f"💡 **Highlights**: {highlight}", ""]
                note = cand["note_zh"] if zh else cand["note_en"]
                if note:
                    out += [note, ""]
            if len(sc["candidates"]) == 1:
                out += ["本场景只有这一条候选（没有替代写法）。" if zh else "Single candidate for this scenario (no alternative).", ""]
            out += ["---", ""]
    return "\n".join(out).rstrip() + "\n"


def render_sources_table(data: dict, zh: bool) -> str:
    c = counts(data)
    head = "| 来源 | 条数 | 上游许可 |\n|---|---|---|" if zh else "| Source | Entries | Upstream license |\n|---|---|---|"
    out = [head]
    for up in data["upstreams"]:
        n = c["per_upstream"].get(up["id"], 0)
        if not n:
            continue
        name = up["name"]
        if up["id"] == "original":
            name = "本仓库编写" if zh else "Written for this catalog"
        elif up["url"]:
            name = f"[{name}]({up['url']})"
        lic = up["license"]
        if lic == "unknown":
            lic = "仓库未声明" if zh else "not declared"
        elif up["license_url"]:
            lic = f"[{lic}]({up['license_url']})"
        out.append(f"| {name} | {n} | {lic} |")
    total_label = "合计" if zh else "Total"
    out.append(f"| **{total_label}** | **{c['candidates']}** | |")
    out.append("")
    if zh:
        out.append(f"{c['candidates']} 条候选中，{c['candidates'] - c['originals']} 条整理或改编自公开项目，{c['originals']} 条为本仓库编写。每条候选的来源行注明是原文、改编还是本仓库编写。figures4papers 仅作为 5.2 的另见资源，不计入候选。")
    else:
        out.append(f"Of the {c['candidates']} candidates, {c['candidates'] - c['originals']} are collected or adapted from public projects and {c['originals']} were written for this catalog. Each candidate's source line says whether it is verbatim, adapted or original. figures4papers is only a further-reading resource for 5.2 and is not counted as a candidate.")
    return "\n".join(out)


def render_site_data(data: dict) -> dict:
    c = counts(data)
    scs = []
    for cat, sc in scenarios(data):
        scs.append(
            {
                "id": sc["id"],
                "title_zh": sc["title_zh"],
                "title_en": sc["title_en"],
                "summary_zh": sc["summary_zh"],
                "summary_en": sc["summary_en"],
                "category": cat["id"],
                "category_zh": cat["title_zh"],
                "category_en": cat["title_en"],
                "candidates": [
                    {
                        "tier": ca["tier"],
                        "source_zh": ca["source_zh"],
                        "source_en": ca["source_en"],
                        "highlight_zh": ca["highlight_zh"],
                        "highlight_en": ca["highlight_en"],
                        "note_zh": ca["note_zh"],
                        "note_en": ca["note_en"],
                        "language": ca["language"],
                        "blocks": ca["blocks"],
                    }
                    for ca in sc["candidates"]
                ],
            }
        )
    return {
        "updated": data["updated"],
        "scenario_count": c["scenarios"],
        "candidate_count": c["candidates"],
        "categories": [
            {"id": cat["id"], "title_zh": cat["title_zh"], "title_en": cat["title_en"]}
            for cat in data["categories"]
        ],
        "scenarios": scs,
    }


def render_all(data: dict) -> dict[Path, str]:
    c = counts(data)
    tokens = {
        "{{scenario_count}}": str(c["scenarios"]),
        "{{candidate_count}}": str(c["candidates"]),
        "{{category_count}}": str(len(data["categories"])),
        "{{updated}}": data["updated"],
    }
    files: dict[Path, str] = {}

    for name, zh in (("readme_zh.md", True), ("readme_en.md", False)):
        text = (TEMPLATES / name).read_text(encoding="utf-8")
        for key, value in tokens.items():
            text = text.replace(key, value)
        text = text.replace("{{badges}}", render_badges(data, zh))
        text = text.replace("{{quick_pick}}", render_quick_pick(data, zh))
        text = text.replace("{{index}}", render_index(data, zh))
        text = text.replace("{{sources_table}}", render_sources_table(data, zh))
        text = text.replace("{{prompts}}", render_prompts(data, zh))
        files[ROOT / ("README.md" if zh else "README_EN.md")] = text

    for name, zh in (("catalog_zh.md", True), ("catalog_en.md", False)):
        text = (TEMPLATES / name).read_text(encoding="utf-8")
        for key, value in tokens.items():
            text = text.replace(key, value)
        text = text.replace("{{nav}}", render_nav(data, zh))
        text = text.replace("{{sources_table}}", render_sources_table(data, zh))
        text = text.replace("{{catalog}}", render_catalog(data, zh))
        files[ROOT / ("CATALOG.md" if zh else "CATALOG_EN.md")] = text

    site_data = render_site_data(data)
    payload = json.dumps(site_data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    site = (TEMPLATES / "site.html").read_text(encoding="utf-8")
    site = site.replace("{{data_json}}", payload)
    site = site.replace("{{scenario_count}}", str(c["scenarios"]))
    site = site.replace("{{candidate_count}}", str(c["candidates"]))
    site = site.replace("{{category_count}}", str(len(data["categories"])))
    site = site.replace("{{updated}}", data["updated"])
    files[DOCS / "index.html"] = site
    files[DOCS / "prompts.json"] = json.dumps(site_data, ensure_ascii=False, indent=2) + "\n"
    return files


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail if generated files are stale")
    args = parser.parse_args()

    data = load_data()
    files = render_all(data)
    stale = []
    for path, content in files.items():
        if args.check:
            old = path.read_text(encoding="utf-8") if path.exists() else ""
            if old != content:
                stale.append(path.relative_to(ROOT))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8", newline="\n")
            print(f"wrote {path.relative_to(ROOT)}")

    if stale:
        print("stale generated files:", ", ".join(map(str, stale)), file=sys.stderr)
        print("run: python tools/build.py", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
