# claymotion

**一句话做一支定格动画短片。** 生图负责“像”，代码负责“动”。

这个包把 [lemo-animi](https://github.com/lemomo-ai/lemo-animi) 的定格动画工作流、Qwen-Image 2.1 / ComfyUI 适配器、跨平台 CLI 和平台说明打成一个 **Agent Skills** 包，豆包、Grok Bot、Kimi、Codex、Claude Code 都能加载。

## 它做什么

- 写故事骨架、节拍、镜头表、分层动作表
- 生成角色表、布景、八格动作表、2×2 近景、道具、fx
- 把动作表切成格子，按一拍二/一拍三排时间
- 加运镜、接触阴影、光、调色、字幕
- 用真实乐器采样写配乐，每个接触配拟音
- 出 1920×1080 / 1080×1920 / 1080×1080，24 fps 的 mp4
- 开一个本地审片台，按时间码写意见

## 它不做什么

- 不用视频生成模型（Sora/可灵/H3 视频）整段出片；定格动画是一格一格拍出来的。
- 不把一张现有图片做成动画。
- 不替用户决定故事；没有故事会先问。

## 快速开始

```bash
python scripts/claymotion.py doctor
python scripts/claymotion.py init pancake --style clay --dur 20 --name pancake --lang zh
cd pancake
```

然后按 `SKILL.md` 的 9 步走：导演方案 → 生图 → 切片 → 合成 → 声音 → 出片 → 审片。

最小生图测试：

```bash
python scripts/claymotion.py prompt clay character prompts/char.slots.txt -o prompts/char.txt
python scripts/claymotion.py image --prompt prompts/char.txt --out src/char_hero.png
```

## 图片后端

| 后端 | 用途 |
|---|---|
| `comfy-qwen` | 本机/局域网 ComfyUI + Qwen-Image 2.1，原生 RGBA |
| `openai` | 任意 OpenAI 兼容图片 API（豆包/即梦/OpenAI/网关） |
| `h3` | 本机 ComfyUI + MiniMax H3-Image |
| `command` | 任何本地命令，按契约输出 PNG |

详见 `references/image-backends.md`。

## 目录

```
claymotion/
  SKILL.md                 # Agent Skills 入口
  scripts/
    claymotion.py          # 统一 CLI
    comfy_qwen.py          # ComfyUI + Qwen 2.1
    openai_images.py       # OpenAI 兼容图片 API
    h3_image.py            # MiniMax H3-Image
    setup.py               # 跨平台环境检查/安装
    animi.py kit.py ...    # lemo-animi 核心
  styles/                  # 8 种材质（文本/提示词/纹理）
  references/              # 导演、合成、声音、质量、后端、pack 模式
  platforms/               # 豆包 / Grok / Kimi / Codex-Claude
  fonts/                   # Source Han Sans 常用字子集
  assets/icon.png          # 512×512
  examples/pancake-20s/    # 20 秒测试的 film.py / 提示词 / 接触表
```

## 平台

- **豆包**：ZIP 根目录放 `SKILL.md`，ZIP ≤16 MB、单文件 ≤2 MB。见 `platforms/doubao.md`。
- **Grok Bot**：放到 `~/agent-data/workflows/claymotion/`。见 `platforms/grok.md`。
- **Kimi**：上传 ZIP 或从 GitHub 安装。见 `platforms/kimi.md`。
- **Codex / Claude**：复制/软链到 skills 目录。见 `platforms/codex-claude.md`。

## 无本地运行时

云端 bot 访问不到你的 ComfyUI 时，不要假装出片。按 `references/hosted-mode.md` 交付 **制作包**：故事、镜头表、每张图的提示词、`tools/film.py`，用户在本机跑最后一步。

## 许可

- **lemo-animi**：CC BY-NC 4.0，by Lemomo / LemoLab。个人非商用免费；商用（广告、接单、带变现频道、产品）需要授权：lemomo.studio@gmail.com。
- 本包新增的适配器、CLI、平台说明：MIT。
- 字体：Source Han Sans 子集，SIL OFL 1.1。
- Qwen-Image 2.1 / MiniMax H3：遵循各自模型/服务许可。

保留 `NOTICE` 和 `LICENSE`，不要删除署名。
