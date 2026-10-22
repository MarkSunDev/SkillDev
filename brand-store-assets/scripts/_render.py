#!/usr/bin/env python3
"""Shared helpers for deterministic HTML-to-PNG rendering.

The renderer uses a locally installed Chromium-based browser in headless mode.
It does not need Playwright, Puppeteer, CairoSVG, or ImageMagick.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple


MAC_BROWSERS = (
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    "/Applications/Vivaldi.app/Contents/MacOS/Vivaldi",
)

LINUX_BROWSERS = (
    "google-chrome",
    "google-chrome-stable",
    "chromium",
    "chromium-browser",
    "microsoft-edge",
    "microsoft-edge-stable",
    "brave-browser",
)

WINDOWS_BROWSERS = (
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
)

HEX_RE = re.compile(r"^#?([0-9A-Fa-f]{3}|[0-9A-Fa-f]{6})$")
SIZE_RE = re.compile(r"^(\d+)\s*[xX×]\s*(\d+)$")


def find_browser(explicit: Optional[str] = None) -> str:
    """Return a Chromium-based browser executable."""
    candidates: List[str] = []
    if explicit:
        candidates.append(explicit)
    if os.environ.get("BROWSER_BIN"):
        candidates.append(os.environ["BROWSER_BIN"])

    cache = Path.home() / "Library" / "Caches" / "ms-playwright"
    for pattern in (
        "chromium-*/chrome-mac/Chromium.app/Contents/MacOS/Chromium",
        "chromium_headless_shell-*/chrome-mac/headless_shell",
    ):
        candidates.extend(str(p) for p in sorted(cache.glob(pattern), reverse=True))

    candidates.extend(MAC_BROWSERS)
    candidates.extend(LINUX_BROWSERS)
    candidates.extend(WINDOWS_BROWSERS)

    for candidate in candidates:
        path = Path(os.path.expanduser(candidate))
        if path.is_file() and os.access(path, os.X_OK):
            return str(path)

    raise RuntimeError(
        "No Chromium-based browser found. Install Google Chrome, Chromium, or "
        "Microsoft Edge, or set BROWSER_BIN=/path/to/browser. "
        "The renderer deliberately avoids Puppeteer/Playwright downloads."
    )


def resolve_path(value: str, base: Path) -> Path:
    path = Path(os.path.expanduser(str(value)))
    if not path.is_absolute():
        path = Path(base) / path
    return path.resolve()


def parse_size(value: str) -> Tuple[int, int]:
    match = SIZE_RE.match(str(value).strip())
    if not match:
        raise ValueError(f"'{value}' is not a size such as 1320x2868")
    width, height = int(match.group(1)), int(match.group(2))
    if width <= 0 or height <= 0:
        raise ValueError(f"'{value}' must contain positive dimensions")
    return width, height


def hex_to_rgb(value: str) -> Tuple[int, int, int]:
    match = HEX_RE.match(str(value).strip())
    if not match:
        raise ValueError(f"'{value}' is not a hex color such as #F7F4ED")
    raw = match.group(1)
    if len(raw) == 3:
        raw = "".join(ch * 2 for ch in raw)
    return int(raw[0:2], 16), int(raw[2:4], 16), int(raw[4:6], 16)


def relative_luminance(value: str) -> float:
    channels = []
    for channel in hex_to_rgb(value):
        c = channel / 255.0
        channels.append(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
    return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]


def contrast_ratio(a: str, b: str) -> float:
    la, lb = relative_luminance(a), relative_luminance(b)
    lighter, darker = max(la, lb), min(la, lb)
    return (lighter + 0.05) / (darker + 0.05)


def load_manifest(path: Path) -> Tuple[Path, Dict[str, Any], List[Dict[str, Any]]]:
    path = Path(path).resolve()
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        root: Dict[str, Any] = {"images": data}
    elif isinstance(data, dict):
        root = data
    else:
        raise ValueError("manifest must be an array of images or an object")

    images = root.get("images")
    if not isinstance(images, list) or not images:
        raise ValueError("manifest must contain a non-empty 'images' array")
    if not all(isinstance(item, dict) for item in images):
        raise ValueError("every entry in 'images' must be an object")
    return path, root, images  # type: ignore[return-value]


def inline_svg(path: Path, ink: str) -> str:
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"<\?xml[^>]*\?>", "", text).strip()
    text = re.sub(r"<!DOCTYPE[^>]*>", "", text, flags=re.IGNORECASE).strip()
    text = text.replace("currentColor", ink)
    if "xmlns=" not in text[:300]:
        text = text.replace("<svg", '<svg xmlns="http://www.w3.org/2000/svg"', 1)
    return text


def prepare_brand(root: Dict[str, Any], base_dir: Path, ink: str) -> Dict[str, Any]:
    brand = root.get("brand") if isinstance(root.get("brand"), dict) else {}
    name = str(brand.get("name") or root.get("app") or "App").strip()
    logo_value = brand.get("logo")
    logo_svg: Optional[str] = None
    logo_url: Optional[str] = None

    inline = brand.get("logo_svg")
    if inline:
        logo_svg = str(inline).replace("currentColor", ink)
    elif logo_value:
        logo_path = resolve_path(str(logo_value), base_dir)
        if logo_path.is_file() and logo_path.suffix.lower() == ".svg":
            logo_svg = inline_svg(logo_path, ink)
        elif logo_path.is_file():
            logo_url = logo_path.as_uri()
        else:
            raise FileNotFoundError(f"brand logo not found: {logo_path}")

    initials = str(brand.get("initials") or "").strip()
    if not initials:
        words = [word for word in re.split(r"\s+", name) if word]
        initials = "".join(word[0] for word in words[:2]).upper() or name[:1].upper()

    return {
        "name": name,
        "logo_svg": logo_svg,
        "logo_url": logo_url,
        "initials": initials,
    }


def image_aspect(path: Path, fallback: float = 1320 / 2868) -> float:
    try:
        from PIL import Image

        with Image.open(path) as img:
            return img.width / img.height
    except Exception:
        return fallback


def typography(root: Dict[str, Any]) -> Dict[str, str]:
    config = root.get("typography") if isinstance(root.get("typography"), dict) else {}
    headline = str(
        config.get("headline")
        or '"Instrument Serif", "Songti SC", "Noto Serif SC", serif'
    )
    body = str(
        config.get("body")
        or '"Public Sans", "PingFang SC", "Noto Sans SC", sans-serif'
    )
    weight = config.get("headline_weight", 850)
    try:
        weight = int(weight)
    except (TypeError, ValueError):
        weight = 850
    line2 = str(config.get("line2") or "serif")
    return {"headline": headline, "body": body, "headline_weight": weight, "line2": line2}


def render_html(
    template: Path,
    data: Dict[str, Any],
    out_path: Path,
    width: int,
    height: int,
    transparent: bool = False,
    wait_ms: int = 5000,
    browser: Optional[str] = None,
    timeout: int = 180,
) -> Path:
    """Inject JSON into a template and screenshot it at an exact viewport size."""
    template = Path(template).resolve()
    if not template.is_file():
        raise FileNotFoundError(f"template not found: {template}")

    html = template.read_text(encoding="utf-8")
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    if "__DATA_JSON__" not in html:
        raise ValueError(f"{template.name} has no __DATA_JSON__ placeholder")
    html = html.replace("__DATA_JSON__", payload)
    html = html.replace("__VIEWPORT_W__", str(width)).replace("__VIEWPORT_H__", str(height))

    handle, temp_name = tempfile.mkstemp(
        prefix=".render-", suffix=".html", dir=str(template.parent)
    )
    os.close(handle)
    temp_html = Path(temp_name)
    temp_html.write_text(html, encoding="utf-8")

    profile_dir = tempfile.mkdtemp(prefix="brand-assets-profile-")
    out_path = Path(out_path).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        browser_bin = find_browser(browser)
        command = [
            browser_bin,
            "--headless=new",
            "--disable-gpu",
            "--hide-scrollbars",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-background-networking",
            "--disable-sync",
            "--disable-extensions",
            "--mute-audio",
            "--allow-file-access-from-files",
            "--force-device-scale-factor=1",
            f"--window-size={width},{height}",
            f"--user-data-dir={profile_dir}",
            f"--virtual-time-budget={wait_ms}",
            f"--screenshot={out_path}",
        ]
        if transparent:
            command.append("--default-background-color=00000000")
        command.append(temp_html.as_uri())

        result = subprocess.run(
            command, capture_output=True, text=True, timeout=timeout, check=False
        )
        if not out_path.is_file() or out_path.stat().st_size == 0:
            stderr = (result.stderr or result.stdout or "").strip()
            raise RuntimeError(
                f"headless browser did not write {out_path}. "
                f"Exit code {result.returncode}. {stderr[-1200:]}"
            )

        try:
            from PIL import Image

            with Image.open(out_path) as img:
                if img.size != (width, height):
                    raise RuntimeError(
                        f"rendered size is {img.width}x{img.height}, "
                        f"expected {width}x{height}"
                    )
        except ImportError:
            pass

        return out_path
    finally:
        temp_html.unlink(missing_ok=True)
        shutil.rmtree(profile_dir, ignore_errors=True)


def save_rgb(
    source: Path,
    destination: Path,
    size: Optional[Tuple[int, int]] = None,
    jpeg: bool = False,
    quality: int = 92,
) -> Path:
    """Flatten to RGB, optionally resize, and save as PNG or JPEG."""
    from PIL import Image

    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(source) as img:
        img = img.convert("RGB")
        if size and img.size != size:
            img = img.resize(size, Image.LANCZOS)
        if jpeg or destination.suffix.lower() in (".jpg", ".jpeg"):
            img.save(
                destination,
                "JPEG",
                quality=quality,
                subsampling=0,
                optimize=True,
                progressive=True,
            )
        else:
            img.save(destination, "PNG", optimize=True)
    return destination


def save_png(image: Any, destination: Path, optimize: bool = True) -> Path:
    from PIL import Image

    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    image.save(destination, "PNG", optimize=optimize)
    return destination


def write_json(path: Path, payload: Any) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return path


def human_size(num_bytes: int) -> str:
    if num_bytes < 1024:
        return f"{num_bytes} B"
    if num_bytes < 1024 * 1024:
        return f"{num_bytes / 1024:.1f} KB"
    return f"{num_bytes / (1024 * 1024):.2f} MB"
