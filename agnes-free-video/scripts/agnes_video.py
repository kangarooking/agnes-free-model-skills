#!/usr/bin/env python3
"""Create, poll, and download Agnes-Video-V2.0 tasks."""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
from pathlib import Path
import sys
import time
from typing import Any
from urllib import error, parse, request


API_BASE = os.environ.get("AGNES_API_BASE", "https://apihub.agnes-ai.com").rstrip("/")
MODEL = "agnes-video-v2.0"
RUNNING_STATES = {"queued", "in_progress", "processing", "submitted", "pending"}
DONE_STATES = {"completed", "succeeded", "success"}
FAILED_STATES = {"failed", "cancelled", "canceled", "error"}


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


def validate_num_frames(value: int) -> None:
    if value > 441 or value < 1 or (value - 1) % 8 != 0:
        raise SystemExit("num_frames must be <= 441 and satisfy 8n + 1, such as 81, 121, 161, 241, or 441.")


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    validate_num_frames(args.num_frames)
    payload: dict[str, Any] = {
        "model": MODEL,
        "prompt": args.prompt,
        "height": args.height,
        "width": args.width,
        "num_frames": args.num_frames,
        "frame_rate": args.frame_rate,
    }
    optional_values = {
        "num_inference_steps": args.num_inference_steps,
        "seed": args.seed,
        "negative_prompt": args.negative_prompt,
    }
    for key, value in optional_values.items():
        if value is not None:
            payload[key] = value

    image_urls = args.image_url or []
    if len(image_urls) == 1 and args.mode not in {"keyframes", "multi-image"}:
        payload["image"] = image_urls[0]
    elif image_urls:
        payload["extra_body"] = {"image": image_urls}
        if args.mode == "keyframes":
            payload["extra_body"]["mode"] = "keyframes"
    if args.mode and args.mode not in {"keyframes", "multi-image"}:
        payload["mode"] = args.mode
    return payload


def extract_task_id(response: dict[str, Any]) -> str:
    for key in ("id", "task_id"):
        value = response.get(key)
        if isinstance(value, str):
            return value
    data = response.get("data")
    if isinstance(data, dict):
        for key in ("id", "task_id"):
            value = data.get(key)
            if isinstance(value, str):
                return value
    raise ApiError(f"Could not find task id in response: {json.dumps(response, ensure_ascii=False)}")


def get_status(token: str, api_base: str, task_id: str) -> dict[str, Any]:
    return request_json("GET", f"{api_base.rstrip('/')}/v1/videos/{parse.quote(task_id)}", token)


def extract_status(response: dict[str, Any]) -> str:
    value = response.get("status")
    if isinstance(value, str):
        return value.lower()
    data = response.get("data")
    if isinstance(data, dict) and isinstance(data.get("status"), str):
        return data["status"].lower()
    return "unknown"


def extract_video_url(response: dict[str, Any]) -> str | None:
    for key in ("video_url", "url", "remixed_from_video_id"):
        value = response.get(key)
        if isinstance(value, str) and value.startswith(("http://", "https://")):
            return value
    data = response.get("data")
    if isinstance(data, dict):
        return extract_video_url(data)
    return None


def poll_task(token: str, api_base: str, task_id: str, interval: float, timeout: float) -> dict[str, Any]:
    deadline = time.time() + timeout
    last_response: dict[str, Any] | None = None
    while time.time() <= deadline:
        response = get_status(token, api_base, task_id)
        last_response = response
        status = extract_status(response)
        progress = response.get("progress")
        if progress is None and isinstance(response.get("data"), dict):
            progress = response["data"].get("progress")
        print(f"Task {task_id}: status={status} progress={progress}", file=sys.stderr)
        if status in DONE_STATES:
            return response
        if status in FAILED_STATES:
            raise ApiError(f"Video task failed with status '{status}'", payload=response)
        if status not in RUNNING_STATES and status != "unknown":
            print(f"Unknown status '{status}', continuing to poll.", file=sys.stderr)
        time.sleep(interval)
    raise ApiError(f"Timed out waiting for task {task_id}", payload=last_response)


def filename_from_url(url: str) -> str:
    parsed = parse.urlparse(url)
    name = Path(parsed.path).name
    if not name or "." not in name:
        ext = mimetypes.guess_extension("video/mp4") or ".mp4"
        name = f"agnes-video{ext}"
    return name


def download_video(url: str, output_dir: str) -> Path:
    directory = Path(output_dir).expanduser()
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / filename_from_url(url)
    with request.urlopen(url, timeout=600) as resp:
        path.write_bytes(resp.read())
    return path


def maybe_download(response: dict[str, Any], output_dir: str | None, download: bool) -> None:
    if not output_dir and not download:
        return
    video_url = extract_video_url(response)
    if not video_url:
        print("No video_url found in response.", file=sys.stderr)
        return
    directory = output_dir or "./outputs/agnes-free-video"
    path = download_video(video_url, directory)
    print(f"Downloaded: {path}")


def cmd_create(args: argparse.Namespace) -> int:
    payload = build_payload(args)
    url = f"{args.api_base.rstrip('/')}/v1/videos"
    if args.dry_run:
        print(json.dumps({"url": url, "payload": payload}, ensure_ascii=False, indent=2))
        return 0

    token = get_api_key()
    try:
        response = request_json("POST", url, token, payload)
        print(json.dumps(response, ensure_ascii=False, indent=2))
        if args.no_poll:
            return 0
        task_id = extract_task_id(response)
        final = poll_task(token, args.api_base, task_id, args.poll_interval, args.timeout)
        print(json.dumps(final, ensure_ascii=False, indent=2))
        maybe_download(final, args.output_dir, args.download)
    except ApiError as exc:
        print(f"Agnes API error: {exc}", file=sys.stderr)
        if exc.payload is not None:
            print(json.dumps(exc.payload, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    token = get_api_key()
    try:
        if args.wait:
            response = poll_task(token, args.api_base, args.task_id, args.poll_interval, args.timeout)
        else:
            response = get_status(token, args.api_base, args.task_id)
        print(json.dumps(response, ensure_ascii=False, indent=2))
        maybe_download(response, args.output_dir, args.download)
    except ApiError as exc:
        print(f"Agnes API error: {exc}", file=sys.stderr)
        if exc.payload is not None:
            print(json.dumps(exc.payload, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1
    return 0


def add_common_create_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--image-url", action="append", help="Input image URL; repeat for multi-image or keyframes")
    parser.add_argument("--mode", choices=["ti2vid", "keyframes", "multi-image"])
    parser.add_argument("--height", type=int, default=768)
    parser.add_argument("--width", type=int, default=1152)
    parser.add_argument("--num-frames", type=int, default=121)
    parser.add_argument("--num-inference-steps", type=int)
    parser.add_argument("--seed", type=int)
    parser.add_argument("--frame-rate", type=float, default=24)
    parser.add_argument("--negative-prompt")
    parser.add_argument("--output-dir")
    parser.add_argument("--download", action="store_true", help="Download video_url when the task completes")
    parser.add_argument("--no-poll", action="store_true", help="Only submit the task and print the task id")
    parser.add_argument("--poll-interval", type=float, default=10)
    parser.add_argument("--timeout", type=float, default=900)
    parser.add_argument("--api-base", default=API_BASE)
    parser.add_argument("--dry-run", action="store_true", help="Print request JSON without calling the API")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create and retrieve Agnes-Video-V2.0 tasks.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    create = subparsers.add_parser("create", help="Create a video generation task")
    add_common_create_args(create)
    create.set_defaults(func=cmd_create)

    status = subparsers.add_parser("status", help="Retrieve a video task")
    status.add_argument("--task-id", required=True)
    status.add_argument("--wait", action="store_true", help="Poll until the task completes or fails")
    status.add_argument("--poll-interval", type=float, default=10)
    status.add_argument("--timeout", type=float, default=900)
    status.add_argument("--download", action="store_true")
    status.add_argument("--output-dir")
    status.add_argument("--api-base", default=API_BASE)
    status.set_defaults(func=cmd_status)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
