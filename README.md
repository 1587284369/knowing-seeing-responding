# 发布包（已脱敏）

本目录是 `08-论文-知道看见回应/` 的可公开发布版本。

## 已替换

| 原文 | 替换为 |
|---|---|
| `<用户目录>\Documents\deepseek-harness\default-workspace` | `<WORKSPACE>` |
| `<盘符>:\Users\<用户名>` | `<USER_HOME>` |
| `<用户名>` / 8.3 短名 | `<USER>` |
| `<Steam 安装目录>\common\NEEDY GIRL OVERDOSE` | `<GAME_DIR>` |

替换只动文本，不动行数；所有统计数字不变（已用 `verify_redaction.py` 校验）。

**作者**：苗志舜（通讯作者）· udongeininaba@foxmail.com
**研究执行与初稿**：DSH（一个运行在 DeepSeek Harness 上的 LLM 智能体）

## 许可

- 代码（`analyze_*.py` 等）：MIT，见 `LICENSE`
- 文字与图：CC BY 4.0，见 `LICENSE-TEXT`
- 游戏截图：版权归发行方，仅研究引用

## 截图

`截图精选/` 有 4 张机制性画面（数值面板、企划列表、JINE、结局卡），均为 960x540 游戏窗口，
不含桌面与账号信息。其余 9,648 张不随包发布，见 `图片-发布黑名单.txt`。

## 未包含

- 截图本体（9,652 张）——体积大，且部分含桌面/账号信息，见 `图片-发布黑名单.txt`。
- 游戏存档 `save-backup/`。
- `09-自述的可靠性/素材/日后谈-2026-10-29.md`：含作者本人的提问原文，需作者确认后再单独发布。

## 校验

- `actions.log` / `brain.log` / `daybook.csv` 行数与原文一致。
- 用 `analyze_v2.py` 指向本目录，统计结果应与 `log-report-v2.md` 完全一致。
