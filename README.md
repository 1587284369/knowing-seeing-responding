# 08 · 论文《知道、看见、回应》

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23769018.svg)](https://doi.org/10.5281/zenodo.23769018)
[![GitHub](https://img.shields.io/badge/GitHub-knowing--seeing--responding-blue)](https://github.com/1587284369/knowing-seeing-responding)

一个 LLM 智能体在《NEEDY STREAMER OVERDOSE》中的 **39 局**（10 天）：前 24 局全败，第 39 局通关 `Happy End World`。

> 与游戏项目（`06-游戏自动化/`）分开存放：这里只放论文、图、复算脚本与派生报告，
> 不修改游戏项目里的任何脚本、存档和日志。
> 统计用的原始日志已**冻结**（v1 在 `data-v1/`，v2 在 `data-v2/`），游戏项目继续被游玩也不会影响论文数字。

## 目录

| 文件 | 说明 |
|---|---|
| `paper.md` | **v2.2 全文**（39 局、五图；含《日后谈》§5–§6 的更正与自述反驳） |
| `paper-v1.md` | v1 全文（24 局、0 通关；作为版本留档） |
| `brief.md` | 一页纸速览 + 评估问卷（v2，给评审 AI / 合作者看） |
| `log-report-v2.md` | v2 量化报告（论文所有数字的来源） |
| `log-report-v1.md` | v1 量化报告 |
| `figs-v2/` | 图 1–5（v2） |
| `figs-v1/` | 图 1–4（v1） |
| `data-v2/` | v2 冻结快照 + 重建账本（`runs-v2.csv`、`nights-v2.csv`） |
| `data-v1/` | v1 冻结快照 |
| `analyze_v2.py` / `make_figs_v2.py` | v2 统计与绘图 |
| `check_runs.py` | 校验正文 39 局表与 `runs-v2.csv` 一致 |
| `redact.py` / `verify_redaction.py` / `make_zip.py` | 生成与校验脱敏发布包 |
| `usage_v2.py` | 从 DSH 会话日志统计 token 用量 |
| `analyze_logs.py` / `make_figs.py` | v1 的脚本（保留以复现 v1） |

## 复现

在本目录执行（Python 3.11；本机 `python` 是商店占位符，用 `py`）：

```powershell
py .\analyze_v2.py        # → log-report-v2.md
py .\make_figs_v2.py      # → figs-v2/fig1-5.png
py .\usage_v2.py          # → token 用量（需 zstandard；无截止时间，数字会随新会话漂移）
py .\check_runs.py        # 校验 paper.md §5.1 的 39 局表与 runs-v2.csv 逐行一致
```

重新生成发布包（脱敏 → 校验 → 打包）：

```powershell
py .\redact.py            # → release/（替换本机路径/用户名）
py .\verify_redaction.py  # 行数、事件数、残留校验
py .\make_zip.py          # → ../08-论文-知道看见回应-发布包-<日期>.zip
```

判定层自测与账本回放（只读游戏项目；回放用冻结账本保证结果一致）：

```powershell
powershell -File ..\06-游戏自动化\NEEDY-GIRL-OVERDOSE\contract.ps1 -SelfTest
powershell -File ..\06-游戏自动化\NEEDY-GIRL-OVERDOSE\contract.ps1 -Replay .\data-v2\daybook.csv -FromTime 00:00 -Until 06:00
```

## 相关课题

- `../09-自述的可靠性/`：从《日后谈》长出的独立课题（自述可信度、免费可得性、纠正分诊三问）。

## 论文的一句话

不是"我们通关了"，而是"**一个能背出全部攻略的智能体，先在全败里证明瓶颈不是知识，
再用一次通关证明瓶颈可以被三条与策略无关的改动挪开——一晚不断播、她说话时不许动、结算前把自己下线**"。

## 状态

- 当前形态：workshop / 短论文 / 预印本级别（v2 比 v1 多了"干预—结果"与一条可检验机制）。
- 若要投正式长文，需补：人类基线、分离 H5（断网 vs 压力）、闸门消融、多模型、跨游戏、开源（见论文 §8.2）。
