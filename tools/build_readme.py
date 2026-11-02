#!/usr/bin/env python3
"""Deprecated compatibility shim.

The build moved to tools/build.py when data/prompts.yaml became the single
source of truth. This wrapper keeps old commands working.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

print("tools/build_readme.py is deprecated; running tools/build.py", file=sys.stderr)
raise SystemExit(
    subprocess.call([sys.executable, str(Path(__file__).with_name("build.py")), *sys.argv[1:]])
)
