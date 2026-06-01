# Agnes 免费模型 Agent Skills

[English](README.en.md)

这是一套可直接放进 Codex/Agent 运行环境的本地 skills，用来调用 Agnes AI 的免费文本、图片和视频模型 API。仓库只包含可复用的 skill 文件、参考文档和 Python 辅助脚本，不包含任何 API Key、生成结果或本地运行产物。

## 包含哪些 Skill

| Skill | 能力 | 适合场景 |
| --- | --- | --- |
| `agnes-free-text` | 调用 Agnes-2.0-Flash 免费文本模型，支持 Chat Completions、流式输出和工具调用实验。 | 用户说“用免费的文本模型”“免费文本 API”“Agnes 文本”等。 |
| `agnes-free-image` | 调用 Agnes Image 2.1 Flash 免费图片模型，支持文生图、图生图/图片改造，并下载返回图片。 | 用户说“用免费的图片模型”“免费图片生成”“Agnes 图片”等。 |
| `agnes-free-video` | 调用 Agnes-Video-V2.0 免费视频模型，创建异步任务、轮询状态并下载视频。 | 用户说“用免费视频模型”“免费生成视频”“Agnes 视频”等。 |

## 安装

把需要的 skill 文件夹复制到你的 Codex skills 目录：

```bash
cp -R agnes-free-text ~/.codex/skills/
cp -R agnes-free-image ~/.codex/skills/
cp -R agnes-free-video ~/.codex/skills/
```

也可以把这个仓库放在任意位置，然后在自己的 Agent 运行时里引用对应的 `SKILL.md`。

## 配置

请通过环境变量提供 Agnes API Key，不要把 Key 写进 skill、脚本或仓库。

```bash
export AGNES_API_KEY="your_api_key_here"
```

辅助脚本也支持 `AGNES_TOKEN` 作为备用变量。如果 Agnes 的接口域名发生变化，可以用 `AGNES_API_BASE` 覆盖默认地址。

## 快速校验

```bash
python3 -m py_compile \
  agnes-free-text/scripts/agnes_text.py \
  agnes-free-image/scripts/agnes_image.py \
  agnes-free-video/scripts/agnes_video.py

python3 agnes-free-text/scripts/agnes_text.py --help
python3 agnes-free-image/scripts/agnes_image.py --help
python3 agnes-free-video/scripts/agnes_video.py --help
```

## 使用示例

文本模型：

```bash
python3 agnes-free-text/scripts/agnes_text.py chat \
  --message "用三句话解释 Agent skill 是什么"
```

图片模型：

```bash
python3 agnes-free-image/scripts/agnes_image.py generate \
  --prompt "一张适合公众号封面的科技感插画，干净明亮"
```

视频模型：

```bash
python3 agnes-free-video/scripts/agnes_video.py create \
  --prompt "竖屏短视频，医生办公室，干净明亮的医疗科普画面，无文字，无旁白"
```

视频任务通常是异步的，可以继续轮询并下载：

```bash
python3 agnes-free-video/scripts/agnes_video.py status \
  --task-id task_123456 \
  --wait \
  --download-dir downloads
```

## 安全边界

- API Key 只从环境变量读取。
- 仓库不包含真实密钥、生成媒体、本地运行输出或用户私有素材。
- `references/api.md` 中只使用占位符，例如 `YOUR_API_KEY` 和 `$AGNES_API_KEY`。
- `.gitignore` 已忽略 `.env`、`outputs/`、`downloads/` 和常见媒体生成文件。

## 许可证

MIT
