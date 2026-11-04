# -*- coding: utf-8 -*-
"""Configuration management for Price Pilot."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml


class Config:
    """Manage Price Pilot configuration in ~/.price-pilot/config.yaml."""

    CONFIG_DIR = Path.home() / ".price-pilot"
    CONFIG_FILE = CONFIG_DIR / "config.yaml"

    PLATFORM_KEYS = {
        "jd": "jd_cookie_file",
        "taobao": "taobao_cookie_file",
        "pinduoduo": "pinduoduo_cookie_file",
        "xianyu": "xianyu_cookie_file",
        "zhuanzhuan": "zhuanzhuan_cookie_file",
    }

    def __init__(self, config_path: Path | None = None):
        self.config_path = Path(config_path) if config_path else self.CONFIG_FILE
        self.config_dir = self.config_path.parent
        self.data: dict[str, Any] = {}
        self._ensure_dir()
        self.load()

    def _ensure_dir(self) -> None:
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def load(self) -> None:
        if self.config_path.exists():
            self.data = yaml.safe_load(self.config_path.read_text(encoding="utf-8")) or {}
        else:
            self.data = {}

    def save(self) -> None:
        self._ensure_dir()
        self.config_path.write_text(
            yaml.safe_dump(self.data, allow_unicode=True, sort_keys=True),
            encoding="utf-8",
        )

    def get(self, key: str, default: Any = None) -> Any:
        if key in self.data:
            return self.data[key]
        env_key = key.upper()
        return os.environ.get(env_key, default)

    def set(self, key: str, value: Any) -> None:
        self.data[key] = value
        self.save()

    def set_cookie_file(self, platform: str, path: str) -> None:
        key = self.PLATFORM_KEYS[platform]
        self.set(key, str(Path(path).expanduser()))

    def delete_cookie_file(self, platform: str) -> None:
        key = self.PLATFORM_KEYS[platform]
        self.data.pop(key, None)
        self.save()

    def get_cookie_file(self, platform: str) -> str | None:
        key = self.PLATFORM_KEYS.get(platform)
        if not key:
            return None
        value = self.get(key)
        return str(value) if value else None

    def cookie_map(self) -> dict[str, str]:
        result: dict[str, str] = {}
        for platform in self.PLATFORM_KEYS:
            value = self.get_cookie_file(platform)
            if value:
                result[platform] = value
        return result

    def to_dict(self) -> dict[str, Any]:
        masked: dict[str, Any] = {}
        for key, value in self.data.items():
            if "cookie" in key.lower():
                masked[key] = str(value)
            else:
                masked[key] = value
        return masked
