# Grok Bot

Grok Bot 读取机器人电脑上的技能库：

```
~/agent-data/workflows/<kebab-slug>/SKILL.md
```

## 安装

在 Grok Bot 的对话里：

> Install the claymotion skill from this folder, then confirm it in Settings > Plugins > Yours.

或者直接在机器人电脑上运行：

```bash
git clone https://github.com/lastfox2000/claymotion.git ~/claymotion-src
sh ~/claymotion-src/scripts/install_grok.sh
```

默认安装到 `~/agent-data/workflows/claymotion/`；传一个目录可以改位置：

```bash
sh scripts/install_grok.sh /path/to/workflows/claymotion
```

装完后在 **Settings → Plugins → Yours** 里应能看到 `claymotion`，对话的 `/` 菜单里也能选。

## 使用

```
/claymotion 做一支 20 秒黏土定格动画：小企鹅学做煎饼
```

Grok Bot 有 shell 时可以直接跑：

```bash
python scripts/claymotion.py doctor
python scripts/claymotion.py init pancake --style clay --dur 20 --name pancake --lang zh
```

机器人电脑如果访问不到你的 ComfyUI，用 `CLAYMOTION_BACKEND=openai` 指向可访问的图片网关，或走 pack 模式。

## 更新

```bash
cd ~/claymotion-src && git pull
sh scripts/install_grok.sh
```

## 注意

- Grok Bot 的技能库是账号级的，同一账号下所有 bot 都能看到。
- 技能不会自己安装 Python 包；先 `python scripts/setup.py --install`。
- 不要假设机器人电脑有 ffmpeg；`doctor` 会检查。
