#!/usr/bin/env python3
"""Validate data/prompts.yaml and the generated files.

Exit status is non-zero when a hard check fails. Warnings do not fail the build.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "prompts.yaml"

sys.path.insert(0, str(ROOT / "tools"))
import build  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--links", action="store_true", help="check external links (network)")
    args = parser.parse_args()

    errors: list[str] = []
    warnings: list[str] = []

    data = yaml.safe_load(DATA.read_text(encoding="utf-8"))
    for key in ("schema", "title_zh", "title_en", "updated", "upstreams", "categories"):
        if key not in data:
            errors.append(f"data: missing key {key!r}")
    if data.get("schema") != 1:
        errors.append("data: schema must be 1")

    upstream_ids = {u["id"] for u in data.get("upstreams", [])}
    for up in data.get("upstreams", []):
        for key in ("id", "name", "license"):
            if not up.get(key):
                errors.append(f"upstream {up.get('id', '?')}: missing {key}")

    scenario_ids: list[str] = []
    candidate_total = 0
    for cat in data["categories"]:
        if not re.fullmatch(r"[a-z0-9-]+", cat["id"]):
            errors.append(f"category id not slug-like: {cat['id']!r}")
        for sc in cat["scenarios"]:
            sid = sc["id"]
            scenario_ids.append(sid)
            if not re.fullmatch(r"\d+\.\d+", sid):
                errors.append(f"scenario id not N.N: {sid!r}")
            if sc.get("category") != cat["id"]:
                errors.append(f"{sid}: category {sc.get('category')!r} != {cat['id']!r}")
            for key in ("title_zh", "title_en", "summary_zh", "summary_en"):
                if not str(sc.get(key, "")).strip():
                    errors.append(f"{sid}: empty {key}")
            cands = sc.get("candidates", [])
            if not 1 <= len(cands) <= 2:
                errors.append(f"{sid}: expected 1-2 candidates, got {len(cands)}")
            if cands and cands[0].get("tier") != "primary":
                errors.append(f"{sid}: first candidate must be primary")
            for i, ca in enumerate(cands):
                candidate_total += 1
                tier = "primary" if i == 0 else "alternative"
                if ca.get("tier") != tier:
                    errors.append(f"{sid}: candidate {i} tier {ca.get('tier')!r} != {tier!r}")
                if ca.get("upstream") not in upstream_ids:
                    errors.append(f"{sid}: unknown upstream {ca.get('upstream')!r}")
                if not ca.get("blocks"):
                    errors.append(f"{sid}: candidate {i} has no blocks")
                for block in ca.get("blocks", []):
                    if not isinstance(block, str) or not block.strip():
                        errors.append(f"{sid}: candidate {i} has an empty block")
                if ca.get("language") not in {"zh", "en", "mixed"}:
                    errors.append(f"{sid}: bad language {ca.get('language')!r}")
                if not ca.get("highlight_zh") or not ca.get("highlight_en"):
                    warnings.append(f"{sid}: candidate {i} has no bilingual highlight")
                if "---" in str(ca.get("note_zh", "")).split("\n") or "---" in str(ca.get("note_en", "")).split("\n"):
                    errors.append(f"{sid}: note contains a separator line")

    if len(scenario_ids) != len(set(scenario_ids)):
        errors.append("duplicate scenario ids")
    if len({s for s in scenario_ids}) < 1:
        errors.append("no scenarios")

    # Generated files must match the renderer output.
    files = build.render_all(data)
    for path, expected in files.items():
        if not path.exists():
            errors.append(f"missing generated file: {path.relative_to(ROOT)}")
        elif path.read_text(encoding="utf-8") != expected:
            errors.append(f"stale generated file: {path.relative_to(ROOT)} (run python tools/build.py)")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    readme_en = (ROOT / "README_EN.md").read_text(encoding="utf-8")
    for name, text in (("README.md", readme), ("README_EN.md", readme_en)):
        ids = re.findall(r"<summary><b>(\d+\.\d+)</b>", text)
        if ids != scenario_ids:
            errors.append(f"{name}: summaries {ids} != scenarios {scenario_ids}")
        anchors = re.findall(r'<a id="(p-\d+-\d+)"></a>', text)
        if len(anchors) != len(set(anchors)) or len(anchors) != len(scenario_ids):
            errors.append(f"{name}: anchor count/uniqueness mismatch ({len(anchors)})")

    for name in ("CATALOG.md", "CATALOG_EN.md"):
        text = (ROOT / name).read_text(encoding="utf-8")
        heads = re.findall(r"^### (?:首选候选|替代候选|Primary Candidate|Alternative Candidate)$", text, flags=re.M)
        if len(heads) != candidate_total:
            errors.append(f"{name}: {len(heads)} candidate headings != {candidate_total}")
        sources = len(re.findall(r"^> (?:来源：|Source: )", text, flags=re.M))
        if sources != candidate_total:
            errors.append(f"{name}: {sources} source lines != {candidate_total}")

    site = json.loads((ROOT / "docs" / "prompts.json").read_text(encoding="utf-8"))
    if len(site.get("scenarios", [])) != len(scenario_ids):
        errors.append("docs/prompts.json scenario count mismatch")
    if site.get("candidate_count") != candidate_total:
        errors.append("docs/prompts.json candidate count mismatch")

    for required in ("LICENSE", "LICENSE-CODE", "THIRD_PARTY_NOTICES.md", "CONTRIBUTING.md", "CHANGELOG.md", "CITATION.cff"):
        if not (ROOT / required).exists():
            errors.append(f"missing {required}")
    notices = (ROOT / "THIRD_PARTY_NOTICES.md").read_text(encoding="utf-8")
    for up in data["upstreams"]:
        if up["id"] != "original" and up["name"] not in notices:
            warnings.append(f"upstream {up['id']} not named in THIRD_PARTY_NOTICES.md")

    if args.links:
        urls = set()
        for up in data["upstreams"]:
            if up.get("url"):
                urls.add(up["url"])
            if up.get("license_url", "").startswith("http"):
                urls.add(up["license_url"])
        for _, sc in build.scenarios(data):
            for ca in sc["candidates"]:
                for text in (ca["source_zh"], ca["source_en"]):
                    urls.update(re.findall(r"\((https?://[^)]+)\)", text))
                for text in (ca["note_zh"], ca["note_en"]):
                    urls.update(re.findall(r"\((https?://[^)]+)\)", text))
        for url in sorted(urls):
            req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "prompt-catalog-link-check"})
            try:
                with urllib.request.urlopen(req, timeout=15) as resp:
                    if resp.status >= 400:
                        warnings.append(f"link {url}: HTTP {resp.status}")
            except (urllib.error.URLError, TimeoutError, ValueError) as exc:
                warnings.append(f"link {url}: {exc}")

    print(f"scenarios: {len(scenario_ids)}")
    print(f"candidates: {candidate_total}")
    print(f"upstreams: {', '.join(f'{k}={v}' for k, v in build.counts(data)['per_upstream'].items())}")
    for warning in warnings:
        print(f"warning: {warning}", file=sys.stderr)
    for error in errors:
        print(f"error: {error}", file=sys.stderr)
    if errors:
        print(f"FAILED with {len(errors)} error(s)", file=sys.stderr)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
