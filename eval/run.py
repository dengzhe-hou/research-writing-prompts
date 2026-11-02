#!/usr/bin/env python3
"""Run the fixed evaluation cases against an OpenAI-compatible chat endpoint.

    python eval/run.py --dry-run
    OPENAI_API_KEY=... python eval/run.py --model <model> --out eval/results/<model>

The script only calls the model; it does not score the output. Score with
eval/rubric.md and keep the raw files.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "prompts.yaml"
CASES = ROOT / "eval" / "cases.yaml"


def load_prompts() -> dict[str, dict]:
    data = yaml.safe_load(DATA.read_text(encoding="utf-8"))
    out = {}
    for cat in data["categories"]:
        for sc in cat["scenarios"]:
            out[sc["id"]] = sc
    return out


def build_prompt(scenario: dict, user_input: str) -> str:
    base = "\n\n".join(scenario["candidates"][0]["blocks"]).rstrip()
    marker = "# Input"
    idx = base.rfind(marker)
    if idx != -1:
        return base[:idx] + marker + "\n" + user_input.strip() + "\n"
    return base + "\n\n# Input\n" + user_input.strip() + "\n"


def slug(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "-", text).strip("-").lower() or "model"


def call_model(base_url: str, api_key: str, model: str, prompt: str, timeout: int) -> dict:
    url = base_url.rstrip("/") + "/chat/completions"
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0,
        "max_tokens": 2000,
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def text_of(response: dict) -> str:
    try:
        return response["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        return ""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="validate cases without calling a model")
    parser.add_argument("--model", default=os.environ.get("MODEL", ""), help="model name (or MODEL env)")
    parser.add_argument("--base-url", default=os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1"))
    parser.add_argument("--api-key", default=os.environ.get("OPENAI_API_KEY", ""))
    parser.add_argument("--out", default="", help="output directory (default eval/results/<model>)")
    parser.add_argument("--case", action="append", default=[], help="run only this case id (repeatable)")
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--force", action="store_true", help="overwrite existing raw outputs")
    args = parser.parse_args()

    prompts = load_prompts()
    cases = yaml.safe_load(CASES.read_text(encoding="utf-8"))
    if args.case:
        wanted = set(args.case)
        cases = [c for c in cases if c["id"] in wanted]
        missing = wanted - {c["id"] for c in cases}
        if missing:
            print(f"unknown case(s): {', '.join(sorted(missing))}", file=sys.stderr)
            return 2

    errors = []
    for case in cases:
        if case["prompt"] not in prompts:
            errors.append(f"{case['id']}: unknown prompt id {case['prompt']!r}")
        for field in ("id", "prompt", "input", "must_keep", "must_not", "notes"):
            if not case.get(field):
                errors.append(f"{case.get('id', '?')}: empty {field}")
    if errors:
        for error in errors:
            print(f"error: {error}", file=sys.stderr)
        return 1

    if args.dry_run:
        print(f"{len(cases)} cases, {len(prompts)} prompts")
        for case in cases:
            prompt = build_prompt(prompts[case["prompt"]], case["input"])
            print(f"  {case['id']:<24} prompt {case['prompt']:<4} {len(prompt):>5} chars  keep={len(case['must_keep'])}")
        print("dry run OK; no model calls made")
        return 0

    if not args.model:
        print("error: pass --model or set MODEL", file=sys.stderr)
        return 2
    if not args.api_key:
        print("error: set OPENAI_API_KEY (or pass --api-key)", file=sys.stderr)
        return 2

    out_dir = Path(args.out) if args.out else ROOT / "eval" / "results" / slug(args.model)
    out_dir.mkdir(parents=True, exist_ok=True)
    raw_path = out_dir / "raw.jsonl"
    if raw_path.exists() and not args.force:
        print(f"error: {raw_path} exists; pass --force to append/overwrite", file=sys.stderr)
        return 2

    timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    for case in cases:
        prompt = build_prompt(prompts[case["prompt"]], case["input"])
        print(f"running {case['id']} ...", flush=True)
        try:
            response = call_model(args.base_url, args.api_key, args.model, prompt, args.timeout)
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", "replace")[:500]
            print(f"  HTTP {exc.code}: {body}", file=sys.stderr)
            return 1
        except urllib.error.URLError as exc:
            print(f"  network error: {exc}", file=sys.stderr)
            return 1

        output = text_of(response)
        record = {
            "case": case["id"],
            "prompt_id": case["prompt"],
            "model": args.model,
            "base_url": args.base_url,
            "timestamp": timestamp,
            "temperature": 0,
            "input": case["input"],
            "prompt": prompt,
            "output": output,
            "usage": response.get("usage", {}),
        }
        with raw_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")

        md = [
            f"# {case['id']}",
            "",
            f"- model: `{args.model}`",
            f"- prompt: `{case['prompt']}`",
            f"- timestamp: {timestamp}",
            "- temperature: 0",
            "",
            "## Input",
            "",
            "```text",
            case["input"].strip(),
            "```",
            "",
            "## Output",
            "",
            "```text",
            output.strip(),
            "```",
            "",
            "## Checks",
            "",
            "Must keep: " + ", ".join(f"`{x}`" for x in case["must_keep"]),
            "",
            "Must not contain: " + ", ".join(f"`{x}`" for x in case["must_not"]),
            "",
            f"Notes: {case['notes']}",
            "",
            "Score with `eval/rubric.md`; do not edit this file.",
            "",
        ]
        (out_dir / f"{case['id']}.md").write_text("\n".join(md), encoding="utf-8")

    print(f"wrote {len(cases)} outputs to {out_dir.relative_to(ROOT) if out_dir.is_relative_to(ROOT) else out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
