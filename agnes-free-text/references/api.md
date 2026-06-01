# Agnes Free Text API Reference

Source document: `outputs/wechat-runs/2026-05-30-agnes-ai-free-api/文本模型文档.md`.

## Model

- Name: `agnes-2.0-flash`
- Provider: Sapiens AI
- Use cases: chat completion, multi-turn conversation, tool calling, agentic workflows, coding tasks, reasoning, streaming output, JSON-style output.

## Endpoint

```text
POST https://apihub.agnes-ai.com/v1/chat/completions
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json
```

## Request Fields

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `model` | string | yes | Fixed to `agnes-2.0-flash`. |
| `messages` | array | yes | OpenAI-style messages with `system`, `user`, and `assistant` roles. |
| `temperature` | number | no | Lower values make output more deterministic. |
| `top_p` | number | no | Nucleus sampling. |
| `max_tokens` | number | no | Maximum generated tokens. |
| `stream` | boolean | no | Enable streaming output. |
| `tools` | array | no | Function/tool definitions for agent workflows. |
| `tool_choice` | string/object | no | Controls whether and how tools are used. |

## Basic Request

```bash
curl https://apihub.agnes-ai.com/v1/chat/completions \
  -H "Authorization: Bearer $AGNES_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "agnes-2.0-flash",
    "messages": [
      {"role": "system", "content": "You are a helpful AI assistant."},
      {"role": "user", "content": "Explain how autonomous agents use tools."}
    ],
    "temperature": 0.7,
    "max_tokens": 1024
  }'
```

## Streaming Request

```json
{
  "model": "agnes-2.0-flash",
  "messages": [
    {"role": "user", "content": "Write a short product introduction for an AI assistant app."}
  ],
  "stream": true
}
```

## Tool Calling Shape

```json
{
  "model": "agnes-2.0-flash",
  "messages": [
    {"role": "user", "content": "What is the weather like in Singapore today?"}
  ],
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "get_weather",
        "description": "Get the current weather for a location",
        "parameters": {
          "type": "object",
          "properties": {
            "location": {
              "type": "string",
              "description": "The city and country"
            }
          },
          "required": ["location"]
        }
      }
    }
  ]
}
```

## Response Fields

Expect an OpenAI-style response with:

- `id`
- `object`
- `created`
- `model`
- `choices[].message.role`
- `choices[].message.content`
- `choices[].finish_reason`
- `usage.prompt_tokens`
- `usage.completion_tokens`
- `usage.total_tokens`

## Prompting Notes

- Give clear instructions, context, and desired output format.
- For coding tasks, include language, framework, error message, and expected behavior.
- For agent workflows, include the goal, available tools, constraints, and stopping conditions.
