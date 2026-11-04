# -*- coding: utf-8 -*-
"""Source routing helpers for deterministic marketplace access plans."""

from __future__ import annotations

from typing import Any

from .config import Config
from .discovery import get_platform_discovery_capability
from .integrations.mcporter import locate_mcporter_config, resolve_platform_server


SOURCE_PLAYBOOK: dict[str, dict[str, Any]] = {
    "jd": {
        "preferred_sources": ["public_search", "cookie_session", "mcporter", "direct_link", "manual_evidence"],
        "deterministic_level": "medium",
        "decision_role": "适合做新品价格、店铺和评论的综合决策。",
        "inquiry_mode": "优先商品页与店铺页比对，必要时再补人工询价。",
    },
    "taobao": {
        "preferred_sources": ["public_search", "cookie_session", "mcporter", "direct_link", "manual_evidence"],
        "deterministic_level": "medium",
        "decision_role": "适合做价格、店铺信誉与售后承诺的平衡判断。",
        "inquiry_mode": "优先先筛店铺，再人工确认是否需要问价。",
    },
    "pinduoduo": {
        "preferred_sources": ["direct_link", "cookie_session", "mcporter", "best_effort_search", "manual_evidence"],
        "deterministic_level": "low",
        "decision_role": "更适合作为价格下限和补贴信号来源，不适合单靠网页抓取。",
        "inquiry_mode": "优先直链和补贴页证据，必要时交给浏览器自动化。",
    },
    "xianyu": {
        "preferred_sources": ["direct_link", "cookie_session", "manual_evidence", "mcporter", "best_effort_search"],
        "deterministic_level": "low",
        "decision_role": "更适合作为二手候选池和风险识别来源，需要人工复核卖家信息。",
        "inquiry_mode": "先生成话术并人工确认，再跟踪卖家回复。",
    },
    "zhuanzhuan": {
        "preferred_sources": ["direct_link", "cookie_session", "manual_evidence", "mcporter"],
        "deterministic_level": "low",
        "decision_role": "更适合作为验机和二手保障信号来源，公开搜索不可依赖。",
        "inquiry_mode": "优先用户直链或验机页，再决定是否发起询价。",
    },
}


def _available_sources(capability: dict[str, Any], has_cookie: bool, has_mcporter: bool) -> list[str]:
    available: list[str] = ["manual_evidence", "direct_link"]
    search_mode = capability.get("search_mode")
    if search_mode == "public_search":
        available.append("public_search")
    elif search_mode == "best_effort_search":
        available.append("best_effort_search")
    if has_cookie:
        available.append("cookie_session")
    if has_mcporter:
        available.append("mcporter")
    return available


def build_platform_source_plan(platform: str, config: Config) -> dict[str, Any]:
    capability = get_platform_discovery_capability(platform)
    mcporter_path = locate_mcporter_config()
    mcporter_server = resolve_platform_server(platform, mcporter_path)
    cookie_file = config.get_cookie_file(platform)
    playbook = SOURCE_PLAYBOOK.get(platform, {})
    available = _available_sources(capability, bool(cookie_file), bool(mcporter_server))

    preferred = playbook.get("preferred_sources", ["manual_evidence", "direct_link"])
    recommended = next((source for source in preferred if source in available), "manual_evidence")
    fallback_chain = [source for source in preferred if source != recommended and source in available]

    return {
        "platform": platform,
        "recommended_source": recommended,
        "available_sources": available,
        "fallback_chain": fallback_chain,
        "deterministic_level": playbook.get("deterministic_level", "low"),
        "decision_role": playbook.get("decision_role", "用于综合价格和风险判断。"),
        "inquiry_mode": playbook.get("inquiry_mode", "先人工确认，再执行询价。"),
        "search_mode": capability["search_mode"],
        "search_url": capability["search_url"],
        "reason": capability["reason"],
        "fallback": capability["fallback"],
        "supports_direct_listing_fetch": capability["supports_direct_listing_fetch"],
        "has_cookie": bool(cookie_file),
        "cookie_file": cookie_file,
        "mcporter_server": mcporter_server,
        "mcporter_config": str(mcporter_path) if mcporter_path else None,
    }


def build_source_plan(platforms: list[str], config: Config) -> list[dict[str, Any]]:
    return [build_platform_source_plan(platform, config) for platform in platforms]
