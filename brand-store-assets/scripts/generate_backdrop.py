#!/usr/bin/env python3
"""Generate decorative backdrops for logo showcases and feature graphics.

This is optional. Store screenshots and app UI must always come from the real
build. The generated image is a texture/background only: never ask the model
to draw UI, devices, text, logos, or fake app screens.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

STYLE_PROMPTS = {
    "ink": (
        "Abstract editorial backdrop for a premium calm product. Deep ink field, "
        "one soft warm accent glow entering from the upper right, extremely fine film grain, "
        "subtle handmade paper texture, generous empty negative space, matte finish"
    ),
    "paper": (
        "Warm off-white handmade paper backdrop, visible cold-press fibers, soft natural "
        "window light, very subtle warm gray vignette, generous negative space, no shadows"
    ),
    "frosted": (
        "Deep titanium gray frosted glass backdrop, fine organic grain, a large low-saturation "
        "cold blue-gray halo dissolving at the edges, sophisticated and breathable"
    ),
    "mist": (
        "Warm ivory backdrop with a thin layer of morning haze, soft pastel mint and dawn "
        "orange light dissolving into the base, low contrast, approachable and calm"
    ),
    "studio": (
        "Extremely dark warm carbon gray studio backdrop, one softbox from the left creating "
        "a natural vignette, fine photographic grain, editorial magazine quality"
    ),
    "flat": (
        "Absolutely flat solid color backdrop, no gradient, no texture, no noise, pure graphic "
        "field with confident negative space"
    ),
    "void": (
        "Pure black void backdrop with extremely fine silver micro-noise and a faint icy glow "
        "at one extreme corner, cold and infinite"
    ),
}

NEGATIVE = (
    "No text, no letters, no words, no logo, no brand mark, no app UI, no device, no phone, "
    "no screenshot, no people, no objects, no collage, no mockup. Background texture only."
)


def parse_config(path: Path) -> Dict[str, str]:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        data = json.loads(text)
        return {
            "api_key": str(data.get("api_key") or data.get("key") or ""),
            "base_url": str(data.get("base_url") or data.get("url") or ""),
            "model": str(data.get("model") or ""),
        }

    section = text
    marker = re.search(r"##+\s*绘图", text)
    if marker:
        section = text[marker.start():]
    key = re.search(r"API\s*KEY\s*[:：]\s*(\S+)", section, re.IGNORECASE)
    url = re.search(r"URL\s*[:：]\s*(https?://\S+)", section, re.IGNORECASE)
    models = re.search(r"模型\s*ID\s*[:：]\s*(.+)", section)
    model = ""
    if models:
        candidates = re.findall(r"[A-Za-z0-9._-]+", models.group(1))
        model = candidates[0] if candidates else ""
    return {
        "api_key": key.group(1) if key else "",
        "base_url": url.group(1).rstrip("/") if url else "",
        "model": model,
    }


def curl_json(url: str, key: str, payload: Optional[Dict[str, Any]], timeout: int) -> Any:
    curl = shutil.which("curl")
    if not curl:
        raise RuntimeError("curl not found")
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as handle:
        response_path = Path(handle.name)
    command = [
        curl, "-sS", "-L", "--max-time", str(timeout),
        "-H", f"Authorization: Bearer {key}",
        "-H", "Content-Type: application/json",
        "-H", "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "-o", str(response_path),
        "-w", "%{http_code}",
    ]
    if payload is not None:
        command.extend(["-X", "POST", "-d", json.dumps(payload, ensure_ascii=False)])
    command.append(url)
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=timeout + 15)
        status = (result.stdout or "").strip()
        raw = response_path.read_text(encoding="utf-8", errors="replace")
        if not raw:
            raise RuntimeError(f"empty response (HTTP {status}) {result.stderr[-400:]}")
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            raise RuntimeError(f"non-JSON response (HTTP {status}): {raw[:400]}")
        return parsed
    finally:
        response_path.unlink(missing_ok=True)


def urllib_json(url: str, key: str, payload: Optional[Dict[str, Any]], timeout: int) -> Any:
    data = json.dumps(payload, ensure_ascii=False).encode() if payload is not None else None
    request = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode())


def call_api(url: str, key: str, payload: Optional[Dict[str, Any]], timeout: int) -> Any:
    try:
        if shutil.which("curl"):
            return curl_json(url, key, payload, timeout)
        return urllib_json(url, key, payload, timeout)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode(errors="replace")[:600]
        raise RuntimeError(f"HTTP {exc.code}: {body}") from exc


def download(url: str, key: str, out: Path, timeout: int) -> None:
    curl = shutil.which("curl")
    out.parent.mkdir(parents=True, exist_ok=True)
    if curl:
        result = subprocess.run(
            [
                curl, "-fsSL", "-L", "--max-time", str(timeout),
                "-H", f"Authorization: Bearer {key}",
                "-o", str(out), url,
            ],
            capture_output=True, text=True, timeout=timeout + 15,
        )
        if result.returncode != 0 or not out.is_file():
            raise RuntimeError(f"download failed: {result.stderr[-400:]}")
        return
    request = urllib.request.Request(url, headers={"Authorization": f"Bearer {key}"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        out.write_bytes(response.read())


def list_models(base: str, key: str, timeout: int) -> List[str]:
    payload = call_api(f"{base}/models", key, None, timeout)
    if isinstance(payload, dict) and payload.get("error"):
        error = payload["error"]
        message = error.get("message") if isinstance(error, dict) else error
        raise RuntimeError(f"model list failed: {message}")
    data = payload.get("data") if isinstance(payload, dict) else None
    if not isinstance(data, list):
        return []
    return [str(item.get("id")) for item in data if isinstance(item, dict) and item.get("id")]


def choose_models(
    explicit: Optional[str], available: List[str], preferred_model: Optional[str] = None
) -> List[str]:
    if explicit:
        return [explicit]
    preferred = [
        preferred_model or "",
        "gpt-image-2",
        "gpt-image-2.5",
        "grok-imagine-image-quality",
        "grok-imagine-image",
    ]
    ordered = [model for model in preferred if model and model in available]
    ordered.extend(
        model for model in available
        if model not in ordered and "image" in model.lower() and "video" not in model.lower()
    )
    return ordered


def generate(
    base: str,
    key: str,
    models: List[str],
    prompt: str,
    size: str,
    quality: str,
    timeout: int,
    use_async: bool,
) -> Tuple[bytes, str]:
    last_error = ""
    for model in models:
        payload: Dict[str, Any] = {
            "model": model,
            "prompt": prompt,
            "size": size,
            "quality": quality,
            "response_format": "b64_json",
            "n": 1,
        }
        if use_async:
            payload["response_format"] = "url"
            payload["async"] = True
        try:
            response = call_api(f"{base}/images/generations", key, payload, timeout)
            if isinstance(response, dict) and response.get("error"):
                error = response["error"]
                last_error = f"{model}: {error.get('message') if isinstance(error, dict) else error}"
                continue

            data = response.get("data") if isinstance(response, dict) else None
            if isinstance(data, list) and data:
                item = data[0]
                if item.get("b64_json"):
                    return base64.b64decode(item["b64_json"]), model
                if item.get("url"):
                    with tempfile.NamedTemporaryFile(suffix=".img", delete=False) as handle:
                        temp = Path(handle.name)
                    try:
                        download(item["url"], key, temp, timeout)
                        return temp.read_bytes(), model
                    finally:
                        temp.unlink(missing_ok=True)

            image_id = response.get("id") if isinstance(response, dict) else None
            if image_id:
                deadline = time.time() + timeout
                while time.time() < deadline:
                    status_payload = call_api(f"{base}/images/{image_id}", key, None, timeout)
                    status = str(status_payload.get("status") or "")
                    if status == "completed":
                        content_url = status_payload.get("content_url") or f"/images/{image_id}/content"
                        if str(content_url).startswith("/"):
                            content_url = base + "/" + str(content_url).lstrip("/")
                        with tempfile.NamedTemporaryFile(suffix=".img", delete=False) as handle:
                            temp = Path(handle.name)
                        try:
                            download(str(content_url), key, temp, timeout)
                            return temp.read_bytes(), model
                        finally:
                            temp.unlink(missing_ok=True)
                    if status == "failed":
                        last_error = f"{model}: task failed: {status_payload.get('error')}"
                        break
                    time.sleep(3)
                else:
                    last_error = f"{model}: timed out waiting for async task {image_id}"
                continue

            last_error = f"{model}: unexpected response {str(response)[:240]}"
        except Exception as exc:
            last_error = f"{model}: {exc}"
    raise RuntimeError(last_error or "no image model available")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--prompt", default=None)
    parser.add_argument("--style", choices=sorted(STYLE_PROMPTS), default=None)
    parser.add_argument("--size", default="1024x1024")
    parser.add_argument("--quality", default="high")
    parser.add_argument("--model", default=None)
    parser.add_argument("--count", type=int, default=1)
    parser.add_argument("--config", type=Path, default=None, help="Markdown or JSON config")
    parser.add_argument("--base-url", default=None)
    parser.add_argument("--api-key", default=None)
    parser.add_argument("--api-key-env", default="IMAGE_API_KEY")
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--async-mode", action="store_true")
    parser.add_argument("--list-models", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    config: Dict[str, str] = {}
    if args.config:
        config = parse_config(args.config.resolve())

    key = (
        args.api_key
        or os.environ.get(args.api_key_env)
        or config.get("api_key")
        or ""
    )
    base = (
        args.base_url
        or os.environ.get("IMAGE_API_BASE")
        or config.get("base_url")
        or "https://api.krill-code.net/v1"
    ).rstrip("/")
    explicit_model = args.model or os.environ.get("IMAGE_MODEL") or None
    config_model = config.get("model") or None

    if not key:
        print(
            f"ERROR: no API key. Set {args.api_key_env}, pass --api-key, or use --config.",
            file=sys.stderr,
        )
        return 2

    if args.list_models:
        try:
            models = list_models(base, key, args.timeout)
        except Exception as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 1
        for model in models:
            print(model)
        return 0

    if not args.prompt and not args.style:
        parser.error("pass --prompt or --style")

    prompt_parts = []
    if args.style:
        prompt_parts.append(STYLE_PROMPTS[args.style])
    if args.prompt:
        prompt_parts.append(args.prompt.strip())
    prompt = ". ".join(part.rstrip(".") for part in prompt_parts) + ". " + NEGATIVE

    if args.dry_run:
        print(f"base: {base}")
        print(f"model: {explicit_model or config_model or 'auto'}")
        print(f"size: {args.size}")
        print(f"prompt: {prompt}")
        return 0

    try:
        available = list_models(base, key, args.timeout)
        models = choose_models(explicit_model, available, config_model)
        if not models:
            print("ERROR: no image model available", file=sys.stderr)
            return 1
        import io

        from PIL import Image

        for index in range(1, max(1, args.count) + 1):
            raw, used_model = generate(
                base, key, models, prompt, args.size, args.quality, args.timeout, args.async_mode
            )
            suffix = "" if args.count == 1 else f"-{index}"
            target = args.out.with_name(f"{args.out.stem}{suffix}{args.out.suffix}")
            target.parent.mkdir(parents=True, exist_ok=True)
            with Image.open(io.BytesIO(raw)) as image:
                image = image.convert("RGB")
                if target.suffix.lower() in (".jpg", ".jpeg"):
                    image.save(target, "JPEG", quality=94, subsampling=0, optimize=True)
                else:
                    image.save(target, "PNG", optimize=True)
                width, height = image.size
            print(f"wrote {target} ({width}x{height}, model {used_model})")
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
