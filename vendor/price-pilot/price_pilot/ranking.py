# -*- coding: utf-8 -*-
"""Ranking utilities for normalized shopping candidates."""

from __future__ import annotations

from typing import Any


PLATFORM_TRUST = {
    "jd": 0.92,
    "jingdong": 0.92,
    "taobao": 0.78,
    "pinduoduo": 0.75,
    "pdd": 0.75,
    "xianyu": 0.56,
    "zhuanzhuan": 0.64,
}

RISK_PENALTIES = {
    "suspicious_price": 0.15,
    "spec_mismatch": 0.14,
    "weak_warranty": 0.08,
    "poor_reviews": 0.12,
    "missing_photos": 0.08,
    "off_platform": 0.20,
    "unknown_condition": 0.10,
    "no_inspection": 0.08,
}


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def normalize_platform(name: str) -> str:
    return (name or "").strip().lower()


def price_score(items: list[dict[str, Any]], item: dict[str, Any]) -> float:
    prices = [safe_float(entry.get("landed_price") or entry.get("price"), 0.0) for entry in items]
    prices = [price for price in prices if price > 0]
    current = safe_float(item.get("landed_price") or item.get("price"), 0.0)
    if not prices or current <= 0:
        return 0.45
    min_price = min(prices)
    max_price = max(prices)
    if max_price == min_price:
        return 0.75
    return clamp(1 - ((current - min_price) / (max_price - min_price)))


def review_score(item: dict[str, Any]) -> float:
    rating = safe_float(item.get("rating"), 4.2)
    review_count = safe_float(item.get("review_count"), 0.0)
    rating_component = clamp((rating - 3.0) / 2.0)
    count_component = clamp(review_count / 500.0)
    return clamp(rating_component * 0.7 + count_component * 0.3)


def completeness_score(item: dict[str, Any]) -> float:
    keys = [
        "title",
        "price",
        "condition",
        "seller_type",
        "rating",
        "review_count",
        "warranty",
        "return_policy",
        "advantages",
        "red_flags",
        "url",
    ]
    present = 0
    for key in keys:
        value = item.get(key)
        if isinstance(value, list):
            present += int(bool(value))
        else:
            present += int(value not in (None, "", "unknown"))
    return present / len(keys)


def trust_score(item: dict[str, Any]) -> float:
    platform = normalize_platform(str(item.get("platform", "")))
    base = PLATFORM_TRUST.get(platform, 0.65)
    seller_type = str(item.get("seller_type", "")).lower()
    if any(token in seller_type for token in ("official", "flagship", "self-operated", "自营", "旗舰")):
        base += 0.08
    if "inspection" in str(item.get("inspection", "")).lower():
        base += 0.06
    return clamp(base)


def risk_adjustment(item: dict[str, Any]) -> float:
    penalties = 0.0
    for risk in item.get("risk_flags", []) or []:
        penalties += RISK_PENALTIES.get(str(risk), 0.05)
    if normalize_platform(str(item.get("platform", ""))) in {"xianyu", "zhuanzhuan"}:
        condition = str(item.get("condition", "")).lower()
        if not condition:
            penalties += 0.08
        elif any(token in condition for token in ("used", "二手", "95", "9成")):
            penalties += 0.03
    return clamp(1 - penalties)


def build_summary(item: dict[str, Any], components: dict[str, float]) -> str:
    reasons: list[str] = []
    if components["price"] >= 0.8:
        reasons.append("price is near the best observed level")
    if components["reviews"] >= 0.75:
        reasons.append("reviews look relatively strong")
    if components["trust"] >= 0.85:
        reasons.append("seller or platform protection is strong")
    if components["risk"] <= 0.6:
        reasons.append("risk signals need closer manual review")
    if not reasons:
        reasons.append("overall balance is acceptable but not standout")
    return "; ".join(reasons)


def score_item(items: list[dict[str, Any]], item: dict[str, Any]) -> dict[str, Any]:
    components = {
        "price": price_score(items, item),
        "reviews": review_score(item),
        "completeness": completeness_score(item),
        "trust": trust_score(item),
        "risk": risk_adjustment(item),
    }
    total = (
        components["price"] * 0.35
        + components["reviews"] * 0.25
        + components["completeness"] * 0.15
        + components["trust"] * 0.15
        + components["risk"] * 0.10
    )
    return {
        "platform": item.get("platform"),
        "title": item.get("title"),
        "price": item.get("price"),
        "landed_price": item.get("landed_price"),
        "url": item.get("url"),
        "score": round(total, 4),
        "components": {key: round(value, 4) for key, value in components.items()},
        "summary": build_summary(item, components),
    }


def rank_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ranked = [score_item(items, item) for item in items]
    ranked.sort(key=lambda entry: entry["score"], reverse=True)
    return ranked

