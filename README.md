# Agnes Free Model Skills

Three Codex/Agent skills for calling Agnes AI free model APIs:

- `agnes-free-text`: free text chat completions with Agnes-2.0-Flash, including streaming and tool-calling examples.
- `agnes-free-image`: free image generation and image transformation with Agnes Image 2.1 Flash.
- `agnes-free-video`: free async video generation with Agnes-Video-V2.0, including task polling and video download helpers.

## Install

Copy the skill folders you need into your Codex skills directory:

```bash
cp -R agnes-free-text ~/.codex/skills/
cp -R agnes-free-image ~/.codex/skills/
cp -R agnes-free-video ~/.codex/skills/
```

You can also keep the repository anywhere and reference the `SKILL.md` files from your own agent runtime.

## Configuration

Set your Agnes API key in the environment. Do not hardcode keys in the skill files.

```bash
export AGNES_API_KEY="your_api_key_here"
```

The helper scripts also accept `AGNES_TOKEN` as a fallback. You can override the API host with `AGNES_API_BASE` if the endpoint changes.

## Quick Checks

```bash
python3 -m py_compile \
  agnes-free-text/scripts/agnes_text.py \
  agnes-free-image/scripts/agnes_image.py \
  agnes-free-video/scripts/agnes_video.py

python3 agnes-free-text/scripts/agnes_text.py --help
python3 agnes-free-image/scripts/agnes_image.py --help
python3 agnes-free-video/scripts/agnes_video.py --help
```

## Security

- API keys are read only from environment variables.
- No generated media, local run outputs, or private API keys are included.
- The reference docs use placeholder credentials only.

## License

MIT
