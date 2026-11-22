# 《小企鹅学煎饼》· 20 秒测试

这是 claymotion 的一次完整跑通记录，不是可独立运行的成片。

包含：

- `film.py` — 4 镜头的合成脚本（7 / 5.5 / 5 / 2.5 秒）
- `sound.json` — 112 BPM 卡通乐队 + 拟音
- `production-log.md` — 导演方案、实际制作记录、Must-pass 判定
- `prompts/` — 每张图的槽位和完整提示词
- `contact.jpg` — 8 帧接触表

## 为什么没有 mp4

为了把包压进豆包 16 MB 的限制，示例不带 7 MB 的成片。成片在原始项目里：

```
pancake/out/pancake.mp4
```

## 怎么复用

1. 按 `SKILL.md` 建一个新的片子文件夹。
2. 参考 `film.py` 的 `load()` / `SHOTS` / `build()` / `render()` 写法。
3. 不要直接运行这个 `film.py`：它的 `SKILL_AT_INIT` 指向原机器的 skill 路径，`src/` 和 `work/` 也不在包里。

这个示例证明的是：Qwen-Image 2.1 + ComfyUI 能出可切的角色表和动作表；WSL 里能跑完 lemo-animi 的 20 秒全流程；声音、切片、锚点、渲染、审片台都能走通。质量上的已知问题写在 `production-log.md` 里。
