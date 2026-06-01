# Agnes Free Image API Reference

Source document: `outputs/wechat-runs/2026-05-30-agnes-ai-free-api/图片模型文档.md`.

## Model

- Name: `agnes-image-2.1-flash`
- Use cases: text-to-image, image-to-image, high-information-density visuals, composition-preserving transformations, marketing creatives, thumbnails, banners, storytelling visuals.

## Endpoint

```text
POST https://apihub.agnes-ai.com/v1/images/generations
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json
```

## Request Fields

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `model` | string | yes | Fixed to `agnes-image-2.1-flash`. |
| `prompt` | string | yes | Text instruction for generation or editing. |
| `size` | string | no | Output size such as `1024x768`. |
| `extra_body` | object | no | Advanced workflow parameters. |
| `extra_body.image` | array | no | Input image URLs for image-to-image. |
| `extra_body.response_format` | string | no | Use `url` to request image URLs. |

## Text-To-Image Request

```bash
curl https://apihub.agnes-ai.com/v1/images/generations \
  -H "Authorization: Bearer $AGNES_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "agnes-image-2.1-flash",
    "prompt": "A luminous floating city above a misty canyon at sunrise, cinematic realism",
    "size": "1024x768"
  }'
```

## Image-To-Image Request

```bash
curl https://apihub.agnes-ai.com/v1/images/generations \
  -H "Authorization: Bearer $AGNES_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "agnes-image-2.1-flash",
    "prompt": "Transform the scene into a rain-soaked cyberpunk night with neon reflections while preserving the composition",
    "size": "1024x768",
    "extra_body": {
      "image": ["https://example.com/input-image.png"],
      "response_format": "url"
    }
  }'
```

## Prompt Structure

```text
[Subject] + [Scene / Environment] + [Style] + [Lighting] + [Composition] + [Quality Requirements]
```

For image-to-image, specify:

- What should change
- What should remain unchanged
- Composition or subject preservation requirements

## High-Density Visuals

For complex visuals, describe:

- Main subject
- Background environment
- Important secondary details
- Style and lighting
- Composition constraints
- Preservation requirements for image-to-image

## Notes

- Use `agnes-image-2.1-flash` as the model name.
- For text-to-image, `model` and `prompt` are required.
- For image-to-image, provide input image URLs under `extra_body.image`.
- Use `extra_body.response_format: "url"` when generated results should be returned as image URLs.
- Do not expose temporary API keys in public documentation.
