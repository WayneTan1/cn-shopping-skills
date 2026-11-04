# -*- coding: utf-8 -*-
"""Inquiry assistant: draft messages, queue confirmations, and summarize replies."""

from __future__ import annotations

import json
import os
import re
import subprocess
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from .models import InquiryMessage, InquiryReply, ProductCandidate


DEFAULT_QUESTIONS = [
    "请问现在最低到手价是多少？",
    "是否包邮，是否支持验货或退换？",
    "商品具体成色/版本/配件是否齐全？",
]


def build_inquiry_message(candidate: ProductCandidate, custom_questions: list[str] | None = None) -> InquiryMessage:
    """Generate a reusable inquiry message draft for a candidate."""

    questions = custom_questions or DEFAULT_QUESTIONS
    seller_name = candidate.seller.seller_name or "老板"
    opening = f"{seller_name}你好，我对这件商品感兴趣。"
    product_line = f"我看到的是「{candidate.title}」"
    if candidate.condition:
        product_line += f"，标注成色/状态为 {candidate.condition}"
    text = "\n".join([opening, product_line, *questions])
    return InquiryMessage(
        platform=candidate.platform,
        candidate_url=candidate.url,
        seller_name=candidate.seller.seller_name,
        text=text,
        confirmed=False,
    )


def build_inquiry_queue(candidates: list[ProductCandidate], limit: int = 3) -> list[InquiryMessage]:
    """Build a shortlist of inquiry drafts pending manual confirmation."""

    return [build_inquiry_message(candidate) for candidate in candidates[:limit]]


def confirm_inquiry(message: InquiryMessage) -> InquiryMessage:
    """Mark an inquiry draft as manually confirmed for sending."""

    message.confirmed = True
    return message


def parse_reply(platform: str, candidate_url: str | None, seller_name: str | None, reply_text: str) -> InquiryReply:
    """Parse a seller reply into a structured reply object."""

    quoted_price = extract_price(reply_text)
    return InquiryReply(
        platform=platform,
        candidate_url=candidate_url,
        seller_name=seller_name,
        reply_text=reply_text,
        quoted_price=quoted_price,
    )


def summarize_reply(reply: InquiryReply) -> dict:
    """Convert an inquiry reply into a compact serializable summary."""

    return asdict(reply)


def extract_price(text: str) -> float | None:
    """Extract a likely RMB price from free-form seller text."""

    matches = re.findall(r"(?:(?:¥|￥|rmb|RMB)\s*)?(\d{2,6}(?:\.\d{1,2})?)", text)
    if not matches:
        return None
    try:
        return float(matches[0])
    except ValueError:
        return None


def inquiry_log_dir(base_dir: Path | None = None) -> Path:
    root = base_dir or (Path.home() / ".price-pilot" / "inquiries")
    root.mkdir(parents=True, exist_ok=True)
    return root


def send_inquiry_messages(
    messages: list[InquiryMessage],
    *,
    require_confirmed: bool = True,
    transport: str = "log",
    command_template: str | None = None,
    log_dir: Path | None = None,
) -> list[dict]:
    """Dispatch confirmed inquiry messages through a log or shell transport."""

    results: list[dict] = []
    target_dir = inquiry_log_dir(log_dir)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d")
    log_path = target_dir / f"{timestamp}.jsonl"

    for message in messages:
        if require_confirmed and not message.confirmed:
            results.append({
                "platform": message.platform,
                "candidate_url": message.candidate_url,
                "seller_name": message.seller_name,
                "ok": False,
                "transport": transport,
                "message": "Inquiry message must be confirmed before sending",
            })
            continue

        payload = asdict(message)
        payload["sent_at"] = datetime.now(timezone.utc).isoformat()
        payload["transport"] = transport

        if transport == "log":
            with log_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
            results.append({
                "platform": message.platform,
                "candidate_url": message.candidate_url,
                "seller_name": message.seller_name,
                "ok": True,
                "transport": transport,
                "log_path": str(log_path),
                "message": "Inquiry recorded to log transport",
            })
            continue

        if transport == "shell":
            if not command_template:
                results.append({
                    "platform": message.platform,
                    "candidate_url": message.candidate_url,
                    "seller_name": message.seller_name,
                    "ok": False,
                    "transport": transport,
                    "message": "Shell transport requires a command template",
                })
                continue
            env = {
                "PRICE_PILOT_PLATFORM": message.platform,
                "PRICE_PILOT_CANDIDATE_URL": message.candidate_url or "",
                "PRICE_PILOT_SELLER_NAME": message.seller_name or "",
                "PRICE_PILOT_MESSAGE": message.text,
                "PRICE_PILOT_LOG_PATH": str(log_path),
            }
            completed = subprocess.run(
                command_template,
                shell=True,
                text=True,
                capture_output=True,
                env={**os.environ, **env},
            )
            payload["shell_returncode"] = completed.returncode
            payload["shell_stdout"] = completed.stdout
            payload["shell_stderr"] = completed.stderr
            with log_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
            results.append({
                "platform": message.platform,
                "candidate_url": message.candidate_url,
                "seller_name": message.seller_name,
                "ok": completed.returncode == 0,
                "transport": transport,
                "log_path": str(log_path),
                "returncode": completed.returncode,
                "stdout": completed.stdout.strip(),
                "stderr": completed.stderr.strip(),
                "message": "Shell transport executed",
            })
            continue

        results.append({
            "platform": message.platform,
            "candidate_url": message.candidate_url,
            "seller_name": message.seller_name,
            "ok": False,
            "transport": transport,
            "message": f"Unsupported transport: {transport}",
        })

    return results
