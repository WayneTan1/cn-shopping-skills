# -*- coding: utf-8 -*-
"""Taobao — broad catalog and seller comparison."""

from .base import Channel
from ..cookies import cookie_status
from ..integrations.mcporter import has_platform_server


class TaobaoChannel(Channel):
    name = "taobao"
    description = "淘宝商品搜索与比价"
    backends = ["live web search", "Taobao listing pages"]
    tier = 0

    def can_handle(self, text: str) -> bool:
        text = text.lower()
        return "taobao.com" in text or "淘宝" in text

    def check(self, config=None, probe: bool = False, timeout: int = 12) -> tuple[str, str]:
        if has_platform_server("taobao"):
            return "ok", "mcporter Taobao server is configured"
        cookie_file = config.get_cookie_file("taobao") if config else None
        if cookie_file:
            status = cookie_status("taobao", cookie_file, probe=probe, timeout=timeout)
            if status.get("probe", {}).get("ok"):
                return "ok", f"Cookie configured and probe passed: {cookie_file}"
            if status["ok"]:
                return "warn", f"Cookie configured at {cookie_file}; MCP server not configured yet"
            return "warn", status["message"]
        return "off", "Need Taobao cookie export or mcporter server before stable live access"
