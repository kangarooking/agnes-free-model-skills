---
name: agnes-free-text
description: Call the free Agnes text model API for chat completions, streaming answers, coding help, tool-calling experiments, and OpenAI-compatible text generation. Use when the user asks for 免费文本, 免费的文本模型, free text API, Agnes text, Agnes-2.0-Flash, free LLM calls, or wants to use a free chat/completion model through an Agent skill.
---

# Agnes Free Text

Use this skill to call Sapiens AI's Agnes-2.0-Flash text model through the Agnes API.

## Credential Rule

Read the API key from the environment. Do not hardcode keys in prompts, scripts, skill files, commits, or shell history.

Preferred variable:

```bash
export AGNES_API_KEY="..."
```

The helper also accepts `AGNES_TOKEN` as a fallback.

## Quick Start

Run a normal chat completion:

```bash
python3 scripts/agnes_text.py chat \
  --prompt "用三句话解释 Agent 为什么需要工具调用"
```

Use a system prompt and save the raw response JSON:

```bash
python3 scripts/agnes_text.py chat \
  --system "You are a concise technical writer." \
  --prompt "Explain tool calling for a beginner." \
  --output-json ./outputs/agnes-free-text/response.json
```

Pass tool definitions from JSON:

```bash
python3 scripts/agnes_text.py chat \
  --prompt "Decide whether a weather tool is needed." \
  --tools-json ./tools.json \
  --tool-choice auto
```

Validate the request shape without calling the API:

```bash
python3 scripts/agnes_text.py chat \
  --prompt "Write a short product intro." \
  --max-tokens 300 \
  --dry-run
```

## Workflow

1. Clarify whether the user wants a direct answer, JSON-like structured output, coding help, or streaming output.
2. Use `scripts/agnes_text.py` for repeatable calls. Prefer `--dry-run` first when parameters are complex.
3. Keep the model fixed to `agnes-2.0-flash` unless the API docs are updated.
4. For multi-turn context, pass repeated `--message role:content` values instead of flattening the conversation into one prompt.
5. For tool calling, pass `--tools-json` as either an inline JSON array or a path to a JSON file.

## Notes

- Endpoint: `POST https://apihub.agnes-ai.com/v1/chat/completions`
- Model: `agnes-2.0-flash`
- Request shape is compatible with OpenAI Chat Completions.
- Supported features include system prompts, multi-turn messages, streaming, tool definitions, and tool choice.
- If the API returns an authorization error, check `AGNES_API_KEY` first.

## Reference

Read `references/api.md` when you need endpoint details, response fields, tool-calling shape, or streaming examples.
