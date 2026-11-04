# -*- coding: utf-8 -*-
"""Channel registry — lists all supported shopping platforms."""

from __future__ import annotations

from .base import Channel
from .jd import JDChannel
from .pinduoduo import PinduoduoChannel
from .taobao import TaobaoChannel
from .xianyu import XianyuChannel
from .zhuanzhuan import ZhuanzhuanChannel


ALL_CHANNELS: list[Channel] = [
    JDChannel(),
    TaobaoChannel(),
    PinduoduoChannel(),
    XianyuChannel(),
    ZhuanzhuanChannel(),
]


def get_channel(name: str) -> Channel | None:
    for channel in ALL_CHANNELS:
        if channel.name == name:
            return channel
    return None


def get_all_channels() -> list[Channel]:
    return ALL_CHANNELS


__all__ = ["Channel", "ALL_CHANNELS", "get_channel", "get_all_channels"]

