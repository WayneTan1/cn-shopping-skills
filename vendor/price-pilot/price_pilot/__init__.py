# -*- coding: utf-8 -*-

from .decision import aggregate_decision
from .discovery import normalize_candidate, normalize_candidates
from .inquiry import build_inquiry_message, build_inquiry_queue, parse_reply
from .models import (
    CandidateScore,
    DecisionReport,
    InquiryMessage,
    InquiryReply,
    ProductCandidate,
    SellerProfile,
)
from .scoring import score_candidate, score_candidates
from .sources import build_source_plan, build_platform_source_plan

__version__ = "0.3.0"

__all__ = [
    "__version__",
    "SellerProfile",
    "ProductCandidate",
    "InquiryMessage",
    "InquiryReply",
    "CandidateScore",
    "DecisionReport",
    "normalize_candidate",
    "normalize_candidates",
    "score_candidate",
    "score_candidates",
    "build_inquiry_message",
    "build_inquiry_queue",
    "parse_reply",
    "aggregate_decision",
    "build_source_plan",
    "build_platform_source_plan",
]
