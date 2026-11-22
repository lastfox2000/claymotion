# 豆包（Doubao）

豆包开放平台的技能使用 Agent Skills 的 `SKILL.md` 格式，包结构与本技能一致。

## 上传

1. 把 `claymotion/` 目录里的内容压成 ZIP，**让 `SKILL.md` 直接位于 ZIP 根目录**（不要多套一层文件夹）。
2. 打开豆包开放平台 → 技能 → 新建/上传技能，选择 ZIP。
3. 检查展示名、简介、图标是否读取正确。

## 平台限制

| 项 | 上限 |
|---|---|
| ZIP 大小 | 16 MB |
| ZIP 条目数 | 1024 |
| 单个文件解压后 | 2 MB |
| 整包解压 | 16 MB |

本包已经按这个限制裁剪：

- 不含 `styles/*/ref/` 的大参考图（只保留 `ref/texture.jpg`）。
- 字体是 Source Han Sans 常用字子集（约 0.8 MB），不是 8 MB 全量字体。
- 不含示例 mp4；`examples/pancake-20s/` 只有文本、`film.py` 和接触表。

如果还想更小：删掉 `fonts/`（标题/字幕会退回系统字体）、删掉 `examples/`、删掉不用的 `styles/<id>/`。

## 运行环境

`name`、`description`、`metadata` 必须满足豆包规范：`name` 小写字母/数字/连字符，1–64 字符；`description` ≤300 字符；`metadata` 的键和值都是字符串；图标 512×512 PNG/JPG，≤500 KB。

脚本能否运行取决于目标客户端。豆包云端通常**不能访问你本机的 `127.0.0.1:8188`**：

- 有 Python + 能访问远程图片服务：用 `CLAYMOTION_BACKEND=openai`，把 `IMAGE_API_BASE` 指向可访问的网关。
- 没有 Python / 没有图片服务：走 **pack 模式**（`references/hosted-mode.md`），交付故事、镜头表、提示词和 `film.py`，不要声称已出片。

## 自检

上传前在本机：

```bash
python scripts/claymotion.py doctor
python scripts/claymotion.py styles --lang zh
```

再确认 ZIP 根目录有 `SKILL.md`，且没有超过 2 MB 的单文件。
