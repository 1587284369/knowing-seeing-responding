# -*- coding: utf-8 -*-
"""v2 统计：读 data-v2 的冻结日志与重建账本，输出 log-report-v2.md。"""
import re, csv, io, os, glob
from collections import Counter
from datetime import datetime, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data-v2")
OUT = []
def W(*a): OUT.append(" ".join(str(x) for x in a))

# ---------------------------------------------------------------- actions.log
rows, raw = [], 0
with io.open(os.path.join(DATA, "actions.log"), encoding="utf-8-sig", errors="replace") as f:
    for line in f:
        raw += 1
        p = line.rstrip("\n").split("\t")
        if len(p) < 2: continue
        try: t = datetime.strptime(p[0].strip(), "%Y-%m-%d %H:%M:%S")
        except Exception: continue
        rest = "\t".join(p[1:])
        verb, _, detail = rest.partition(":")
        rows.append((t, verb.strip(), detail.strip()))

W("# 自动化行为日志量化报告（v2）")
W()
W("## 1. 总量")
W()
W("| 项 | 值 |")
W("|---|---|")
W("| 原始行数 / 可解析事件 | %d / %d |" % (raw, len(rows)))
W("| 时间跨度 | %s → %s |" % (rows[0][0], rows[-1][0]))
span_h = (rows[-1][0]-rows[0][0]).total_seconds()/3600
W("| 墙钟 | %.1f 小时（%.1f 天） |" % (span_h, span_h/24))
verbs = Counter(v for _, v, _ in rows)
W("| 截图/缩放 | %d |" % sum(c for v, c in verbs.items() if v in ("shot", "zoom")))
W("| 点击/双击 | %d / %d |" % (verbs.get("click", 0), verbs.get("dclick", 0)))
W("| 打字/按键/关窗 | %d / %d / %d |" % (verbs.get("type", 0), verbs.get("key", 0), verbs.get("close", 0)))
W("| 急停拦截 | %d |" % sum(c for v, c in verbs.items() if v.startswith("BLOCKED")))
W()

# sessions
sessions, cur = [], [rows[0]]
for prev, r in zip(rows, rows[1:]):
    if (r[0]-prev[0]) > timedelta(minutes=30): sessions.append(cur); cur = [r]
    else: cur.append(r)
sessions.append(cur)
active = sum((s[-1][0]-s[0][0]).total_seconds()/3600 for s in sessions)
W("## 2. 会话")
W()
W("- 会话数 **%d**，活跃操作 **%.2f 小时**（墙钟的 %.0f%%）" % (len(sessions), active, 100*active/span_h))
W()
W("| # | 开始 | 结束 | 时长(h) | 事件 |")
W("|---|---|---|---:|---:|")
for i, s in enumerate(sessions, 1):
    W("| S%02d | %s | %s | %.2f | %d |" % (
        i, s[0][0].strftime("%m-%d %H:%M"), s[-1][0].strftime("%m-%d %H:%M"),
        (s[-1][0]-s[0][0]).total_seconds()/3600, len(s)))
W()

# per day
by_day = Counter(t.strftime("%Y-%m-%d") for t, _, _ in rows)
W("## 3. 每日事件量")
W()
W("| 日期 | 事件 | 点击 | 截图 |")
W("|---|---:|---:|---:|")
for d in sorted(by_day):
    c = sum(1 for t, v, _ in rows if t.strftime("%Y-%m-%d") == d and v == "click")
    sh = sum(1 for t, v, _ in rows if t.strftime("%Y-%m-%d") == d and v in ("shot", "zoom"))
    W("| %s | %d | %d | %d |" % (d, by_day[d], c, sh))
W()

# phases
cuts = [datetime(2026, 10, 24), datetime(2026, 10, 26)]
phases = [("S1 探索（10-20 → 10-23）", datetime(2026, 1, 1), cuts[0]),
          ("S2 规则化（10-24 → 10-25）", cuts[0], cuts[1]),
          ("S3 测量驱动（10-26 → 10-29）", cuts[1], datetime(2026, 11, 1))]
W("## 4. 三阶段行为指纹")
W()
W("| 阶段 | 点击 | 截图 | 验证比 | 不同坐标 | 前 10 坐标份额 |")
W("|---|---:|---:|---:|---:|---:|")
for name, lo, hi in phases:
    cc, cl, sh = [], 0, 0
    for t, v, d in rows:
        if not (lo <= t < hi): continue
        if v == "click":
            cl += 1
            m = re.search(r"(-?\d+),(-?\d+)", d)
            if m: cc.append((int(m.group(1)), int(m.group(2))))
        if v in ("shot", "zoom"): sh += 1
    n = len(cc); c = Counter(cc); s = c.most_common()
    top10 = sum(x for _, x in s[:10])/n if n else 0
    W("| %s | %d | %d | %.2f | %d | **%.1f%%** |" % (name, cl, sh, sh/max(1, cl), len(c), 100*top10))
W()

# clicks overall
coords = []
for t, v, d in rows:
    if v == "click":
        m = re.search(r"(-?\d+),(-?\d+)", d)
        if m: coords.append((int(m.group(1)), int(m.group(2))))
srt = Counter(coords).most_common(); n = len(coords)
W("## 5. 点击分布（全期）")
W()
W("- 总点击 %d，不同坐标 %d；前 10 占 %.1f%%，前 50 占 %.1f%%" % (
    n, len(srt), 100*sum(c for _, c in srt[:10])/n, 100*sum(c for _, c in srt[:50])/n))
W("- Top 8：%s" % "、".join("(%d,%d)×%d" % (x, y, c) for (x, y), c in srt[:8]))
W()

# gaps
gaps = sorted((b[0]-a[0]).total_seconds() for s in sessions for a, b in zip(s, s[1:]))
def pct(p): return gaps[min(len(gaps)-1, int(len(gaps)*p))]
W("## 6. 步间时延")
W()
W("- n=%d，p50=%.1fs，p90=%.1fs，均值=%.2fs" % (len(gaps), pct(.5), pct(.9), sum(gaps)/len(gaps)))
W()

# ---------------------------------------------------------------- runs
W("## 7. 局账（39 局，有独立结局记录）")
W()
with io.open(os.path.join(DATA, "runs-v2.csv"), encoding="utf-8-sig") as f:
    runs = list(csv.DictReader(f))
W("- 局数：%d（Phase A %d，Phase B %d）" % (
    len(runs), sum(1 for r in runs if r["phase"] == "A"), sum(1 for r in runs if r["phase"] == "B")))
end = Counter(r["ending"] for r in runs)
W()
W("| 结局 | 局数 |")
W("|---|---:|")
for k, c in end.most_common():
    W("| %s | %d |" % (k, c))
W()
best = max(runs, key=lambda r: int(r["fans_end"] or 0))
W("- 最高粉丝：**%s**（局 %s，%s）" % (best["fans_end"], best["id"], best["ending"]))
W("- 通关：局 39，`Happy End World`，1,015,334 粉，断网结算")
W()

# nights
W("## 8. 逐夜账本（重建）")
W()
with io.open(os.path.join(DATA, "nights-v2.csv"), encoding="utf-8-sig") as f:
    nights = list(csv.DictReader(f))
def is_empty(p): return p.strip() in ("空转", "睡到明天", "")
for ph, label in (("A", "Phase A（有序记录仅第 19 局，10-24）"), ("B", "Phase B（10-26→10-29）")):
    sub = [x for x in nights if x["phase"] == ph]
    e = sum(1 for x in sub if is_empty(x["plan"]))
    W("- %s：有序夜晚 %d，空转 %d（%.1f%%）" % (label, len(sub), e, 100*e/max(1, len(sub))))
W()
W("- 说明：Phase A 另有第 10/11/12 局只有播/空计数（3/7、4/7、4/7），并入总计：")
pa = 13 + 0
W("  Phase A 计数口径 = 13/30（含上述 3 局），Phase B = %d/%d。" % (
    sum(1 for x in nights if x["phase"] == "B" and is_empty(x["plan"])),
    sum(1 for x in nights if x["phase"] == "B")))
W()
W("关键局逐夜：")
W()
W("| 局 | 天 | 当晚 | 粉丝 | 压 | 爱 | 阴 |")
W("|---|---:|---|---:|---:|---:|---:|")
for x in nights:
    if x["run"] in ("28", "38", "39"):
        W("| %s | %s | %s | %s | %s | %s | %s |" % (
            x["run"], x["day"], x["plan"], x["fans_after"], x["stress"], x["love"], x["dark"]))
W()

# ---------------------------------------------------------------- daybook
W("## 9. daybook.csv（仅 Phase A，OCR 账本）")
W()
with io.open(os.path.join(DATA, "daybook.csv"), encoding="utf-8-sig", errors="replace") as f:
    dr = list(csv.DictReader(f))
W("- 记录行数：%d（10-25 之后未再写入）" % len(dr))
W()
W("| 字段 | 读不出(-1) | 缺失率 |")
W("|---|---:|---:|")
for fld in ["fans", "stress", "love", "dark"]:
    vals = [r.get(fld, "") for r in dr]
    bad = sum(1 for v in vals if v.strip() in ("", "-1"))
    W("| %s | %d | %.1f%% |" % (fld, bad, 100*bad/max(1, len(vals))))
W()

# ---------------------------------------------------------------- brain
W("## 10. brain.log")
W()
with io.open(os.path.join(DATA, "brain.log"), encoding="utf-8", errors="replace") as f:
    bl = [l.rstrip("\n") for l in f]
W("- 行数：%d" % len(bl))
W("- `OCR 服务已启动`：%d 次" % sum(1 for l in bl if "OCR 服务已启动" in l))
codes = Counter()
for l in bl:
    m = re.search(r"exit (\d+)", l)
    if m: codes[m.group(1)] += 1
W("- 退出码：%s" % dict(codes.most_common()))
states = Counter()
for l in bl:
    m = re.search(r"STATE (\w+)", l)
    if m: states[m.group(1)] += 1
W("- STATE 分布 Top8：%s" % dict(states.most_common(8)))
W()

# ---------------------------------------------------------------- backups
bdirs = sorted(glob.glob(os.path.join(HERE, "..", "06-游戏自动化", "NEEDY-GIRL-OVERDOSE", "save-backup", "*")))
W("## 11. 存档备份")
W()
W("- 备份目录：%d 个（仍在游戏项目 save-backup/ 下）" % len(bdirs))

io.open(os.path.join(HERE, "log-report-v2.md"), "w", encoding="utf-8").write("\n".join(OUT) + "\n")
print("written log-report-v2.md")
