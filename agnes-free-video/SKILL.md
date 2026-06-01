---
name: agnes-free-video
description: Create free Agnes video generation tasks and retrieve video results through Agnes-Video-V2.0, including text-to-video, image-to-video, multi-image video, keyframe animation, async polling, and video download. Use when the user asks for 免费视频, 免费的视频模型, free video API, Agnes video, Agnes-Video-V2.0, text-to-video, image-to-video, keyframes, or wants a free video model Agent skill.
---

# Agnes Free Video

Use this skill to create and poll asynchronous video generation tasks with `agnes-video-v2.0`.

## Credential Rule

Read the API key from the environment. Do not hardcode keys in prompts, scripts, skill files, commits, or shell history.

Preferred variable:

```bash
export AGNES_API_KEY="..."
```

The helper also accepts `AGNES_TOKEN` as a fallback.

## Quick Start

Text-to-video:

```bash
python3 scripts/agnes_video.py create \
  --prompt "A cinematic shot of a cat walking on the beach at sunset, soft ocean waves, warm golden lighting, realistic motion" \
  --width 1152 \
  --height 768 \
  --num-frames 121 \
  --frame-rate 24 \
  --output-dir ./outputs/agnes-free-video
```

Image-to-video:

```bash
python3 scripts/agnes_video.py create \
  --prompt "Animate the product with a slow camera push-in, soft studio reflections, stable identity" \
  --image-url "https://example.com/product.png" \
  --num-frames 121 \
  --frame-rate 24
```

Keyframe transition:

```bash
python3 scripts/agnes_video.py create \
  --prompt "Create a smooth cinematic transition between the keyframes with natural pacing" \
  --image-url "https://example.com/keyframe1.png" \
  --image-url "https://example.com/keyframe2.png" \
  --mode keyframes \
  --num-frames 121
```

Check an existing task:

```bash
python3 scripts/agnes_video.py status \
  --task-id task_123456 \
  --download \
  --output-dir ./outputs/agnes-free-video
```

Validate request shape without calling the API:

```bash
python3 scripts/agnes_video.py create \
  --prompt "A short cinematic AI product teaser, slow dolly shot, clean lighting" \
  --num-frames 81 \
  --dry-run
```

## Workflow

1. Decide the mode: text-to-video, image-to-video, multi-image, or keyframe animation.
2. Write the prompt with subject, action, scene, camera movement, lighting, and style.
3. Keep `num_frames` at `81`, `121`, `161`, `241`, or `441` unless the user has a specific duration need.
4. Use `scripts/agnes_video.py create` to submit and poll. Use `status` if the user already has a task ID.
5. Download the `video_url` promptly when it appears.

## Notes

- Create endpoint: `POST https://apihub.agnes-ai.com/v1/videos`
- Status endpoint: `GET https://apihub.agnes-ai.com/v1/videos/{task_id}`
- Model: `agnes-video-v2.0`
- Video generation is asynchronous.
- `num_frames` must be `<= 441` and satisfy `8n + 1`.
- Default helper settings are `1152x768`, `121` frames, and `24` FPS.

## Reference

Read `references/api.md` when you need request fields, task status values, error codes, or mode-specific prompt examples.
