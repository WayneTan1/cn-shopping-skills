# -*- coding: utf-8 -*-
"""Xianyu — peer-to-peer used goods with higher fraud risk."""

from .base import Channel
from ..cookies import cookie_status
from ..integrations.mcporter import has_platform_server


class XianyuChannel(Channel):
    name = "xianyu"
    description = "闲鱼二手商品搜索与风险评估"
    backends = ["live web search", "Xianyu listing pages"]
    tier = 0

    def can_handle(self, text: str) -> bool:
        text = text.lower()
        return "xianyu" in text or "2.taobao.com" in text or "闲鱼" in text

    def check(self, config=None, probe: bool = False, timeout: int = 12) -> tuple[str, str]:
        if has_platform_server("xianyu"):
            return "ok", "mcporter Xianyu server is configured"
        cookie_file = config.get_cookie_file("xianyu") if config else None
        if cookie_file:
            status = cookie_status("xianyu", cookie_file, probe=probe, timeout=timeout)
            if status.get("probe", {}).get("ok"):
                return "ok", f"Cookie configured and probe passed: {cookie_file}"
            if status["ok"]:
                return "warn", f"Cookie configured at {cookie_file}; MCP server not configured yet"
            return "warn", status["message"]
        return "off", "Need Xianyu cookie export or mcporter server before stable live access"
