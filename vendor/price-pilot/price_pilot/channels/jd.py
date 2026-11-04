# -*- coding: utf-8 -*-
"""JD — new product listings and stronger after-sales."""

from .base import Channel
from ..cookies import cookie_status
from ..integrations.mcporter import has_platform_server


class JDChannel(Channel):
    name = "jd"
    description = "京东商品搜索与比价"
    backends = ["browser cookies", "mcporter MCP", "live browsing"]
    tier = 1

    def can_handle(self, text: str) -> bool:
        text = text.lower()
        return "jd.com" in text or "京东" in text or "jingdong" in text

    def check(self, config=None, probe: bool = False, timeout: int = 12) -> tuple[str, str]:
        if has_platform_server("jd"):
            return "ok", "mcporter JD server is configured"
        cookie_file = config.get_cookie_file("jd") if config else None
        if cookie_file:
            status = cookie_status("jd", cookie_file, probe=probe, timeout=timeout)
            if status.get("probe", {}).get("ok"):
                return "ok", f"Cookie configured and probe passed: {cookie_file}"
            if status["ok"]:
                return "warn", f"Cookie configured at {cookie_file}; MCP server not configured yet"
            return "warn", status["message"]
        return "off", "Need JD cookie export or mcporter server before stable live access"
