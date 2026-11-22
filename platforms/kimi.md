# Kimi

Kimi 支持把 ZIP 或 GitHub 仓库安装为技能，也支持在 Kimi Work 里上传技能包。

## 方式一：ZIP

1. 把 `claymotion/` 压成 ZIP，`SKILL.md` 在根目录。
2. 打开 Kimi Work → 技能 → 上传/安装技能，选择 ZIP。
3. 在对话里用 `/claymotion` 或直接描述任务。

## 方式二：GitHub

把仓库 URL 发给 Kimi：

> 从这个仓库安装 claymotion 技能，并添加到我的 Kimi 工作区：https://github.com/lastfox2000/claymotion

Kimi 会拉取 `SKILL.md` 和配套文件。

## 运行环境

- Kimi 的沙盒如果有 Python + ffmpeg，可以跑完整流程；没有就自动走 pack 模式。
- 云端沙盒不能访问你本机的 ComfyUI。需要 `CLAYMOTION_BACKEND=openai` 指向公网可访问的图片网关，或者生成 pack 后在本机跑 `tools/film.py`。
- 不要把 API key 写进 `SKILL.md` 或 `prompts/`；用环境变量。

## 自检

```bash
python scripts/claymotion.py doctor
python scripts/claymotion.py styles --lang zh
```

如果 `doctor` 报 Python/ffmpeg 缺失，不要继续假装出片；按 `references/hosted-mode.md` 交付制作包。
