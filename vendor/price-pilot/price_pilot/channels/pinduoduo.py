# -*- coding: utf-8 -*-
"""Pinduoduo — subsidy pricing and low-price benchmarking."""

from .base import Channel
from ..cookies import cookie_status
from ..integrations.mcporter import has_platform_server


class PinduoduoChannel(Channel):
    name = "pinduoduo"
    description = "拼多多商品搜索与比价"
    backends = ["live web search", "Pinduoduo listing pages"]
    tier = 0

    def can_handle(self, text: str) -> bool:
        text = text.lower()
        return "pinduoduo" in text or "pdd" in text or "拼多多" in text

    def check(self, config=None, probe: bool = False, timeout: int = 12) -> tuple[str, str]:
        if has_platform_server("pinduoduo"):
            return "ok", "mcporter Pinduoduo server is configured"
        cookie_file = config.get_cookie_file("pinduoduo") if config else None
        if cookie_file:
            status = cookie_status("pinduoduo", cookie_file, probe=probe, timeout=timeout)
            if status.get("probe", {}).get("ok"):
                return "ok", f"Cookie configured and probe passed: {cookie_file}"
            if status["ok"]:
                return "warn", f"Cookie configured at {cookie_file}; MCP server not configured yet"
            return "warn", status["message"]
        return "off", "Need Pinduoduo cookie export or mcporter server before stable live access"
