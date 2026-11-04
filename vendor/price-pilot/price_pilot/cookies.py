# -*- coding: utf-8 -*-
"""Cookie import, validation, and status helpers."""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


PLATFORM_RULES = {
    "jd": {
        "domains": ["jd.com", "jingdong.com"],
        "required_names": ["pt_key", "pt_pin"],
        "probe_url": "https://home.jd.com/",
        "login_markers": ["passport.jd.com", "登录", "验证码", "安全验证"],
        "success_markers": ["我的京东", "退出登录", "账户设置"],
    },
    "taobao": {
        "domains": ["taobao.com", "tmall.com"],
        "required_names": ["cookie2", "_tb_token_", "unb"],
        "probe_url": "https://i.taobao.com/my_taobao.htm",
        "login_markers": ["login.taobao.com", "验证码", "请登录", "login_unusual.htm"],
        "success_markers": ["我的淘宝", "已买到的宝贝", "收货地址"],
    },
    "pinduoduo": {
        "domains": ["pinduoduo.com", "yangkeduo.com"],
        "required_names": ["api_uid", "_nano_fp"],
        "probe_url": "https://mobile.yangkeduo.com/personal.html",
        "login_markers": ["登录", "验证码", "mobile.yangkeduo.com/login"],
        "success_markers": ["个人中心", "我的订单", "收货地址"],
    },
    "xianyu": {
        "domains": ["2.taobao.com", "taobao.com", "idlefish.com"],
        "required_names": ["cookie2", "_tb_token_", "unb"],
        "probe_url": "https://www.goofish.com/",
        "login_markers": ["登录", "验证码", "login.taobao.com", "安全验证"],
        "success_markers": ["闲鱼", "我发布的", "我买到的"],
    },
    "zhuanzhuan": {
        "domains": ["zhuanzhuan.com"],
        "required_names": ["zzptt", "uid"],
        "probe_url": "https://www.zhuanzhuan.com/",
        "login_markers": ["登录", "验证码", "passport", "安全验证"],
        "success_markers": ["转转", "我的", "个人中心"],
    },
}


@dataclass
class CookieCheckResult:
    ok: bool
    platform: str
    file: Path
    cookie_count: int
    matched_domains: list[str]
    present_names: list[str]
    missing_names: list[str]
    format_name: str
    message: str


@dataclass
class CookieProbeResult:
    ok: bool
    platform: str
    file: Path
    status_code: int | None
    final_url: str | None
    mode: str
    message: str


def cookie_store_dir(config_dir: Path) -> Path:
    return config_dir / "cookies"


def import_cookie_file(platform: str, source: Path, target_dir: Path) -> Path:
    destination_dir = cookie_store_dir(target_dir)
    destination_dir.mkdir(parents=True, exist_ok=True)
    destination = destination_dir / f"{platform}.json"
    shutil.copy2(source, destination)
    return destination


def _normalize_cookie_entry(entry: dict[str, Any]) -> dict[str, str] | None:
    name = entry.get("name")
    value = entry.get("value")
    domain = entry.get("domain") or entry.get("host")
    if not name or value is None:
        return None
    return {
        "name": str(name),
        "value": str(value),
        "domain": str(domain or ""),
    }


def load_cookie_file(path: Path) -> tuple[list[dict[str, str]], str]:
    payload = json.loads(path.read_text(encoding="utf-8"))

    if isinstance(payload, list):
        cookies = [_normalize_cookie_entry(entry) for entry in payload if isinstance(entry, dict)]
        return [entry for entry in cookies if entry], "list"

    if isinstance(payload, dict):
        if isinstance(payload.get("cookies"), list):
            cookies = [_normalize_cookie_entry(entry) for entry in payload["cookies"] if isinstance(entry, dict)]
            return [entry for entry in cookies if entry], "cookies-object"
        if isinstance(payload.get("data"), list):
            cookies = [_normalize_cookie_entry(entry) for entry in payload["data"] if isinstance(entry, dict)]
            return [entry for entry in cookies if entry], "data-object"
        if all(isinstance(value, str) for value in payload.values()):
            cookies = [
                {
                    "name": key,
                    "value": value,
                    "domain": "",
                }
                for key, value in payload.items()
            ]
            return cookies, "name-value-object"

    raise ValueError("Unsupported cookie format. Expected a cookie list or object with cookies/data.")


def _build_cookie_header(cookies: list[dict[str, str]]) -> str:
    return "; ".join(f"{entry['name']}={entry['value']}" for entry in cookies)


def validate_cookie_file(platform: str, path: Path) -> CookieCheckResult:
    rules = PLATFORM_RULES[platform]
    cookies, format_name = load_cookie_file(path)
    domains = rules["domains"]
    required_names = rules["required_names"]

    matched_domains = sorted(
        {
            cookie["domain"]
            for cookie in cookies
            if any(domain in cookie["domain"] for domain in domains)
        }
    )
    present_names = sorted({cookie["name"] for cookie in cookies if cookie["name"] in required_names})
    missing_names = [name for name in required_names if name not in present_names]

    ok = bool(cookies) and bool(matched_domains or format_name == "name-value-object") and not missing_names
    if ok:
        message = f"Cookie file looks usable for {platform}"
    elif not cookies:
        message = "Cookie file contains no usable cookie entries"
    elif missing_names:
        message = f"Missing expected cookies: {', '.join(missing_names)}"
    else:
        message = f"No matching domains found for {platform}"

    return CookieCheckResult(
        ok=ok,
        platform=platform,
        file=path,
        cookie_count=len(cookies),
        matched_domains=matched_domains,
        present_names=present_names,
        missing_names=missing_names,
        format_name=format_name,
        message=message,
    )


def analyze_probe_response(platform: str, status_code: int | None, final_url: str | None, body: str) -> CookieProbeResult:
    rules = PLATFORM_RULES[platform]
    normalized_url = (final_url or "").lower()
    lowered_body = (body or "").lower()
    login_markers = [marker.lower() for marker in rules["login_markers"]]
    success_markers = [marker.lower() for marker in rules["success_markers"]]

    if status_code and status_code >= 400:
        return CookieProbeResult(
            ok=False,
            platform=platform,
            file=Path("."),
            status_code=status_code,
            final_url=final_url,
            mode="http_error",
            message=f"Probe returned HTTP {status_code}",
        )

    if any(marker in normalized_url or marker in lowered_body for marker in login_markers):
        return CookieProbeResult(
            ok=False,
            platform=platform,
            file=Path("."),
            status_code=status_code,
            final_url=final_url,
            mode="login_required",
            message="Cookie likely expired or redirected to login/verification",
        )

    if any(marker in lowered_body for marker in success_markers):
        return CookieProbeResult(
            ok=True,
            platform=platform,
            file=Path("."),
            status_code=status_code,
            final_url=final_url,
            mode="authenticated",
            message="Probe suggests the cookie is still usable",
        )

    return CookieProbeResult(
        ok=False,
        platform=platform,
        file=Path("."),
        status_code=status_code,
        final_url=final_url,
        mode="uncertain",
        message="Probe completed but could not confirm authenticated state",
    )


def probe_cookie_file(platform: str, path: Path, timeout: int = 12) -> CookieProbeResult:
    cookies, _ = load_cookie_file(path)
    probe_url = PLATFORM_RULES[platform]["probe_url"]
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml,application/json;q=0.9,*/*;q=0.8",
        "Cookie": _build_cookie_header(cookies),
    }
    request = Request(probe_url, headers=headers)

    try:
        with urlopen(request, timeout=timeout) as response:
            body = response.read(8192).decode("utf-8", errors="ignore")
            result = analyze_probe_response(platform, response.getcode(), response.geturl(), body)
    except HTTPError as exc:
        body = exc.read(8192).decode("utf-8", errors="ignore")
        result = analyze_probe_response(platform, exc.code, exc.geturl(), body)
    except URLError as exc:
        return CookieProbeResult(
            ok=False,
            platform=platform,
            file=path,
            status_code=None,
            final_url=None,
            mode="network_error",
            message=f"Probe failed: {exc.reason}",
        )

    result.file = path
    return result


def cookie_status(platform: str, path: Path | None, probe: bool = False, timeout: int = 12) -> dict[str, Any]:
    if not path:
        return {
            "platform": platform,
            "configured": False,
            "ok": False,
            "message": "No cookie file configured",
        }
    file_path = Path(path).expanduser()
    if not file_path.exists():
        return {
            "platform": platform,
            "configured": True,
            "ok": False,
            "message": f"Configured file does not exist: {file_path}",
        }
    result = validate_cookie_file(platform, file_path)
    payload = {
        "platform": platform,
        "configured": True,
        "ok": result.ok,
        "file": str(file_path),
        "cookie_count": result.cookie_count,
        "matched_domains": result.matched_domains,
        "present_names": result.present_names,
        "missing_names": result.missing_names,
        "format": result.format_name,
        "message": result.message,
    }
    if probe and result.ok:
        probe_result = probe_cookie_file(platform, file_path, timeout=timeout)
        payload["probe"] = {
            "ok": probe_result.ok,
            "mode": probe_result.mode,
            "status_code": probe_result.status_code,
            "final_url": probe_result.final_url,
            "message": probe_result.message,
        }
        payload["ok"] = payload["ok"] and probe_result.ok
    return payload
