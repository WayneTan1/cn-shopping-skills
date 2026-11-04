#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rank normalized product listings by value for money."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from price_pilot.ranking import rank_items


def parse_input(path: Path) -> list[dict]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and isinstance(payload.get("items"), list):
        return payload["items"]
    raise ValueError("Input must be a JSON array or an object with an 'items' array.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Score normalized shopping candidates.")
    parser.add_argument("--input", required=True, help="Path to a JSON array or object with an items array.")
    args = parser.parse_args()
    print(json.dumps({"ranked_items": rank_items(parse_input(Path(args.input)))}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

