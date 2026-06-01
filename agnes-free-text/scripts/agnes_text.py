#!/usr/bin/env python3
"""Call the Agnes-2.0-Flash chat completions API."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
from typing import Any
from urllib import error, request


API_BASE = os.environ.get("AGNES_API_BASE", "https://apihub.agnes-ai.com").rstrip("/")
MODEL = "agnes-2.0-flash"


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


def request_json(url: str, token: str, payload: dict[str, Any]) -> dict[str, Any]:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=120) as resp:
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


def stream_response(url: str, token: str, payload: dict[str, Any]) -> None:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=120) as resp:
            for raw_line in resp:
                line = raw_line.decode("utf-8", errors="replace").rstrip()
                if line:
                    print(line)
    except error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        parsed = parse_json_or_text(raw)
        message = extract_error_message(parsed) or f"HTTP {exc.code}: {raw}"
        raise ApiError(message, status=exc.code, payload=parsed) from exc
    except error.URLError as exc:
        raise ApiError(f"Network error: {exc}") from exc


def parse_message(raw: str) -> dict[str, str]:
    if ":" not in raw:
        raise SystemExit(f"Invalid --message value. Use role:content, got: {raw}")
    role, content = raw.split(":", 1)
    role = role.strip()
    content = content.strip()
    if role not in {"system", "user", "assistant"}:
        raise SystemExit(f"Invalid message role: {role}")
    if not content:
        raise SystemExit("Message content cannot be empty.")
    return {"role": role, "content": content}


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    messages: list[dict[str, str]] = []
    if args.system:
        messages.append({"role": "system", "content": args.system})
    for raw in args.message or []:
        messages.append(parse_message(raw))
    if args.prompt:
        messages.append({"role": "user", "content": args.prompt})
    if not messages:
        raise SystemExit("Provide --prompt or at least one --message role:content value.")

    payload: dict[str, Any] = {
        "model": MODEL,
        "messages": messages,
    }
    optional_values = {
        "temperature": args.temperature,
        "top_p": args.top_p,
        "max_tokens": args.max_tokens,
        "stream": args.stream,
    }
    for key, value in optional_values.items():
        if value is not None:
            payload[key] = value
    if args.tools_json:
        payload["tools"] = read_json_value(args.tools_json, "--tools-json")
    if args.tool_choice:
        payload["tool_choice"] = read_json_value(args.tool_choice, "--tool-choice", allow_plain_string=True)
    return payload


def read_json_value(value: str, label: str, allow_plain_string: bool = False) -> Any:
    path = Path(value).expanduser()
    raw = path.read_text(encoding="utf-8") if path.exists() else value
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        if allow_plain_string and not raw.strip().startswith(("{", "[", '"')):
            return raw
        raise SystemExit(f"Invalid JSON for {label}: {exc}") from exc


def extract_text(response: dict[str, Any]) -> str | None:
    choices = response.get("choices")
    if isinstance(choices, list) and choices:
        first = choices[0]
        if isinstance(first, dict):
            message = first.get("message")
            if isinstance(message, dict) and isinstance(message.get("content"), str):
                return message["content"]
            if isinstance(first.get("text"), str):
                return first["text"]
    return None


def cmd_chat(args: argparse.Namespace) -> int:
    payload = build_payload(args)
    url = f"{args.api_base.rstrip('/')}/v1/chat/completions"

    if args.dry_run:
        print(json.dumps({"url": url, "payload": payload}, ensure_ascii=False, indent=2))
        return 0

    token = get_api_key()
    try:
        if args.stream:
            stream_response(url, token, payload)
            return 0
        response = request_json(url, token, payload)
    except ApiError as exc:
        print(f"Agnes API error: {exc}", file=sys.stderr)
        if exc.payload is not None:
            print(json.dumps(exc.payload, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1

    if args.output_json:
        output_path = Path(args.output_json).expanduser()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(response, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    text = extract_text(response)
    if text:
        print(text)
    else:
        print(json.dumps(response, ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Call Agnes-2.0-Flash chat completions.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    chat = subparsers.add_parser("chat", help="Submit a chat completion request")
    chat.add_argument("--prompt", help="User prompt to append as the final user message")
    chat.add_argument("--system", help="Optional system prompt")
    chat.add_argument("--message", action="append", help="Message as role:content; can be repeated")
    chat.add_argument("--temperature", type=float)
    chat.add_argument("--top-p", type=float)
    chat.add_argument("--max-tokens", type=int)
    chat.add_argument("--stream", action="store_true", help="Print raw streaming response lines")
    chat.add_argument("--tools-json", help="Tools JSON array or path to a JSON file")
    chat.add_argument("--tool-choice", help="Tool choice as a JSON value or plain string such as auto")
    chat.add_argument("--output-json", help="Write the raw response JSON to this path")
    chat.add_argument("--api-base", default=API_BASE)
    chat.add_argument("--dry-run", action="store_true", help="Print request JSON without calling the API")
    chat.set_defaults(func=cmd_chat)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
