# -*- coding: utf-8 -*-
"""Decision aggregation for candidate scores and inquiry replies."""

from __future__ import annotations

from .models import CandidateScore, DecisionReport, InquiryReply


def aggregate_decision(
    ranked_candidates: list[CandidateScore],
    quoted_replies: list[InquiryReply] | None = None,
) -> DecisionReport:
    """Merge ranked candidates and inquiry replies into a final recommendation report."""

    quoted_replies = quoted_replies or []
    best_candidate = ranked_candidates[0] if ranked_candidates else None
    reason = build_decision_reason(best_candidate, quoted_replies)
    return DecisionReport(
        best_candidate=best_candidate,
        ranked_candidates=ranked_candidates,
        top_recommendations=ranked_candidates[:3],
        quoted_replies=quoted_replies,
        decision_reason=reason,
    )


def build_decision_reason(best_candidate: CandidateScore | None, quoted_replies: list[InquiryReply]) -> str:
    """Generate the top-level decision explanation."""

    if not best_candidate:
        return "暂无足够候选，无法生成推荐。"

    if quoted_replies:
        quoted_prices = [reply.quoted_price for reply in quoted_replies if reply.quoted_price is not None]
        if quoted_prices:
            lowest_quote = min(quoted_prices)
            return (
                f"综合候选评分后优先推荐 {best_candidate.platform} 的「{best_candidate.title}」。"
                f" 当前询价回复中最低报价约为 {lowest_quote:.0f} 元，"
                f" 推荐理由：{best_candidate.recommendation_reason}。"
            )

    return (
        f"综合候选评分后优先推荐 {best_candidate.platform} 的「{best_candidate.title}」，"
        f" 推荐理由：{best_candidate.recommendation_reason}。"
    )
