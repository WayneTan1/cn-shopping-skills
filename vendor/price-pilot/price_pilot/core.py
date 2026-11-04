# -*- coding: utf-8 -*-
"""Core helpers for bundled skill access, installation, and validation."""

from __future__ import annotations

import os
import shutil
from pathlib import Path


def package_root() -> Path:
    return Path(__file__).resolve().parent


def skill_root() -> Path:
    return package_root() / "skill"


def required_skill_files() -> list[str]:
    return [
        "SKILL.md",
        "agents/openai.yaml",
        "references/platform-playbook.md",
        "references/ranking-rubric.md",
        "scripts/score_products.py",
    ]


def validate_skill() -> tuple[bool, list[str]]:
    root = skill_root()
    missing = [relative for relative in required_skill_files() if not (root / relative).exists()]
    return len(missing) == 0, missing


def default_skills_dir() -> Path:
    codex_home = os.environ.get("CODEX_HOME")
    if codex_home:
        return Path(codex_home) / "skills"
    return Path.home() / ".codex" / "skills"


def installed_skill_dir(target_dir: Path | None = None) -> Path:
    base = target_dir or default_skills_dir()
    return base / "cn-shopping-compare"


def install_skill(target_dir: Path | None = None, force: bool = False) -> Path:
    destination = installed_skill_dir(target_dir)
    source = skill_root()

    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        if not force:
            raise FileExistsError(f"Skill already exists at {destination}")
        shutil.rmtree(destination)

    shutil.copytree(source, destination)
    return destination


def uninstall_skill(target_dir: Path | None = None) -> Path:
    destination = installed_skill_dir(target_dir)
    if destination.exists():
        shutil.rmtree(destination)
    return destination
