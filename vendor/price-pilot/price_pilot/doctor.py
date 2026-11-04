# -*- coding: utf-8 -*-
"""Doctor output for package and channel readiness."""

from __future__ import annotations

from .config import Config
from .channels import get_all_channels
from .core import validate_skill
from .integrations.mcporter import list_mcporter_servers, locate_mcporter_config


def run_doctor(probe: bool = False, timeout: int = 12) -> list[tuple[str, str, str]]:
    status: list[tuple[str, str, str]] = []
    config = Config()
    ok, missing = validate_skill()
    if ok:
        status.append(("ok", "skill", "Bundled skill files are present"))
    else:
        status.append(("error", "skill", f"Missing skill files: {', '.join(missing)}"))
    mcporter_path = locate_mcporter_config()
    if mcporter_path:
        servers = list_mcporter_servers(mcporter_path)
        summary = ", ".join(servers) if servers else "no servers configured"
        status.append(("ok", "mcporter", f"{mcporter_path} ({summary})"))
    else:
        status.append(("warn", "mcporter", "mcporter config not found"))
    for channel in get_all_channels():
        channel_status, message = channel.check(config, probe=probe, timeout=timeout)
        status.append((channel_status, channel.name, message))
    return status


def format_doctor_report(probe: bool = False, timeout: int = 12) -> str:
    lines = ["Price Pilot doctor", ""]
    for status, name, message in run_doctor(probe=probe, timeout=timeout):
        badge = {
            "ok": "[ok]",
            "warn": "[warn]",
            "off": "[off]",
            "error": "[error]",
        }.get(status, "[info]")
        lines.append(f"{badge} {name}: {message}")
    return "\n".join(lines)
