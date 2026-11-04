# -*- coding: utf-8 -*-
"""Zhuanzhuan — used goods with stronger inspection options."""

from .base import Channel
from ..cookies import cookie_status
from ..integrations.mcporter import has_platform_server


class ZhuanzhuanChannel(Channel):
    name = "zhuanzhuan"
    description = "转转二手商品搜索与风险评估"
    backends = ["live web search", "Zhuanzhuan listing pages"]
    tier = 0

    def can_handle(self, text: str) -> bool:
        text = text.lower()
        return "zhuanzhuan" in text or "转转" in text

    def check(self, config=None, probe: bool = False, timeout: int = 12) -> tuple[str, str]:
        if has_platform_server("zhuanzhuan"):
            return "ok", "mcporter Zhuanzhuan server is configured"
        cookie_file = config.get_cookie_file("zhuanzhuan") if config else None
        if cookie_file:
            status = cookie_status("zhuanzhuan", cookie_file, probe=probe, timeout=timeout)
            if status.get("probe", {}).get("ok"):
                return "ok", f"Cookie configured and probe passed: {cookie_file}"
            if status["ok"]:
                return "warn", f"Cookie configured at {cookie_file}; MCP server not configured yet"
            return "warn", status["message"]
        return "off", "Need Zhuanzhuan cookie export or mcporter server before stable live access"
