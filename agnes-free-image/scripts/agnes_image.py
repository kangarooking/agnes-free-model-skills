#!/usr/bin/env python3
"""Generate Agnes Image 2.1 Flash images and download URL results."""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
from pathlib import Path
import re
import sys
from typing import Any
from urllib import error, parse, request


API_BASE = os.environ.get("AGNES_API_BASE", "https://apihub.agnes-ai.com").rstrip("/")
MODEL = "agnes-image-2.1-flash"


class ApiError(RuntimeError):
    def __init__(self, message: str, status: int | None = None, payload: Any = None):
        super().__init__(message)
        self.status = status
        self.payload = payload


def get_api_key() -> str:
    token = os.environ.get("AGNES_API_KEY") or os.environ.get("AGNES_TOKEN")
    if not token:
        raise SystemExit("Missing API key. Set AGNES_API_KEY, for example: export AGNES_API_KEY='...'")
    return token


def parse_json_or_text(raw: str) -> Any:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw


def extract_error_message(payload: Any) -> str | None:
    if isinstance(payload, dict):
        err = payload.get("error")
        if isinstance(err, dict):
            return str(err.get("message") or err.get("type") or err)
        if isinstance(err, str):
            return err
        if payload.get("message"):
            return str(payload["message"])
    return None


def request_json(method: str, url: str, token: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    data = None
    headers = {"Authorization": f"Bearer {token}"}
    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = request.Request(url, data=data, headers=headers, method=method)
    try:
        with request.urlopen(req, timeout=180) as resp:
            raw = resp.read().decode("utf-8")
    except error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        parsed = parse_json_or_text(raw)
        message = extract_error_message(parsed) or f"HTTP {exc.code}: {raw}"
        raise ApiError(message, status=exc.code, payload=parsed) from exc
    except error.URLError as exc:
        raise ApiError(f"Network error: {exc}") from exc

    parsed = parse_json_or_text(raw)
    if not isinstance(parsed, dict):
        raise ApiError(f"Expected JSON object, got: {raw[:300]}")
    if parsed.get("error"):
        raise ApiError(extract_error_message(parsed) or "API returned an error", payload=parsed)
    return parsed


def validate_size(value: str) -> None:
    if re.fullmatch(r"[1-9][0-9]{1,4}x[1-9][0-9]{1,4}", value) is None:
        raise SystemExit(f"Invalid size '{value}'. Use a pixel size such as 1024x768.")


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    validate_size(args.size)
    payload: dict[str, Any] = {
        "model": MODEL,
        "prompt": args.prompt,
        "size": args.size,
    }
    if args.image_url:
        payload["extra_body"] = {
            "image": args.image_url,
            "response_format": "url",
        }
    elif args.response_format:
        payload["extra_body"] = {"response_format": args.response_format}
    return payload


def collect_urls(value: Any) -> list[str]:
    urls: list[str] = []
    if isinstance(value, dict):
        for key, nested in value.items():
            if key in {"url", "image_url"} and isinstance(nested, str) and nested.startswith(("http://", "https://")):
                urls.append(nested)
            else:
                urls.extend(collect_urls(nested))
    elif isinstance(value, list):
        for item in value:
            urls.extend(collect_urls(item))
    return urls


def filename_from_url(url: str, index: int) -> str:
    parsed = parse.urlparse(url)
    name = Path(parsed.path).name
    if not name or "." not in name:
        ext = mimetypes.guess_extension("image/png") or ".png"
        name = f"agnes-image-{index:02d}{ext}"
    return name


def download_urls(urls: list[str], output_dir: str) -> list[Path]:
    directory = Path(output_dir).expanduser()
    directory.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for index, url in enumerate(urls, start=1):
        path = directory / filename_from_url(url, index)
        try:
            with request.urlopen(url, timeout=180) as resp:
                path.write_bytes(resp.read())
        except error.URLError as exc:
            print(f"Download failed for {url}: {exc}", file=sys.stderr)
            continue
        paths.append(path)
    return paths


def cmd_generate(args: argparse.Namespace) -> int:
    payload = build_payload(args)
    url = f"{args.api_base.rstrip('/')}/v1/images/generations"

    if args.dry_run:
        print(json.dumps({"url": url, "payload": payload}, ensure_ascii=False, indent=2))
        return 0

    token = get_api_key()
    try:
        response = request_json("POST", url, token, payload)
    except ApiError as exc:
        print(f"Agnes API error: {exc}", file=sys.stderr)
        if exc.payload is not None:
            print(json.dumps(exc.payload, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1

    print(json.dumps(response, ensure_ascii=False, indent=2))
    urls = collect_urls(response)
    if args.output_dir and urls:
        for path in download_urls(urls, args.output_dir):
            print(f"Downloaded: {path}")
    elif args.output_dir:
        print("No downloadable image URLs found in response.", file=sys.stderr)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate images with Agnes Image 2.1 Flash.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    generate = subparsers.add_parser("generate", help="Submit an image generation request")
    generate.add_argument("--prompt", required=True)
    generate.add_argument("--size", default="1024x768")
    generate.add_argument("--image-url", action="append", help="Reference image URL for image-to-image; repeatable")
    generate.add_argument("--response-format", default="url", choices=["url"])
    generate.add_argument("--output-dir", help="Download returned image URLs into this directory")
    generate.add_argument("--api-base", default=API_BASE)
    generate.add_argument("--dry-run", action="store_true", help="Print request JSON without calling the API")
    generate.set_defaults(func=cmd_generate)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
