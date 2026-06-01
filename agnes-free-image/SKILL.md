---
name: agnes-free-image
description: Generate free images with Agnes Image 2.1 Flash through the Agnes API, including text-to-image, image-to-image, high-density visual prompts, URL results, and local downloads. Use when the user asks for 免费图片, 免费的图片模型, free image API, Agnes image, Agnes Image 2.1 Flash, free AI image generation, image-to-image via Agnes, or wants a free image model Agent skill.
---

# Agnes Free Image

Use this skill to generate or transform images with `agnes-image-2.1-flash`.

## Credential Rule

Read the API key from the environment. Do not hardcode keys in prompts, scripts, skill files, commits, or shell history.

Preferred variable:

```bash
export AGNES_API_KEY="..."
```

The helper also accepts `AGNES_TOKEN` as a fallback.

## Quick Start

Text-to-image:

```bash
python3 scripts/agnes_image.py generate \
  --prompt "A luminous floating city above a misty canyon at sunrise, cinematic realism" \
  --size 1024x768 \
  --output-dir ./outputs/agnes-free-image
```

Image-to-image with a public image URL:

```bash
python3 scripts/agnes_image.py generate \
  --prompt "Transform the scene into a rain-soaked cyberpunk night while preserving the composition" \
  --image-url "https://example.com/input.png" \
  --size 1024x768 \
  --output-dir ./outputs/agnes-free-image
```

Validate the request shape without calling the API:

```bash
python3 scripts/agnes_image.py generate \
  --prompt "A detailed AI workflow dashboard poster, clean editorial style" \
  --size 1024x1024 \
  --dry-run
```

## Prompt Pattern

Use this structure for text-to-image:

```text
[Subject] + [Scene / Environment] + [Style] + [Lighting] + [Composition] + [Quality Requirements]
```

For image-to-image, say both what should change and what should remain unchanged.

## Workflow

1. Decide whether the request is text-to-image or image-to-image.
2. Turn vague visual requests into a concrete prompt with subject, environment, style, lighting, composition, and detail level.
3. Use `scripts/agnes_image.py generate`. Prefer `--dry-run` first for complex prompts or reference images.
4. Save returned image URLs locally with `--output-dir` when the response includes downloadable URLs.
5. Read `references/api.md` when the raw response shape or advanced parameters matter.

## Notes

- Endpoint: `POST https://apihub.agnes-ai.com/v1/images/generations`
- Model: `agnes-image-2.1-flash`
- Default size in the helper is `1024x768`.
- For image-to-image, input images must be URL-accessible and are sent under `extra_body.image`.
- The helper asks for URL responses with `extra_body.response_format: "url"`.

## Reference

Read `references/api.md` when you need request fields, response handling, or prompt examples from the source docs.
