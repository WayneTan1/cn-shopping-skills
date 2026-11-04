# -*- coding: utf-8 -*-
"""Candidate scoring focused on value, risk, and recommendation reasons."""

from __future__ import annotations

from .models import CandidateScore, ProductCandidate
from .ranking import (
    clamp,
    completeness_score,
    normalize_platform,
    price_score,
    review_score,
    trust_score,
)


RISK_FLAG_DEDUCTIONS = {
    "suspicious_price": 0.28,
    "spec_mismatch": 0.24,
    "weak_warranty": 0.10,
    "poor_reviews": 0.18,
    "missing_photos": 0.12,
    "off_platform": 0.30,
    "unknown_condition": 0.16,
    "no_inspection": 0.14,
}


def score_candidates(candidates: list[ProductCandidate]) -> list[CandidateScore]:
    """Score candidates by value, risk, and a blended recommendation score."""

    candidate_dicts = [candidate_to_scoring_dict(candidate) for candidate in candidates]
    scores = [
        score_candidate(candidates, candidate, candidate_dicts)
        for candidate in candidates
    ]
    scores.sort(key=lambda item: item.total_score, reverse=True)
    return scores


def score_candidate(
    all_candidates: list[ProductCandidate],
    candidate: ProductCandidate,
    candidate_dicts: list[dict] | None = None,
) -> CandidateScore:
    """Score a single candidate against the current candidate set."""

    candidate_dicts = candidate_dicts or [candidate_to_scoring_dict(item) for item in all_candidates]
    item = candidate_to_scoring_dict(candidate)

    value_score = clamp(
        price_score(candidate_dicts, item) * 0.45
        + review_score(item) * 0.20
        + completeness_score(item) * 0.15
        + trust_score(item) * 0.20
    )

    risk_score = compute_risk_score(candidate)
    total_score = clamp(value_score * 0.65 + risk_score * 0.35)

    breakdown = {
        "value_score": round(value_score, 4),
        "risk_score": round(risk_score, 4),
        "price_component": round(price_score(candidate_dicts, item), 4),
        "review_component": round(review_score(item), 4),
        "trust_component": round(trust_score(item), 4),
        "completeness_component": round(completeness_score(item), 4),
    }

    return CandidateScore(
        platform=candidate.platform,
        title=candidate.title,
        url=candidate.url,
        value_score=round(value_score, 4),
        risk_score=round(risk_score, 4),
        total_score=round(total_score, 4),
        recommendation_reason=build_recommendation_reason(candidate, breakdown),
        score_breakdown=breakdown,
    )


def compute_risk_score(candidate: ProductCandidate) -> float:
    """Compute a normalized risk score where higher means safer."""

    score = 1.0
    for risk_flag in candidate.risk_flags:
        score -= RISK_FLAG_DEDUCTIONS.get(risk_flag, 0.08)

    platform = normalize_platform(candidate.platform)
    if platform in {"xianyu", "zhuanzhuan"}:
        if not candidate.condition:
            score -= 0.10
        elif "used" in candidate.condition.lower() or "二手" in candidate.condition:
            score -= 0.04

    seller_reputation = candidate.seller.reputation_score
    if seller_reputation is not None:
        if seller_reputation >= 0.9:
            score += 0.04
        elif seller_reputation < 0.5:
            score -= 0.08

    return clamp(score)


def build_recommendation_reason(candidate: ProductCandidate, breakdown: dict[str, float]) -> str:
    """Generate a concise recommendation reason for the candidate."""

    reasons: list[str] = []
    if breakdown["price_component"] >= 0.8:
        reasons.append("价格竞争力强")
    if breakdown["review_component"] >= 0.75:
        reasons.append("评价信号较好")
    if breakdown["trust_component"] >= 0.85:
        reasons.append("平台或卖家可信度高")
    if candidate.risk_flags:
        reasons.append(f"需关注风险: {', '.join(candidate.risk_flags[:2])}")
    if not reasons:
        reasons.append("综合表现均衡")
    return "；".join(reasons)


def candidate_to_scoring_dict(candidate: ProductCandidate) -> dict:
    """Convert ProductCandidate into the dict structure expected by legacy scoring helpers."""

    return {
        "platform": candidate.platform,
        "title": candidate.title,
        "price": candidate.price,
        "landed_price": candidate.landed_price,
        "condition": candidate.condition,
        "seller_type": candidate.seller.seller_type or "",
        "rating": candidate.rating,
        "review_count": candidate.review_count,
        "warranty": candidate.raw.get("warranty"),
        "return_policy": candidate.raw.get("return_policy"),
        "advantages": candidate.raw.get("advantages", []),
        "red_flags": candidate.raw.get("red_flags", []),
        "url": candidate.url,
        "inspection": candidate.raw.get("inspection"),
        "risk_flags": candidate.risk_flags,
    }

