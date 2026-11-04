# -*- coding: utf-8 -*-
"""
Channel base class — platform availability checking.

Each channel represents a shopping platform and provides:
  - can_handle(text) → whether a prompt or URL clearly targets this platform
  - check() → whether the bundled workflow for this platform is available
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class Channel(ABC):
    """Base class for all channels."""

    name: str = ""
    description: str = ""
    backends: list[str] = []
    tier: int = 0

    @abstractmethod
    def can_handle(self, text: str) -> bool:
        """Check if this channel can handle the given text or URL."""
        ...

    def check(self, config=None, probe: bool = False, timeout: int = 12) -> tuple[str, str]:
        """Return (status, message) for doctor output."""
        backend_text = "、".join(self.backends) if self.backends else "bundled guidance"
        return "ok", backend_text
