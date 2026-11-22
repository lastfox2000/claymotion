---
name: claymotion
description: 用一句话做一支黏土/定格动画短片：写故事和镜头表，生成角色、布景和动作表，在代码里逐格合成，配乐拟音，最后出片。支持本机 ComfyUI（Qwen-Image 2.1）或任意生图工具。
metadata:
  display_name: 黏土定格动画工坊
  display_description: 一句话做一支定格动画短片：故事、镜头表、生图提示词、切片合成、配乐拟音；可用本机 ComfyUI 或平台自带生图。
  icon: ./assets/icon.png
---

# 黏土定格动画工坊

**一句话做一支定格动画短片。** 生图负责“像”，代码负责“动”：不生成视频，而是把角色表、八格动作表切成格子，按一拍二/一拍三排时间，再加运镜、接触阴影、光和调色。

## 何时使用

用户说“做一支定格动画 / 黏土动画 / 定格短片 / claymation / stop-motion”，或者给一句话故事、想要分镜和成片时使用。**不适用于**：把一张现有图片做成动画、剪辑现有视频、纯视频生成（H3/Sora/可灵整段出片）。

## 两种模式

| 模式 | 前提 | 产出 |
|---|---|---|
| **local（完整出片）** | 能跑 Python 3.10+、ffmpeg，能访问 ComfyUI 或图片 API | `out/<name>.mp4`、接触表、审片台 |
| **pack（提示词包）** | 平台不能跑 Python/ffmpeg，或不能访问本机图片服务 | `production-log.md`、镜头表、每张图的完整提示词、`film.py`；由用户在本机渲染 |

先跑 `python scripts/claymotion.py doctor`。如果 Python 或 ffmpeg 缺失，**不要假装能出片**，改用 pack 模式，并在交付里说清楚。

## 输入

一次问齐，默认项排第一：

1. 风格：黏土 / 纸艺 / 铁皮 / 羊毛毡 / 纸板箱 / 木偶 / 钩织 / 布偶（`python scripts/claymotion.py styles` 列出 id、中文名、英文名）。
2. 故事：一句话即可；没有就请用户给，不要替用户编。
3. 时长：20 / 40 / 60 秒，或 20 秒–2 分钟；默认 40 秒。
4. 画幅：横屏 1920×1080 / 竖屏 1080×1920 / 方形 1080×1080。
5. 旁白：默认无；要旁白需要联网（edge-tts，文字会发到微软语音服务）。
6. 片头/片尾：默认无。
7. 预览角色：默认无。
8. 其他要求：角色图、参考片、必须出现的物件。

用户用中文写，就用中文交流；旁白和字幕只做中文或英文。

## 工作流

### 0. 环境

```bash
python scripts/claymotion.py doctor
```

缺依赖时：

```bash
python scripts/setup.py --install          # pip 依赖
python scripts/setup.py --instruments      # 配乐采样，约 1.4GB，可断点续传
python scripts/setup.py --matte            # 可选：BiRefNet 抠图模型，约 0.97GB
```

也可以继续用 lemo-animi 的 `scripts/setup.sh`（macOS/Linux/WSL）。

### 1. 建片

```bash
python scripts/claymotion.py init pancake --style clay --dur 20 --size landscape --name pancake --lang zh
cd pancake
```

### 2. 导演方案

在 `production-log.md` 写：logline、故事骨架（20 秒是一个 gag：setup→surprise→reaction；40 秒是 setup→三次尝试→低谷→转机→payoff）、节拍表、镜头表、分层动作表、生图清单。

规则：
- 每个新事件间隔 1–1.5 秒；20 秒至少 13 个事件。
- 每个镜头要有 `place` 和 `view`；同一地点同一方向只靠改变大小 = zoom cut，不允许。
- 主角在画面短边的占比：wide ≥ 30%，开场/payoff wide ≥ 33%，medium ≥ 40%，medium-close ≥ 60%。
- 20 秒：2–4 镜，约 10–14 张图；40 秒：5–8 镜，约 20–26 张图。

### 3. 建提示词

```bash
python scripts/claymotion.py prompt clay character prompts/char.slots.txt -o prompts/char.txt
python scripts/claymotion.py prompt clay bg prompts/bg_wide.slots.txt -o prompts/bg_wide.txt --size landscape
python scripts/claymotion.py prompt clay sheet8 prompts/sheet_toss.slots.txt -o prompts/sheet_toss.txt
python scripts/claymotion.py prompt clay sheet4 prompts/close_face.slots.txt -o prompts/close_face.txt
```

槽位文件用 `[character]`、`[action]`、`[scene]`、`[shot_size]`、`[margin]`、`[prop]`、`[fx]` 开头；缺槽会报错并列出缺哪个。

### 4. 生图

默认后端是 ComfyUI + Qwen-Image 2.1：

```bash
python scripts/claymotion.py image --prompt prompts/char.txt --out src/char_hero.png
python scripts/claymotion.py image --prompt prompts/sheet_toss.txt --out src/sheet_toss.png --ref src/char_hero.png
```

也可以用：

```bash
# OpenAI 兼容图片 API（豆包/即梦/OpenAI/其他网关）
CLAYMOTION_BACKEND=openai IMAGE_API_BASE=https://... IMAGE_API_KEY=... IMAGE_MODEL=... \
python scripts/claymotion.py image --prompt prompts/char.txt --out src/char_hero.png

# MiniMax H3-Image
CLAYMOTION_BACKEND=h3 python scripts/claymotion.py image --prompt prompts/char.txt --out src/char_hero.png
```

透明资产的要求：角色表、动作表、近景、道具、fx 要透明底；背景不透明、不要出现主角。**先检查再切片**，不要拿一张“看起来还行”的图直接往下做。

### 5. 质检、切片、锚点

```bash
python scripts/claymotion.py check src/sheet_toss.png --n 8 --out work/check_toss.jpg
python scripts/claymotion.py slice src/sheet_toss.png work/cells toss --n 8
python scripts/claymotion.py anchors work/cells --prefix toss --json work/anchors_toss.json --preview work/cells_toss.jpg
```

白底图（生图模型没有 alpha）用：

```bash
python scripts/claymotion.py slice src/sheet_toss.png work/cells toss --n 8 --birefnet
```

切片后如果还有白边：用 `scripts/cut.py` 给每个 cell 出 mask，mask 腐蚀 1px + 0.7px 模糊后写回 alpha。

### 6. 合成

编辑 `tools/film.py` 四处：顶部设置（`SKILL`、`STYLE_ID`、`SIZE`、`NAME`、`HERO_H`）、`load()`、`SHOTS + build()`、`render()`。

```bash
python tools/film.py lint
python tools/film.py board
python tools/film.py still 0 40 80
```

### 7. 声音

```bash
python scripts/claymotion.py sound lint sound.json
python scripts/claymotion.py sound build sound.json
```

每个落地、碰撞、抛接、开合都要有拟音；音乐跟着情绪走；转折前留 0.8–2 秒静音。无旁白时不要写 `vo`，也不要有字幕。

### 8. 出片与自检

```bash
python tools/film.py
sh scripts/contact.sh out/pancake.mp4 out/contact.jpg
python scripts/selfcheck.py out/pancake.mp4 --style clay
python scripts/claymotion.py sound check out/pancake.mp4
```

### 9. 审片

```bash
python scripts/claymotion.py review add out/pancake.mp4 --id film-v1 --lang zh
python scripts/claymotion.py review open --no-browser
```

把打印出的 URL 给用户。等用户写意见或点通过；超时也不丢，意见存在片子文件夹里。用户说“看完了”后运行 `review notes` 读取。

## 图像后端

| 后端 | 环境变量 | 说明 |
|---|---|---|
| `comfy-qwen`（默认） | `COMFYUI_URL`、`QWEN_UNET`、`QWEN_CLIP`、`QWEN_VAE` | 本机/局域网 ComfyUI，Qwen-Image 2.1，原生 RGBA |
| `openai` | `IMAGE_API_BASE`、`IMAGE_API_KEY`、`IMAGE_MODEL`、`IMAGE_SIZE` | 任意 OpenAI 兼容图片 API；透明底看网关是否支持 |
| `h3` | `COMFYUI_URL` | MiniMax H3-Image；没有 alpha 时走白底+抠图 |
| `command` | `IMAGE_CMD` | 任何本地命令，契约见 `references/image-backends.md` |

ComfyUI 的 Qwen 2.1 工作流：`UNETLoader → CLIPLoader → TextEncodeQwenImage21 → KSampler(25 steps, cfg 1, euler/simple) → VAEDecode → SaveImage`，负向用 `ConditioningZeroOut`；参考图走 `TextEncodeQwenImage21.images`。

## 平台差异

- **豆包**：把整个文件夹压成 ZIP，`SKILL.md` 放在 ZIP 根目录；ZIP ≤16MB、单文件 ≤2MB。云端如果访问不到本机 ComfyUI，改用 `openai` 后端或 pack 模式。
- **Grok Bot**：把 `claymotion/` 放到 `~/agent-data/workflows/claymotion/`；或运行 `sh scripts/install_grok.sh`。
- **Kimi**：Kimi Work → 技能 → 上传 ZIP；或把 GitHub 仓库 URL 发给 Kimi 安装。
- **Codex / Claude**：复制到 `~/.agents/skills/claymotion` 或 `~/.claude/skills/claymotion`。

详细说明见 `platforms/`。

## 失败处理

- 生图 429 / 超时：先做不需要这张图的部分，几分钟后重试；不要用占位图交付。
- 生图报错：把原始错误给用户，做不需要图的部分，问怎么继续；不要自己换模型/换后端。
- 切片 FAIL：先看 `work/check_*.jpg`。整张画成场景 → 重新生成；半透明雾 → `--clean`；刻意的边缘裁切 → `--allow-edge`；一格两个角色 → `--group grid`。
- 放不进 16MB：删掉 `styles/*/ref/` 大图和 `examples/*.mp4`，只留 `style.json`、`STYLE.md`、`prompts/`。
- 平台不能跑 Python：转 pack 模式，交付 `production-log.md`、`prompts/`、`film.py` 和每张图的提示词，不要声称已经出片。

## 交付

1. 片名、logline、风格、时长、画幅、镜头数。
2. 图片数量：背景 / 动作表 / 近景 / 道具 / fx，重生成了几张。
3. Must-pass：逐条 pass / fixed / known issue / not checked；声音分两行：测量了什么，以及“没有用耳朵听”。
4. 最不满意的地方，和没做的事（无网络、没听音频等）。
5. 成片路径、审片台 URL。

## 许可

本技能包含 **lemo-animi**（CC BY-NC 4.0，by Lemomo / LemoLab）的脚本、风格包和文档，以及本包新增的适配器与平台说明。**个人非商用免费，商用需要授权**：lemomo.studio@gmail.com。字体为 Source Han Sans 子集（SIL OFL 1.1）。Qwen-Image 2.1 和 MiniMax H3 的权重/服务遵循各自许可。
