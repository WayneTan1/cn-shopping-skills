# -*- coding: utf-8 -*-
"""Core domain models for discovery, inquiry, scoring, and decision making."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class SellerProfile:
    """Normalized seller metadata across platforms."""

    seller_id: str | None = None
    seller_name: str | None = None
    seller_type: str | None = None
    reputation_score: float | None = None
    reputation_label: str | None = None
    location: str | None = None


@dataclass
class ProductCandidate:
    """Normalized product candidate produced by the discovery stage."""

    platform: str
    title: str
    url: str | None = None
    price: float | None = None
    landed_price: float | None = None
    condition: str | None = None
    region: str | None = None
    published_at: str | None = None
    seller: SellerProfile = field(default_factory=SellerProfile)
    review_count: int | None = None
    rating: float | None = None
    risk_flags: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    raw: dict = field(default_factory=dict)


@dataclass
class InquiryMessage:
    """A message draft or outgoing inquiry targeted at a seller."""

    platform: str
    candidate_url: str | None
    seller_name: str | None
    text: str
    confirmed: bool = False


@dataclass
class InquiryReply:
    """A seller reply captured after an inquiry is sent."""

    platform: str
    candidate_url: str | None
    seller_name: str | None
    reply_text: str
    quoted_price: float | None = None
    quote_currency: str = "CNY"
    quote_type: str = "seller_reply"
    replied_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    extra_terms: dict = field(default_factory=dict)


@dataclass
class CandidateScore:
    """Scoring result for a discovered candidate."""

    platform: str
    title: str
    url: str | None
    value_score: float
    risk_score: float
    total_score: float
    recommendation_reason: str
    score_breakdown: dict[str, float] = field(default_factory=dict)


@dataclass
class DecisionReport:
    """Final decision output combining candidates and inquiries."""

    best_candidate: CandidateScore | None
    ranked_candidates: list[CandidateScore]
    top_recommendations: list[CandidateScore]
    quoted_replies: list[InquiryReply]
    decision_reason: str
