# Agnes Free Video API Reference

Source document: `outputs/wechat-runs/2026-05-30-agnes-ai-free-api/视频模型文档.md`.

## Model

- Name: `agnes-video-v2.0`
- Use cases: text-to-video, image-to-video, multi-image video, keyframe animation, scene motion control, cinematic marketing clips, product demos, social videos.

## Endpoints

```text
POST https://apihub.agnes-ai.com/v1/videos
GET  https://apihub.agnes-ai.com/v1/videos/{task_id}
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json
```

Video generation is asynchronous: create a task first, then retrieve the result by task ID.

## Create Task Fields

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `model` | string | yes | Fixed to `agnes-video-v2.0`. |
| `prompt` | string | yes | Video description. |
| `image` | string/array | no | Single input image URL or image URL array. |
| `mode` | string | no | Generation mode, such as `ti2vid` or `keyframes`. |
| `height` | integer | no | Default `768`. |
| `width` | integer | no | Default `1152`. |
| `num_frames` | integer | no | Must be `<= 441` and satisfy `8n + 1`. |
| `num_inference_steps` | integer | no | Inference step count. |
| `seed` | integer | no | Reproducibility seed. |
| `frame_rate` | number | no | Supported range `1-60`. |
| `negative_prompt` | string | no | What to avoid. |
| `extra_body.image` | array | no | Multi-image or keyframe input URLs. |
| `extra_body.mode` | string | no | Set to `keyframes` for keyframe animation. |

## Text-To-Video Request

```bash
curl -X POST https://apihub.agnes-ai.com/v1/videos \
  -H "Authorization: Bearer $AGNES_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "agnes-video-v2.0",
    "prompt": "A cinematic shot of a cat walking on the beach at sunset, soft ocean waves, warm golden lighting, realistic motion",
    "height": 768,
    "width": 1152,
    "num_frames": 121,
    "frame_rate": 24
  }'
```

## Image-To-Video Request

```json
{
  "model": "agnes-video-v2.0",
  "prompt": "The woman slowly turns around and looks back at the camera, natural facial expression, cinematic camera movement",
  "image": "https://example.com/image.png",
  "num_frames": 121,
  "frame_rate": 24
}
```

## Multi-Image Request

```json
{
  "model": "agnes-video-v2.0",
  "prompt": "Create a smooth transformation scene between the two reference images, cinematic lighting, consistent character identity, natural motion",
  "extra_body": {
    "image": [
      "https://example.com/image1.png",
      "https://example.com/image2.png"
    ]
  },
  "num_frames": 121,
  "frame_rate": 24
}
```

## Keyframe Request

```json
{
  "model": "agnes-video-v2.0",
  "prompt": "Generate a smooth cinematic transition between the keyframes, maintaining visual consistency and natural camera movement",
  "extra_body": {
    "image": [
      "https://example.com/keyframe1.png",
      "https://example.com/keyframe2.png"
    ],
    "mode": "keyframes"
  },
  "num_frames": 121,
  "frame_rate": 24
}
```

## Status Values

- `queued`
- `in_progress`
- `completed`
- `failed`

## Result Fields

Completed task responses may include:

- `id`
- `object`
- `model`
- `status`
- `progress`
- `created_at`
- `completed_at`
- `video_url`
- `size`
- `seconds`
- `usage.duration_seconds`

## Parameter Recommendations

| Use case | Recommended settings |
| --- | --- |
| Standard video generation | `width: 1152`, `height: 768`, `num_frames: 121`, `frame_rate: 24` |
| Short social video | `num_frames: 81` or `121`, `frame_rate: 24` |
| Smoother motion | Higher `frame_rate`, such as `24` or `30` |
| Reproducible result | Set a fixed `seed` |
| Keyframe transition | Use `extra_body.mode: "keyframes"` |
| Avoid unwanted content | Use `negative_prompt` |

## Prompt Notes

- Text-to-video: subject, action, scene, camera movement, lighting, style.
- Image-to-video: describe what should move while the key subject remains stable.
- Multi-image: describe how input images relate to each other.
- Keyframes: describe transition pacing, identity preservation, camera angle, and natural motion.
